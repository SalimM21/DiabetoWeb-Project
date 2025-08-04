from fastapi import FastAPI, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base, Medecin, Patient
from starlette.middleware.sessions import SessionMiddleware
from typing import Annotated
from sqlalchemy import func


app = FastAPI()

# Clé secrète pour la session
app.add_middleware(SessionMiddleware, secret_key="votre-clé-secrète")

templates = Jinja2Templates(directory="templates")

# Dépendance pour la session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def create_db_tables():
    """Crée les tables au démarrage de l'application."""
    Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Affiche la page de connexion/inscription."""
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
        return templates.TemplateResponse("login.html", {"request": request, "error_register": "Les mots de passe ne correspondent pas."})

    existing_user = db.query(Medecin).filter(
        (Medecin.username == username) | (Medecin.email == email)
    ).first()
    
    if existing_user:
        return templates.TemplateResponse("login.html", {"request": request, "error_register": "Ce nom d'utilisateur ou cet e-mail est déjà utilisé."})

    new_medecin = Medecin(username=username, email=email)
    new_medecin.set_password(password)
    
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
        return templates.TemplateResponse("login.html", {"request": request, "error_login": "Nom d'utilisateur ou mot de passe incorrect."})

    # Mise en place de la session
    request.session["medecin_id"] = medecin.id
    request.session["username"] = medecin.username

    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout(request: Request):
    """Déconnexion de l'utilisateur."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# Route de test
@app.get("/patients")
async def patients_home(request: Request):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return HTMLResponse("<h1>Bienvenue sur la page des patients, " + request.session.get("username") + "!</h1><a href='/logout'>Déconnexion</a>")

# Ajout de nouvelles routes

# Route pour afficher le formulaire d'ajout de patient
@app.get("/add", response_class=HTMLResponse)
async def add_patient_page(request: Request):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("add_patient.html", {"request": request})


# Route pour soumettre les données du formulaire
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
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")

    # Création du nouvel objet Patient
    new_patient = Patient(
        doctor_id=doctor_id,
        name=name,
        age=age,
        sex=sex,
        glucose=glucose,
        bmi=bmi,
        bloodpressure=bloodpressure,
        pedigree=pedigree
    )

    # Enregistrement dans la base de données
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # La prédiction du modèle sera ajoutée ici dans la prochaine étape
    
    # Redirection vers le tableau de bord des patients
    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

# Route pour supprimer un patient
@app.post("/delete/{patient_id}")
async def delete_patient(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db)
):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")

    # S'assurer que le médecin ne supprime que ses propres patients
    patient_to_delete = db.query(Patient).filter(Patient.id == patient_id, Patient.doctor_id == doctor_id).first()

    if patient_to_delete:
        db.delete(patient_to_delete)
        db.commit()

    return RedirectResponse(url="/patients", status_code=status.HTTP_303_SEE_OTHER)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="votre-clé-secrète")

templates = Jinja2Templates(directory="templates")

# Variables globales pour le modèle et le pré-processeur
model = None
scaler = None

# Dépendance pour la session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
            print(f"Avertissement : le pré-processeur {scaler_path} n'a pas été trouvé. Assurez-vous que votre modèle n'en a pas besoin.")
            
    except Exception as e:
        print(f"Erreur lors du chargement du modèle ou du pré-processeur : {e}")
    Base.metadata.create_all(bind=engine)

# Route pour soumettre les données du formulaire
@app.post("/submit")
async def submit_patient(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    sex: str = Form(...), # Le sexe n'est pas utilisé dans le modèle Pima mais peut l'être dans d'autres
    glucose: float = Form(...),
    bmi: float = Form(...),
    bloodpressure: float = Form(...),
    pedigree: float = Form(...),
    db: Session = Depends(get_db)
):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")

    # Préparation des données pour le modèle de ML
    # Assurez-vous que l'ordre des features correspond à celui de l'entraînement
    features = [glucose, bloodpressure, bmi, pedigree] # L'âge, le sexe, etc. ne sont pas toujours utilisés

    # Si un pré-processeur a été chargé, l'appliquer aux données
    if scaler:
        scaled_features = scaler.transform([features])
    else:
        scaled_features = [features]

    prediction_result = -1 # Valeur par défaut en cas d'erreur
    if model:
        prediction_result = int(model.predict(scaled_features)[0])
        print(f"Prédiction pour {name} : {prediction_result}")
    
    # Création et enregistrement du nouvel objet Patient dans la base de données
    new_patient = Patient(
        doctor_id=doctor_id,
        name=name,
        age=age,
        sex=sex,
        glucose=glucose,
        bmi=bmi,
        bloodpressure=bloodpressure,
        pedigree=pedigree,
        prediction_result=prediction_result # Enregistrement du résultat
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # Ré-affichage du formulaire avec le résultat de la prédiction
    return templates.TemplateResponse(
        "add_patient.html", 
        {"request": request, "result": prediction_result}
    )

# Route du tableau de bord des patients
@app.get("/patients", response_class=HTMLResponse)
async def patients_dashboard(request: Request, db: Session = Depends(get_db)):
    if "medecin_id" not in request.session:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    doctor_id = request.session.get("medecin_id")
    
    # Récupérer la liste des patients du médecin connecté
    patients = db.query(Patient).filter(Patient.doctor_id == doctor_id).all()
    
    # Calcul des statistiques simples
    total_patients = len(patients)
    diabetic_patients = db.query(func.count(Patient.id)).filter(
        Patient.doctor_id == doctor_id, 
        Patient.prediction_result == 1
    ).scalar()
    
    diabetic_percentage = (diabetic_patients / total_patients * 100) if total_patients > 0 else 0

    return templates.TemplateResponse(
        "patients.html",
        {
            "request": request,
            "patients": patients,
            "total_patients": total_patients,
            "diabetic_patients": diabetic_patients,
            "diabetic_percentage": diabetic_percentage
        }
    )