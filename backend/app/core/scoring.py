import re

def rank_application(item, service):
    """Explainable business heuristic, not a probability of a sale."""
    reasons = []
    deadline = item.deadline.lower().strip()
    if any(s in deadline for s in ["не срочно","без спешки","не определ","не сегодня","не завтра"]):
        urgency = 0
    elif any(s in deadline for s in ["сегодня","завтра","срочно"]):
        urgency = 40
    else:
        duration = re.search(r"(?<!\d)(\d+)\s*(дн|день|дней|недел|месяц)", deadline)
        if duration:
            number = int(duration.group(1))
            days = number * (7 if duration.group(2).startswith("недел") else 30 if duration.group(2).startswith("месяц") else 1)
        elif any(word in deadline for word in ["трёх дн","трех дн"]): days = 3
        elif "двух недел" in deadline: days = 14
        elif "недел" in deadline: days = 7
        elif "месяц" in deadline: days = 30
        else: days = None
        urgency = 40 if days is not None and days <= 3 else 25 if days is not None and days <= 7 else 10 if days is not None and days <= 30 else 0
    reasons.append({"criterion":"Срок", "points":urgency, "detail":item.deadline or "Не указан"})
    budget_points = min(30, round(item.budget/max(service.budget_max,1)*30))
    reasons.append({"criterion":"Бюджет относительно верхней цены услуги", "points":budget_points,"detail":f"{item.budget} / {service.budget_max} ₽"})
    size = item.company_size.lower()
    size_points = 15 if any(s in size for s in ["51-250","более 250"]) else 8 if "11-50" in size else 3 if "до 10" in size else 0
    reasons.append({"criterion":"Размер компании", "points":size_points,"detail":item.company_size or "Не указан"})
    role_points = 10 if "руковод" in item.role.lower() else 3 if "сотруд" in item.role.lower() else 0
    reasons.append({"criterion":"Роль", "points":role_points,"detail":item.role or "Не указана"})
    match = re.search(r"(?<!\d)(\d{1,4})(?!\d)",item.task_scope)
    quantity = int(match.group(1)) if match else 0
    volume_points = 10 if quantity >= 10 else 5 if quantity >= 3 else 0
    reasons.append({"criterion":"Объём задачи", "points":volume_points,"detail":item.task_scope or "Не указан"})
    score=sum(r["points"] for r in reasons)
    temperature = "hot" if score >= 65 else "warm" if score >= 35 else "cold"
    return {"score":score,"temperature":temperature,"label":{"hot":"Горячий","warm":"Средний","cold":"Низкий"}[temperature],"reasons":reasons,"personal_manager":score >= 65,"department":"Корпоративный сервис" if size_points >= 8 or quantity >= 3 else "Частный сервис"}
