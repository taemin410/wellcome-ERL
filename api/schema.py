from pydantic import BaseModel
from datetime import date

class UserResponse(BaseModel):
    id: int
    foreign_name: str
    age: int
    gender: str
    nationality: str
    passport_number: str
    issuance_date: date
    expiration_date: date
    registration_number: str
    validity_period: str
    self_introduction: str

class EducationResponse(BaseModel):
    id: int
    school_name: str
    degree: str
    duration: str
    major: str
    status: str

class ExperienceResponse(BaseModel):
    id: int
    company_name: str
    job_title: str
    duration: str
