from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class PatientBase(BaseModel):
    center_code: str = Field(..., alias="CENTER_CODE")
    mrn: str = Field(..., alias="MRN")
    xn: Optional[str] = Field(None, alias="XN")
    ssn: Optional[str] = Field(None, alias="SSN")
    prefix: Optional[str] = Field(None, alias="PREFIX")
    name: str = Field(..., alias="NAME")
    lastname: str = Field(..., alias="LASTNAME")
    name_eng: Optional[str] = Field(None, alias="NAME_ENG")
    lastname_eng: Optional[str] = Field(None, alias="LASTNAME_ENG")
    sex: Optional[str] = Field(None, alias="SEX")
    birth_date: Optional[date] = Field(None, alias="BIRTH_DATE")
    telephone: Optional[str] = Field(None, alias="TELEPHONE")
    email: Optional[str] = Field(None, alias="EMAIL")
    address: Optional[str] = Field(None, alias="ADDRESS")

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int = Field(..., alias="ID")
    create_date: datetime = Field(default_factory=datetime.now, alias="CREATE_DATE")

    class Config:
        populate_by_name = True
