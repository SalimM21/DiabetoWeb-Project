from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
from passlib.context import CryptContext
import os
import urllib

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Encoder le mot de passe pour l'URL
password_encoded = urllib.parse.quote_plus(DB_PASSWORD)

# Créer la chaîne de connexion PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Créer l'engine SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Medecin(Base):
    """
    Modèle de la table 'medecins'
    """
    __tablename__ = "medecins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password_hash)

class Patient(Base):
    """
    Modèle de la table 'patients'
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("medecins.id"))
    name = Column(String, index=True)
    age = Column(Integer)
    sex = Column(String)
    glucose = Column(Float)
    bmi = Column(Float)
    bloodpressure = Column(Float)
    pedigree = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    prediction_result = Column(Integer, nullable=True)

    doctor = relationship("Medecin")

def create_tables():
    """Crée les tables dans la base de données."""
    print("Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
