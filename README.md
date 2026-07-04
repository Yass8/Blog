# Mon Blog - Flask & Tailwind CSS

Un blog personnel moderne construit avec Flask et Tailwind CSS.
Il dispose d'un systeme d'authentification, de commentaires, d'une gestion des utilisateurs et d'une interface administrateur pour moderer le contenu.

---

## Fonctionnalites

- Articles : creation, edition, suppression (reservee aux proprietaires).
- Authentification : inscription, connexion, deconnexion.
- Roles : `owner` (proprietaire) et `visiteur` (lecteur connecte).
- Commentaires : ajout, modification, suppression par l'auteur ou l'owner.
- Reponses aux commentaires (un niveau de profondeur).
- Badge "Auteur" pour l'auteur de l'article.
- Profils utilisateurs : consultation, modification, changement de mot de passe, suppression du compte.
- Administration (owner uniquement) : liste des utilisateurs, changement de role, suppression d'utilisateur.
- Design responsive avec Tailwind CSS v4 et polices Google Fonts.
- Base de donnees SQLite via SQLAlchemy, migrations avec Flask-Migrate.
- Protection des routes avec decorateurs personnalises.

---

## Technologies utilisees

- Backend : Flask (Python), Flask-Login, Flask-SQLAlchemy, Flask-WTF, Flask-Migrate
- Base de donnees : SQLite (via SQLAlchemy)
- Frontend : Tailwind CSS v4 (mode CLI avec build optimise), Heroicons (icones SVG)
- Securite : Werkzeug (hashage des mots de passe)
- Gestion des dependances : Python (`requirements.txt`), Node.js (`package.json` pour Tailwind)

---

## Prerequis

- Python 3.8+ (avec `pip` et `venv`)
- Node.js et npm (pour compiler Tailwind)
- Git (optionnel)

---

## Installation et lancement en local

### 1. Cloner le depot
```bash
git clone https://github.com/Yass8/Blog.git
cd Blog
```

### 2. Creer l'environnement virtuel Python
```bash
python -m venv venv
source venv/bin/activate   # Sur Windows : venv\Scripts\activate
```

### 3. Installer les dependances Python
```bash
pip install -r requirements.txt
```

### 4. Installer les dependances Node (Tailwind CSS)
```bash
npm install
```

### 5. Compiler le CSS Tailwind (en mode surveillance)
```bash
npm run watch:css
```
Laissez ce terminal ouvert pendant le developpement.

### 6. Configurer les variables d'environnement
Creez un fichier `.env` a la racine avec :
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=une-cle-secrete-tres-longue-a-changer-en-production
```

### 7. Initialiser la base de donnees
```bash
flask db init    # (si le dossier migrations n'existe pas)
flask db migrate -m "Initialisation"
flask db upgrade
```

### 8. Lancer le serveur Flask
```bash
python run.py
```

Accedez a l'application sur `http://127.0.0.1:5000`.

---

## Creer le premier proprietaire (owner)

1. Inscrivez-vous via la page `/auth/register`.
2. Dans un autre terminal, executez :
```bash
flask shell
```
```python
from app import db
from app.models import User
u = User.query.filter_by(email='votre-email@example.com').first()
u.is_owner = True
db.session.commit()
```
Vous pouvez aussi creer directement l'utilisateur en console avec `is_owner=True`.

---

## Structure du projet

```
mon-blog/
├── app/
│   ├── __init__.py        # Initialisation de l'application et des extensions
│   ├── models.py          # Modeles User, Post, Comment
│   ├── forms.py           # Formulaires WTForms
│   ├── routes.py          # Routes principales (articles, commentaires)
│   ├── auth.py            # Authentification (login, register, logout)
│   ├── profile.py         # Profil utilisateur
│   ├── admin.py           # Administration des utilisateurs
│   └── templates/         # Fichiers HTML (Jinja2)
│       ├── base.html
│       ├── index.html
│       ├── post.html
│       ├── _comment.html
│       ├── ... (autres pages)
│       ├── profile/
│       └── admin/
├── migrations/            # Fichiers de migration Alembic
├── static/
│   └── src/
│       └── input.css      # Source Tailwind
├── config.py              # Configuration Flask
├── run.py                 # Point d'entree de l'application
├── requirements.txt
├── package.json
├── .env                   # Variables d'environnement (non versionne)
└── .gitignore
```

---

## Deploiement rapide (gratuit)

Vous pouvez deployer ce blog facilement sur :

- **Render** (gratuit) : connectez le depot GitHub, indiquez `pip install -r requirements.txt && npm install && npm run build:css` comme commande de build, et `python run.py` comme commande de demarrage.
- **PythonAnywhere** : importez votre code, installez les dependances, compilez le CSS et configurez le fichier WSGI.
- **Railway** / **Fly.io** : alternatives modernes et gratuites.

Pensez a definir les variables d'environnement (`SECRET_KEY`, etc.) sur la plateforme.

---

## Ameliorations futures (roadmap)

- [ ] Mode sombre (dark mode)
- [ ] Pagination des articles et des commentaires
- [ ] Upload d'images pour les articles
- [ ] Systeme de likes sur les articles
- [ ] Notifications par email (nouveau commentaire)
- [ ] Tests unitaires (pytest)
- [ ] Protection CSRF globale avec Flask-WTF

---

## Licence

Ce projet est libre de droits. Vous pouvez l'utiliser, le modifier et le partager a votre guise.

---

## Remerciements

- Tutoriel officiel de Flask
- Miguel Grinberg (Flask Mega-Tutorial)
- La communaute Tailwind CSS

---
