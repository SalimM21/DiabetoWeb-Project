import os
import joblib
from fastapi import FastAPI, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from database import engine, Base, Medecin, Patient
from typing import Annotated
from dependencies import get_db
import __main__
from pathlib import Path

app = FastAPI()

# Configuration du middleware de session
app.add_middleware(SessionMiddleware, secret_key="votre-clé-secrète-ultra-securisee")
# templates = Jinja2Templates(directory="templates")

BASE_DIR = Path(__file__).parent
# BASE_DIR = Path(__main__.__file__).parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Contexte pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Variables globales pour le modèle de ML et le pré-processeur
# Ces variables seront chargées au démarrage de l'application
model = None
scaler = None

# --- Fonctions utilitaires ---
# Ces fonctions sont ajoutées pour illustrer comment le modèle Medecin doit gérer les mots de passe
# Dans un vrai projet, ces méthodes seraient définies dans le fichier models.py
def set_password(self, password: str):
    self.password = pwd_context.hash(password)

def verify_password(self, password: str):
    return pwd_context.verify(password, self.password)

# Attacher les méthodes au modèle (nécessaire si elles sont définies ailleurs)
Medecin.set_password = set_password
Medecin.verify_password = verify_password

# --- Routes de l'application ---

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Affiche la page de connexion/inscription."""
    # Redirige vers le tableau de bord si l'utilisateur est déjà connecté
    if "medecin_id" in request.session:
        return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Gère la création d'un nouveau compte médecin."""
    if password != confirm_password:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error_register": "Les mots de passe ne correspondent pas."}
        )
    existing_user = db.query(Medecin).filter((Medecin.username == username) | (Medecin.email == email)).first()
    if existing_user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error_register": "Ce nom d'utilisateur ou cet e-mail est déjà utilisé."}
        )
    
    new_medecin = Medecin(username=username, email=email)
    new_medecin.set_password(password) # Utilise la méthode sécurisée de hachage
    db.add(new_medecin)
    db.commit()
    db.refresh(new_medecin)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Gère la connexion d'un médecin."""
    medecin = db.query(Medecin).filter(Medecin.username == username).first()
    if not medecin or not medecin.verify_password(password):
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error_login": "Nom d'utilisateur ou mot de passe incorrect."}
        )
    
    request.session["medecin_id"] = medecin.id
    request.session["username"] = medecin.username
    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout(request: Request):
    """Déconnexion de l'utilisateur."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/patients", response_class=HTMLResponse)
async def patients_dashboard(request: Request, db: Session = Depends(get_db)):
    """Affiche le tableau de bord des patients pour le médecin connecté."""
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")
    # Récupérer l'objet médecin pour passer les informations au template
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
            "medecin": medecin,  # Ajout de l'objet médecin pour le menu
            "patients": patients,
            "total_patients": total_patients,
            "diabetic_patients": diabetic_patients_count,
            "diabetic_percentage": diabetic_percentage
        }
    )

@app.get("/add", response_class=HTMLResponse)
async def add_patient_page(request: Request, db: Session = Depends(get_db)):
    """Affiche le formulaire d'ajout de patient."""
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    medecin = db.query(Medecin).filter(Medecin.id == request.session.get("medecin_id")).first()
    return templates.TemplateResponse("add_patient.html", {"request": request, "medecin": medecin})

@app.post("/submit")
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
    """Gère la soumission du formulaire, la prédiction et l'enregistrement du patient."""
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")
    medecin = db.query(Medecin).filter(Medecin.id == doctor_id).first()

    # Préparation des données pour le modèle de ML
    features = [[glucose, bloodpressure, bmi, pedigree]]
    scaled_features = features
    
    # Utilisez 'global' pour accéder aux variables globales dans la fonction
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

    # Redirection vers la page des patients après l'ajout
    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/delete/{patient_id}")
async def delete_patient(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Gère la suppression d'un patient."""
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    doctor_id = request.session.get("medecin_id")
    patient_to_delete = db.query(Patient).filter(Patient.id == patient_id, Patient.doctor_id == doctor_id).first()
    
    if patient_to_delete:
        db.delete(patient_to_delete)
        db.commit()
        
    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

@app.on_event("startup")
def load_ml_model():
    """Charge le modèle et le pré-processeur au démarrage de l'application."""
    global model, scaler
    try:
        model_path = os.path.join(os.path.dirname(__file__), "ml_model", "model.pkl")
        scaler_path = os.path.join(os.path.dirname(__file__), "ml_model", "scaler.pkl")

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
    
    # Crée les tables dans la BDD au démarrage si elles n'existent pas
    Base.metadata.create_all(bind=engine)