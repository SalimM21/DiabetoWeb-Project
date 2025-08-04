# DiabetoWeb-Project --> Système d'aide au diagnostic du diabète pour les médecins

# DiabetoWeb

**DiabetoWeb** est une application web sécurisée conçue pour les médecins. Son objectif est de moderniser la gestion des dossiers patients et de soutenir le dépistage précoce du diabète. En combinant un système de gestion de données robuste avec un modèle de Machine Learning, l'application offre un outil d'aide à la décision pour évaluer le risque de diabète chez les patients.

---

### Fonctionnalités Clés

* **Authentification sécurisée** : Les médecins peuvent s'inscrire et se connecter à leur compte pour garantir la confidentialité des données.
* **Gestion des dossiers patients** : Une interface intuitive permet d'ajouter, de consulter, de modifier et de supprimer les informations des patients et leurs données cliniques.
* **Prédiction du diabète** : Un modèle de Machine Learning analyse les données cliniques soumises et fournit une prédiction instantanée du risque de diabète (diabétique/non-diabétique).
* **Tableau de bord récapitulatif** : Un tableau de bord affiche une vue d'ensemble des patients, avec des statistiques clés telles que le pourcentage de patients à risque.

---

### Technologies Utilisées

* **Backend** : FastAPI
* **Frontend** : HTML, CSS, Jinja2
* **Base de données** : PostgreSQL
* **Machine Learning** : scikit-learn, joblib
* **Gestion des mots de passe** : Passlib (bcrypt)
* **Serveur** : Uvicorn

---

### Guide d'installation

Suivez ces étapes pour mettre en place et exécuter le projet localement.

#### Prérequis
Assurez-vous que les logiciels suivants sont installés sur votre machine :
* **Python 3.8+**
* **PostgreSQL**

#### Configuration du projet
1.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/SalimM21/DiabetoWeb-Project.git
    ```
2.  **Naviguer vers le dossier du projet** :
    ```bash
    cd DiabetoWeb
    ```
3.  **Créer et activer un environnement virtuel** :
    ```bash
    python -m venv venv
    # Sur macOS/Linux
    source venv/bin/activate
    # Sur Windows
    venv\Scripts\activate
    ```
4.  **Installer les dépendances Python** :
    ```bash
    pip install fastapi "uvicorn[standard]" jinja2 sqlalchemy psycopg2-binary passlib[bcrypt]
    ```

#### Configuration de la base de données
1.  Créez une base de données PostgreSQL nommée `diabetoweb_db`.
2.  Modifiez le fichier `database.py` pour y ajouter les identifiants de votre base de données :
    ```python
    DATABASE_URL = "postgresql://[votre_utilisateur]:[votre_mot_de_passe]@[votre_hôte]:5432/diabetoweb_db"
    ```
3.  Créez les tables en exécutant votre script de création de tables (si vous en avez un). Sinon, les tables seront créées au premier lancement si votre code utilise `Base.metadata.create_all(bind=engine)`.

#### Démarrage de l'application
1.  Placez votre modèle **`model.pkl`** (et tout autre fichier de modèle, comme `scaler.pkl`) dans un dossier `ml_model/` à la racine du projet.
2.  Lancez l'application avec Uvicorn :
    ```bash
    uvicorn main:app --reload
    ```
3.  Ouvrez votre navigateur et accédez à l'adresse : **http://127.0.0.1:8000**

---

### Structure des fichiers

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

