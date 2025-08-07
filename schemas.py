from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ==============================
# 🩺 Schémas pour Médecin
# ==============================

class MedecinBase(BaseModel):
    username: str
    email: EmailStr


class MedecinCreate(MedecinBase):
    password: str  # utilisé lors de la création seulement


class MedecinRead(MedecinBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ==============================
# 🧑‍⚕️ Schémas pour Patient
# ==============================

class PatientBase(BaseModel):
    name: str
    age: int
    sex: str
    glucose: float
    bmi: float
    bloodpressure: float
    pedigree: float


class PatientCreate(PatientBase):
    doctor_id: int  # association obligatoire au médecin


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    glucose: Optional[float] = None
    bmi: Optional[float] = None
    bloodpressure: Optional[float] = None
    pedigree: Optional[float] = None
    prediction_result: Optional[int] = None


class PatientRead(PatientBase):
    id: int
    doctor_id: int
    created_at: datetime
    prediction_result: Optional[int]

    class Config:
        orm_mode = True
