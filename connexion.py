from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import urllib.parse
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Encoder le mot de passe pour l'URL
# password_encoded = urllib.parse.quote_plus(DB_PASSWORD)

# Créer la chaîne de connexion PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Créer l'engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Tester la connexion en exécutant une requête simple
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.scalar()
        print(" Connexion réussie !")
        print("Version PostgreSQL :", version)
except Exception as e:
    print(" Erreur de connexion :", e)