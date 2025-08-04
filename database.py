# database.py (extrait)
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
import bcrypt
from passlib.context import CryptContext

DATABASE_URL = "postgresql://user:password@host:port/dbname"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Medecin(Base):
    __tablename__ = "medecins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

# Crée les tables dans la base de données
# Lancez cette fonction une seule fois au début du projet
def create_tables():
    print("Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()

# Créez les tables (à faire une seule fois)
# Base.metadata.create_all(bind=engine)

class Patient(Base):
    """
    Modèle de la table 'patients' dans la base de données.
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

    # Relation avec la table Medecin
    doctor = relationship("Medecin")

    # Colonne pour stocker le résultat de la prédiction (nous l'utiliserons plus tard)
    prediction_result = Column(Integer, nullable=True)

# Créez les tables (à lancer une fois ou au démarrage de l'app)
def create_tables():
    print("Création ou mise à jour des tables...")
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()