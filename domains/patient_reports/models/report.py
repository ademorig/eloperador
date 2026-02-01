from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReportBase(BaseModel):
    study_id: str = Field(..., alias="STUDY_ID")
    content: str = Field(..., alias="CONTENT")
    report_status: str = Field("DRAFT", alias="REPORT_STATUS")
    author_id: str = Field(..., alias="AUTHOR_ID")
    study_type: Optional[str] = Field(None, alias="STUDY_TYPE")
    requesting_physician: Optional[str] = Field(None, alias="REQUESTING_PHYSICIAN")

class PatientReport(BaseModel):
    report_id: str
    study_id: str
    patient_id: str
    patient_name: str
    study_type: str
    results_summary: str
    physician: str
    status: str

    def to_dict(self):
        return self.model_dump()

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: int = Field(..., alias="ID")
    created_at: datetime = Field(default_factory=datetime.now, alias="CREATED_AT")
    signed_at: Optional[datetime] = Field(None, alias="SIGNED_AT")
    authenticated_at: Optional[datetime] = Field(None, alias="AUTHENTICATED_AT")

    class Config:
        populate_by_name = True
