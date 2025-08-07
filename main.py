import os
from fastapi.staticfiles import StaticFiles
import joblib
from fastapi import FastAPI, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from starlette.middleware.sessions import SessionMiddleware
from database import engine, Base, Medecin, Patient
from typing import Annotated
from dependencies import get_db
import __main__
from pathlib import Path

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="votre-clé-secrète-ultra-securisee")
app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

model = None
scaler = None

@app.get("/", response_class=HTMLResponse, tags=["GET"])
async def home_page(request: Request):
    if "medecin_id" in request.session:
        return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, tags=["GET"])
async def login_page(request: Request):
    if "medecin_id" in request.session:
        return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse, tags=["GET"])
async def register_page(request: Request):
    if "medecin_id" in request.session:
        return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/logout", response_class=HTMLResponse, tags=["GET"])
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/register" , response_class=HTMLResponse, tags=["POST"])
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error_register": "Les mots de passe ne correspondent pas."}
        )

    existing_user = db.query(Medecin).filter(
        (Medecin.username == username) | (Medecin.email == email)
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error_register": "Ce nom d'utilisateur ou cet e-mail est déjà utilisé."}
        )

    # Enregistrement direct du mot de passe sans hachage
    new_medecin = Medecin(username=username, email=email, password=password)
    db.add(new_medecin)
    db.commit()
    db.refresh(new_medecin)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/login" , response_class=HTMLResponse, tags=["POST"])
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    medecin = db.query(Medecin).filter(Medecin.username == username, Medecin.password == password).first()
    if not medecin:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error_login": "Nom d'utilisateur ou mot de passe incorrect."}
        )

    request.session["medecin_id"] = medecin.id
    request.session["username"] = medecin.username
    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout" , response_class=HTMLResponse, tags=["GET"])
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
@app.get("/add", response_class=HTMLResponse)
async def add_patient_page(request: Request, db: Session = Depends(get_db)):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    medecin = db.query(Medecin).filter(Medecin.id == request.session.get("medecin_id")).first()
    return templates.TemplateResponse("add_patient.html", {"request": request, "medecin": medecin})

@app.post("/submit" , response_class=HTMLResponse , tags=["POST"])
async def submit_patient(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    sex: str = Form(...),
    glucose: float = Form(...),
    bmi: float = Form(...),
    bloodpressure: float = Form(...),
    pedigree: float = Form(...),
    db: Session = Depends(get_db)
):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")
    medecin = db.query(Medecin).filter(Medecin.id == doctor_id).first()
    features = [[glucose, bloodpressure, bmi, pedigree]]
    scaled_features = features
    global scaler
    if scaler:
        scaled_features = scaler.transform(features)
    prediction_result = -1
    global model
    if model:
        prediction_result = int(model.predict(scaled_features)[0])
    new_patient = Patient(
        doctor_id=doctor_id,
        name=name,
        age=age,
        sex=sex,
        glucose=glucose,
        bmi=bmi,
        bloodpressure=bloodpressure,
        pedigree=pedigree,
        prediction_result=prediction_result
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

@app.delete("/delete/{patient_id}", response_class=HTMLResponse)
async def delete_patient(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db)
):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")
    patient_to_delete = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.doctor_id == doctor_id
    ).first()

    if patient_to_delete:
        db.delete(patient_to_delete)
        db.commit()

    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/patients", response_class=HTMLResponse , tags=["GET"])
async def patients_dashboard(request: Request, db: Session = Depends(get_db)):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")
    medecin = db.query(Medecin).filter(Medecin.id == doctor_id).first()
    patients = db.query(Patient).filter(Patient.doctor_id == doctor_id).all()
    total_patients = len(patients)
    diabetic_patients_count = db.query(func.count(Patient.id)).filter(
        Patient.doctor_id == doctor_id, 
        Patient.prediction_result == 1
    ).scalar() or 0
    diabetic_percentage = (diabetic_patients_count / total_patients * 100) if total_patients > 0 else 0
    return templates.TemplateResponse(
        "patients.html",
        {
            "request": request,
            "medecin": medecin,
            "patients": patients,
            "total_patients": total_patients,
            "diabetic_patients": diabetic_patients_count,
            "diabetic_percentage": diabetic_percentage
        }
    )

@app.put("/patients/update/{patient_id}", response_class=HTMLResponse)
async def update_patient(
    request: Request,
    patient_id: int,
    name: str = Form(...),
    age: int = Form(...),
    sex: str = Form(...),
    glucose: float = Form(...),
    bmi: float = Form(...),
    db: Session = Depends(get_db)
):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.doctor_id == doctor_id).first()

    if not patient:
        return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

    # Mise à jour des champs
    patient.name = name
    patient.age = age
    patient.sex = sex
    patient.glucose = glucose
    patient.bmi = bmi

    db.commit()
    db.refresh(patient)

    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

@app.on_event("startup")
def load_ml_model():
    global model, scaler
    try:
        model_path = os.path.join(os.path.dirname(__file__), "diabetes_model", "diabetes_risk_prediction_model.pkl")
        scaler_path = os.path.join(os.path.dirname(__file__), "diabetes_model", "scaler.pkl")
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print("Modèle de ML chargé avec succès.")
        else:
            print(f"Erreur : le fichier {model_path} n'a pas été trouvé.")
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            print("Pré-processeur chargé avec succès.")
        else:
            print(f"Avertissement : le pré-processeur {scaler_path} n'a pas été trouvé.")
    except Exception as e:
        print(f"Erreur lors du chargement du modèle ou du pré-processeur : {e}")
    Base.metadata.create_all(bind=engine)
