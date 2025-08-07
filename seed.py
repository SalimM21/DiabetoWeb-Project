from datetime import datetime
from sqlalchemy.orm import Session
import random

# Assurez-vous que ces imports sont corrects selon la structure de votre projet
from database import SessionLocal, engine
from main import Base, Medecin, Patient

# Création des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

def create_doctors(db: Session):
    """Insère 3 médecins de test"""
    doctors_data = [
        {"username": "dr_leroy", "email": "leroy@diabeto.fr", "password": "Medecin123!"},
        {"username": "dr_dupont", "email": "dupont@diabeto.fr", "password": "SecurePass456!"},
        {"username": "dr_martin", "email": "martin@diabeto.fr", "password": "Diabeto2024*"}
    ]
    
    for doc in doctors_data:
        # Vérifie si le médecin existe déjà pour éviter les doublons
        if not db.query(Medecin).filter(Medecin.email == doc["email"]).first():
            new_doctor = Medecin(
                username=doc["username"],
                email=doc["email"],
                created_at=datetime.utcnow()
            )
            # Utilise la méthode set_password pour hacher le mot de passe
            new_doctor.set_password(doc["password"])
            db.add(new_doctor)
    
    db.commit()

def create_patients(db: Session):
    """Insère 20 patients de test avec des données réalistes"""
    
    # Vérifie s'il y a déjà des patients pour ne pas insérer plusieurs fois
    if db.query(Patient).count() > 0:
        print("Les patients existent déjà. Saut de l'insertion.")
        return

    doctors = db.query(Medecin).all()
    if not doctors:
        raise Exception("Aucun médecin trouvé dans la base. Veuillez d'abord insérer les médecins.")
    
    for i in range(1, 21):
        sex = random.choice(['M', 'F'])
        name = f"Patient_{i}"
        age = random.randint(20, 70)
        glucose = round(random.uniform(70, 200), 1)
        bmi = round(random.uniform(18, 40), 1)
        bp = round(random.uniform(60, 120), 1)
        pedigree = round(random.uniform(0.1, 2.5), 3)
        prediction = 1 if (glucose > 140 and bmi > 30) else 0
        
        # Associe aléatoirement à un médecin
        doctor = random.choice(doctors)
        
        new_patient = Patient(
            doctor_id=doctor.id,
            name=name,
            age=age,
            sex=sex,
            glucose=glucose,
            bmi=bmi,
            bloodpressure=bp,
            pedigree=pedigree,
            prediction_result=prediction,
            created_at=datetime.utcnow()
        )
        db.add(new_patient)
        
    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Initialisation du seeder...")
        
        print("Insertion des médecins...")
        create_doctors(db)
        print("✔ 3 médecins insérés ou déjà présents")
        
        print("Insertion des patients...")
        create_patients(db)
        print("✔ Patients insérés ou déjà présents")
        
        # Vérification
        doctor_count = db.query(Medecin).count()
        patient_count = db.query(Patient).count()
        print(f"\nRésumé:")
        print(f"- Médecins: {doctor_count}")
        print(f"- Patients: {patient_count}")
        
    except Exception as e:
        print(f"Erreur: {e}")
        db.rollback()
    finally:
        db.close()