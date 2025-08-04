# DiabetoWeb-Project --> Système d'aide au diagnostic du diabète pour les médecins

## Introduction
DiabetoWeb est une application web sécurisée conçue pour les médecins, visant à moderniser la gestion des dossiers patients et à soutenir le dépistage précoce du diabète. En combinant un système de gestion de données robuste avec un modèle d'intelligence artificielle, l'application offre un outil d'aide à la décision pour évaluer le risque de diabète chez les patients.

## Fonctionnalités
Authentification sécurisée : Les médecins peuvent s'inscrire et se connecter à leur compte pour garantir la confidentialité des données.

Gestion des dossiers patients : Une interface intuitive permet d'ajouter, de consulter, de modifier et de supprimer les informations des patients et leurs données cliniques.

Prédiction du diabète : Un modèle de Machine Learning analyse les données cliniques soumises et fournit une prédiction instantanée du risque de diabète (diabétique/non-diabétique).

Tableau de bord récapitulatif : Un tableau de bord affiche une vue d'ensemble des patients, avec des statistiques clés telles que le pourcentage de patients à risque.

## Technologies Utilisées
Backend : FastAPI

Frontend : HTML, CSS, Jinja2

Base de données : PostgreSQL

Machine Learning : scikit-learn, joblib

Gestion des mots de passe : Passlib (bcrypt)

Serveur : Uvicorn

## Guide d'installation
Suivez ces étapes pour mettre en place et exécuter le projet localement.

1. Prérequis
Assurez-vous que les logiciels suivants sont installés sur votre machine :

Python 3.8+

PostgreSQL

2. Configuration du projet
Cloner le dépôt :
git clone [URL_DU_DÉPÔT]

Naviguer vers le dossier du projet :
cd DiabetoWeb

Créer et activer un environnement virtuel :
python -m venv venv

Sur macOS/Linux : source venv/bin/activate

Sur Windows : venv\Scripts\activate

Installer les dépendances Python :
pip install -r requirements.txt
(Si vous n'avez pas de fichier requirements.txt, vous pouvez l'installer manuellement : pip install fastapi "uvicorn[standard]" jinja2 sqlalchemy psycopg2-binary passlib[bcrypt])

3. Configuration de la base de données
Créez une base de données PostgreSQL nommée diabetoweb_db.

Modifiez le fichier database.py pour y ajouter les identifiants de votre base de données :
DATABASE_URL = "postgresql://[votre_utilisateur]:[votre_mot_de_passe]@[votre_hôte]:5432/diabetoweb_db"

Créez les tables en exécutant le script :
python database.py

4. Démarrage de l'application
Placez votre modèle model.pkl (et scaler.pkl si utilisé) dans un dossier ml_model/ à la racine du projet.

Lancez l'application avec Uvicorn :
uvicorn main:app --reload

Ouvrez votre navigateur et accédez à l'adresse : http://127.0.0.1:8000

Structure des fichiers

```bash
diabetoweb_app/
├── ml_model/
│   ├── model.pkl
│   └── scaler.pkl 
├── templates/
│   ├── login.html
│   ├── patients.html
│   └── add_patient.html
├── main.py        # Logique de l'API FastAPI et routes
└── database.py    # Configuration de la BDD et modèles SQLAlchemy

```

