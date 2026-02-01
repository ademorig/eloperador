from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime

class StudyBase(BaseModel):
    request_no: str = Field(..., alias="REQUEST_NO")
    accession: str = Field(..., alias="ACCESSION")
    case_no: Optional[str] = Field(None, alias="CASE_NO")
    xray_code: str = Field(..., alias="XRAY_CODE")
    request_date: Optional[date] = Field(None, alias="REQUEST_DATE")
    request_time: Optional[time] = Field(None, alias="REQUEST_TIME")
    status: str = Field("NEW", alias="STATUS")
    urgent: bool = Field(False, alias="URGENT")
    study_uid: Optional[str] = Field(None, alias="STUDY_UID")
    note: Optional[str] = Field(None, alias="NOTE")

class StudyCreate(StudyBase):
    pass

class Study(StudyBase):
    id: int = Field(..., alias="ID")
    request_timestamp: datetime = Field(default_factory=datetime.now, alias="REQUEST_TIMESTAMP")
    report_status: str = Field("0", alias="REPORT_STATUS")
    study_type: Optional[str] = Field(None, alias="study_type")
    requesting_physician: Optional[str] = Field(None, alias="requesting_physician")
    
    class Config:
        populate_by_name = True
