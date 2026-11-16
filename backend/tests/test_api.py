import os
os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@localhost/test"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"
os.environ["BOOTSTRAP_TOKEN"] = "test-bootstrap-key"
os.environ["ENABLE_DOCS"] = "true"
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import uuid
import jwt
import pytest
from sqlalchemy import create_engine,event,select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.core.database import Base,get_db
from app.core.security import SECRET_KEY,verify_password
from app.models.admin import Admin
from app.models.service import Service
from app.models.metrics import BehaviorMetrics
from app.core.scoring import rank_application
from app.main import app

@pytest.fixture
def client():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    @event.listens_for(engine,"connect")
    def fk(conn,record):conn.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    def database():
        with Session(engine) as session:yield session
    app.dependency_overrides[get_db]=database
    yield TestClient(app),engine
    app.dependency_overrides.clear()
    engine.dispose()

credentials={"username":"admin","password":"test-password-12345"}
service={"name":"Полировка","description":"Блеск","budget_min":15000,"budget_max":45000}
def auth(client):
    c,engine=client
    assert c.post("/api/auth/register",json=credentials,headers={"X-Bootstrap-Token":"test-bootstrap-key"}).status_code==201
    token=c.post("/api/auth/login",json=credentials).json()["access_token"]
    return {"Authorization":"Bearer "+token}

def test_registration_login_tokens(client):
    c,engine=client
    assert c.get("/api/auth/check").json()=={"registration_open":True}
    assert c.post("/api/auth/register",json=credentials).status_code==403
    headers=auth(client)
    assert c.get("/api/auth/check").json()=={"registration_open":False}
    assert c.post("/api/auth/register",json=credentials,headers={"X-Bootstrap-Token":"test-bootstrap-key"}).status_code==409
    assert c.get("/api/auth/me",headers=headers).json()["username"]=="admin"
    assert c.get("/api/admin/applications").status_code==401
    assert c.get("/api/admin/applications",auth=("admin",credentials["password"])).status_code==401
    assert c.post("/api/auth/login",json={**credentials,"password":"wrong-password-123"}).status_code==401
    with Session(engine) as db:
        row=db.get(Admin,1)
        assert row.password_hash!=credentials["password"] and verify_password(credentials["password"],row.password_hash)
    now=datetime.now(timezone.utc)
    for key,claims in [(SECRET_KEY,{"exp":now-timedelta(seconds=1),"iat":now-timedelta(minutes=31)}),("another-secret-with-at-least-32-characters",{"exp":now+timedelta(minutes=1),"iat":now})]:
        token=jwt.encode({"sub":"1","iss":"atelier","aud":"atelier-admin",**claims},key,algorithm="HS256")
        assert c.get("/api/auth/me",headers={"Authorization":"Bearer "+token}).status_code==401
    assert c.get("/docs").status_code==200

def test_services_applications_and_integrity(client):
    c,engine=client;headers=auth(client)
    assert c.post("/api/admin/services",json=service).status_code==401
    assert c.post("/api/admin/services",json={**service,"budget_max":1},headers=headers).status_code==422
    response=c.post("/api/admin/services",json=service,headers=headers);assert response.status_code==201
    sid=response.json()["id"]
    assert c.post("/api/admin/services",json=service,headers=headers).status_code==409
    assert c.put(f"/api/admin/services/{sid}",json={**service,"description":"Обновлено"},headers=headers).json()["description"]=="Обновлено"
    data={"service_id":sid,"name":"Тестовый клиент","contact":"demo@example.com","budget":25000,"contact_method":"Email","consent":True,"metrics":{"time_on_page":35,"visits":2,"clicks":["submit"]}}
    for change in [{"budget":1},{"service_id":999},{"consent":False},{"contact":"    "}]:assert c.post("/api/applications",json={**data,**change}).status_code==422
    assert c.get("/api/admin/applications",headers=headers).json()==[]
    created=c.post("/api/applications",json=data);assert created.status_code==201
    aid=created.json()["id"]
    assert c.get(f"/api/admin/applications/{aid}/metrics",headers=headers).json()["time_on_page"]==35
    assert c.delete(f"/api/admin/services/{sid}",headers=headers).status_code==409
    assert c.delete(f"/api/admin/applications/{aid}",headers=headers).status_code==204
    assert c.get(f"/api/admin/applications/{aid}/metrics",headers=headers).status_code==404
    assert c.delete(f"/api/admin/services/{sid}",headers=headers).status_code==204

