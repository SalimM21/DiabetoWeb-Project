# Dockerfile

# Utilisez une image de base Python légère
FROM python:3.9-slim-buster

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez les fichiers de dépendances et installez-les
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste de l'application (y compris app.py et votre modèle)
COPY app.py .
COPY note-book.ipynb .
COPY diabetes_risk_prediction_model.pkl .


# Exposez le port sur lequel Streamlit s'exécute par défaut
EXPOSE 8501

# Commande pour exécuter l'application Streamlit lorsque le conteneur démarre
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]



# ----------------------------------------------------------------------------------------
    # Étape 7 : Ajouter des commentaires
# - FROM : Spécifie l'image de base à utiliser.
# - WORKDIR : Définit le répertoire de travail dans l'image Docker.
# - COPY : Copie les fichiers nécessaires dans l'image Docker.
# - RUN : Installe les dépendances nécessaires.
# - EXPOSE : Expose le port 5000 pour l'application Flask.
# - CMD : Définit la commande à exécuter lorsque le conteneur démarre
# - Les commentaires expliquent chaque étape du Dockerfile.
# - Assurez-vous que le fichier random_forest_best_model.pkl est dans le même ré
#   répertoire que le Dockerfile ou ajustez le chemin dans la commande COPY.
# - Vous pouvez remplacer random_forest_best_model.pkl par le nom de votre modèle
#   si vous utilisez un autre modèle.
# - Pour construire l'image Docker, utilisez la commande :
#   docker build -t nom_de_l_image .
# - Pour exécuter le conteneur, utilisez la commande :
#   docker run -p 5000:5000 nom_de_l_image
# - Vous pouvez ensuite accéder à l'API Flask à l'adresse http://localhost:500
# - Assurez-vous que Docker est installé et en cours d'exécution sur votre machine.