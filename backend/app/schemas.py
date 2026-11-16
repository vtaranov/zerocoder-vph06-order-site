from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class ServiceInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=500)
    budget_min: int = Field(ge=0, le=100000000)
    budget_max: int = Field(ge=0, le=100000000)

    @model_validator(mode="after")
    def ordered_budget(self):
        if self.budget_max < self.budget_min:
            raise ValueError("Максимум бюджета меньше минимума")
        if not self.name.strip():
            raise ValueError("Название не может быть пустым")
        self.name = self.name.strip()
        return self

class ServiceOutput(ServiceInput):
    model_config = ConfigDict(from_attributes=True)
    id: int

class MetricsInput(BaseModel):
    time_on_page: int = Field(default=0, ge=0, le=604800)
    visits: int = Field(default=1, ge=1, le=1000000)
    clicks: list[str] = Field(default_factory=list, max_length=100)
    pointer_samples: list[tuple[int, int]] = Field(default_factory=list, max_length=60)
    technical: dict[str, str | int] = Field(default_factory=dict, max_length=10)

    @field_validator("clicks")
    @classmethod
    def click_limits(cls, values):
        if any(len(v) > 80 for v in values): raise ValueError("Слишком длинная метка")
        return values

    @field_validator("technical")
    @classmethod
    def technical_limits(cls, values):
        if any(len(k) > 40 or len(str(v)) > 300 for k,v in values.items()):
            raise ValueError("Слишком длинное техническое значение")
        return values

class ApplicationInput(BaseModel):
    service_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=120)
    contact: str = Field(min_length=5, max_length=200)
    business: str = Field(default="", max_length=300)
    company_size: str = Field(default="", max_length=80)
    role: str = Field(default="", max_length=80)
    task_scope: str = Field(default="", max_length=500)
    deadline: str = Field(default="", max_length=100)
    budget: int = Field(ge=0, le=100000000)
    contact_method: str = Field(min_length=2, max_length=80)
    contact_time: str = Field(default="", max_length=100)
    comment: str = Field(default="", max_length=2000)
    consent: bool
    metrics: MetricsInput = Field(default_factory=MetricsInput)

    @model_validator(mode="after")
    def valid_contact(self):
        if not self.consent: raise ValueError("Нужно согласие на обработку данных")
        self.name = self.name.strip(); self.contact = self.contact.strip()
        if len(self.name) < 2 or len(self.contact) < 5:
            raise ValueError("Заполните имя и контакт")
        return self