def test_sessions_are_independent_idempotent_and_aggregated(client):
    c,engine=client;headers=auth(client)
    tick={"session_id":str(uuid.uuid4()),"sequence":1,"time_on_page":100,"visits":2,"clicks":["service"],"pointer_samples":[[500,300]],"layout":"mobile"}
    assert c.post("/api/behavior-metrics",json=tick).status_code==200
    assert c.post("/api/behavior-metrics",json=tick).status_code==200
    assert c.post("/api/behavior-metrics",json={**tick,"sequence":2,"time_on_page":200}).status_code==200
    assert c.post("/api/behavior-metrics",json={**tick,"sequence":1,"time_on_page":1}).status_code==200
    assert c.post("/api/behavior-metrics",json={**tick,"pointer_samples":[[1001,20]]}).status_code==422
    assert c.get("/api/admin/statistics").status_code==401
    stats=c.get("/api/admin/statistics",headers=headers).json()
    assert stats["periods"]["day"]=={"sessions":1,"average_seconds":200.0,"max_seconds":200}
    assert stats["samples"]==2 and stats["clicks"]==[{"label":"service","count":2}]
    assert sum(p["count"] for p in stats["heatmap"]["mobile"])==2
    with Session(engine) as db:
        assert len(db.scalars(select(BehaviorMetrics)).all())==1
        db.add(BehaviorMetrics(session_id=str(uuid.uuid4()),layout="desktop",time_on_page=100,visits=1,clicks=[],pointer_samples=[],technical={},started_at=datetime.now(timezone.utc)-timedelta(days=2)));db.commit()
    stats=c.get("/api/admin/statistics",headers=headers).json()
    assert stats["periods"]["day"]["sessions"]==1
    assert stats["periods"]["week"]["average_seconds"]==150

def test_ten_independent_priority_examples(client):
    c,engine=client;headers=auth(client)
    sid=c.post("/api/admin/services",json=service,headers=headers).json()["id"]
    fixtures=json.loads((Path(__file__).parent/"fixtures/leads.json").read_text())
    for lead in fixtures:
        payload={k:v for k,v in lead.items() if k!="expected"}
        assert c.post("/api/applications",json={**payload,"service_id":sid,"consent":True}).status_code==201
    results=c.get("/api/admin/applications",headers=headers).json()
    assert [i["priority"]["score"] for i in results]==sorted([i["priority"]["score"] for i in results],reverse=True)
    expected={i["name"]:i["expected"] for i in fixtures}
    for item in results:assert item["priority"]["temperature"]==expected[item["name"]]
    assert [sum(i["priority"]["temperature"]==t for i in results) for t in ["hot","warm","cold"]]==[4,3,3]

@pytest.mark.parametrize("deadline,points",[("Не срочно",0),("В течение 13 дней",10),("В течение двух недель",10),("В течение 3 дней",40),("В течение 7 дней",25),("Когда-нибудь",0)])
def test_deadline_interpretation(deadline,points):
    item=SimpleNamespace(deadline=deadline,budget=15000,company_size="",role="",task_scope="")
    result=rank_application(item,SimpleNamespace(budget_max=45000))
    assert result["reasons"][0]["points"]==points

def test_database_failure_is_actionable(client,monkeypatch):
    from sqlalchemy.exc import OperationalError
    from app.models.service import ServiceCRUD
    def fail(db):raise OperationalError("SELECT",{},Exception("offline"))
    monkeypatch.setattr(ServiceCRUD,"all",fail)
    response=client[0].get("/api/services")
    assert response.status_code==503 and "SELECT" not in response.text
