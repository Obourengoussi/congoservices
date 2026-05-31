import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuration sécurisée CongoServices"""

    # 🔐 Clé secrète
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # 🗄️ Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASE_DIR, 'congobrazza.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 📁 Upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

    # 🍪 Cookies
    SESSION_COOKIE_SECURE = True  # True seulement en production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # ⚙️ App
    ITEMS_PER_PAGE = 20
    VIDEOS_PER_PAGE = 10

    # 📂 Catégories
    SERVICE_CATEGORIES = [
        ('plomberie', 'Plomberie'),
        ('electricite', 'Électricité'),
        ('menuiserie', 'Menuiserie'),
        ('peinture', 'Peinture'),
        ('maconnerie', 'Maçonnerie'),
        ('mecanique', 'Mécanique auto'),
        ('informatique', 'Informatique'),
        ('telephone', 'Réparation téléphone'),
        ('coiffure', 'Coiffure'),
        ('cuisine', 'Service traiteur'),
        ('menage', 'Ménage'),
        ('jardinage', 'Jardinage'),
        ('transport', 'Transport'),
        ('autre', 'Autre'),
    ]

    # 🌍 Villes
    CITIES = [
        ('Brazzaville', 'Brazzaville'),
        ('Pointe-Noire', 'Pointe-Noire'),
        ('Dolisie', 'Dolisie'),
        ('Nkayi', 'Nkayi'),
        ('Owando', 'Owando'),
        ('Sangmelima', 'Sangmelima'),
        ('Autre', 'Autre'),
    ]