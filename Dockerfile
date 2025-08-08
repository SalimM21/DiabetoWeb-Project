# Étape 1 : Utiliser une image Python légère
FROM python:3.11-slim

# Étape 2 : Définir le dossier de travail dans le conteneur
WORKDIR /app

# Étape 3 : Copier les fichiers de configuration et requirements
COPY requirements.txt .

# Étape 4 : Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : Copier le reste du code dans le conteneur
COPY . .

# Étape 6 : Exposer le port (par défaut FastAPI sur 8000)
EXPOSE 8000

# Étape 7 : Commande pour démarrer l’application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
