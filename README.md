# CongoServices 🚀

**Plateforme de mise en relation de services locaux au Congo Brazzaville**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Flask](https://img.shields.io/badge/Flask-3.0-red)

---

## 🏢 À propos du projet

**CongoServices** est une startup digitale congolaise qui révolutionne l'accès aux services locaux au Congo Brazzaville. Notre plateforme connecte les clients avec les meilleurs prestataires de services (plombiers, électriciens, mécaniciens, artisans, etc.) à travers tout le pays.

### 🎯 Slogan
> *"Trouvez les meilleurs prestataires au Congo"*

### 📱 Fonctionnalités principales
- 🔍 Recherche de prestataires par catégorie et ville
- 📹 Module vidéo style TikTok pour la découverte
- 💬 Contact direct via WhatsApp
- 👑 Système Premium et boost de visibilité
- 📊 Dashboard administrateur complet

---

## 🧱 Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.10 + Flask |
| Base de données | SQLite (évolutif vers PostgreSQL) |
| Frontend | HTML5, CSS3, JavaScript (Mobile-first) |
| Framework CSS | Bootstrap 5 |
| Déploiement | Render |
| Serveur | Gunicorn |

---

## 🚀 Installation locale

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de packages)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone https://github.com/votre-username/congobrazza.git
cd congobrazza
```

2. **Créer un environnement virtuel**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration**
```bash
# Modifier config.py si nécessaire
# Par défaut: SECRET_KEY, SQLite, etc.
```

5. **Initialiser la base de données**
```bash
python app.py
# La base de données sera créée automatiquement
```

6. **Lancer le serveur**
```bash
python app.py
```

7. **Accéder à l'application**
```
http://localhost:5000
```

### 🔑 Comptes de test

---

## 📦 Structure du projet

```
congobrazza/
├── app.py                 # Application principale Flask
├── config.py              # Configuration
├── models.py              # Modèles de base de données
├── requirements.txt       # Dépendances Python
├── static/
│   ├── css/
│   │   └── style.css      # Styles CSS
│   ├── js/
│   │   └── main.js        # JavaScript
│   └── uploads/           # Fichiers uploadés
│       ├── profiles/      # Photos de profil
│       ├── videos/        # Vidéos
│       └── thumbnails/    # Miniatures
├── templates/
│   ├── base.html          # Template de base
│   ├── index.html         # Page d'accueil
│   ├── login.html         # Connexion
│   ├── register.html      # Inscription
│   ├── premium.html       # Offres Premium
│   ├── about.html         # À propos
│   ├── contact.html      # Contact
│   ├── cgu.html          # CGU
│   ├── erreurs/          # Pages d'erreur
│   ├── prestataires/     # Pages prestataires
│   ├── videos/           # Pages vidéos
│   └── admin/            # Dashboard admin
└── README.md
```

---

## 🌐 Déploiement sur Render

### 1. Préparation

1. Créez un compte sur [Render](https://render.com)
2. Connectez votre compte GitHub
3. Créez un nouveau Web Service

### 2. Configuration sur Render

| Paramètre | Valeur |
|-----------|--------|
| Environment | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |

### 3. Variables d'environnement

Ajoutez ces variables dans Render:

```
SECRET_KEY=votre_cle_secrete
DATABASE_URL=sqlite:///congobrazza.db
```

### 4. Déploiement automatique

- Push votre code sur GitHub
- Render détectera automatiquement le déploiement
- L'application sera accessible sur `https://votre-app.onrender.com`

---

## 💰 Modèle économique

### Offres Premium

| Offre | Prix | Fonctionnalités |
|-------|------|-----------------|
| Basic | 5 000FCFA/mois | Badge Premium, apparition en haut |
| Pro | 10 000FCFA/mois | + Vidéos sponsorisées, stats avancées |
| Boost | 2 000FCFA/semaine | 7 jours en tête des résultats |

### Revenus

- Abonnements Premium
- Boost de visibilité
- Vidéos sponsorisées
- Commission sur contacts (future feature)

---

## 📈 Stratégie Growth (Croissance)

### 1. Obtenir les 100 premiers utilisateurs

1. **Prospection directe** : Visiter les artisans et professionnels en personne
2. **Partenariats** : Associations avec les chambres de commerce
3. **WhatsApp** : Groupes WhatsApp locaux pour la promotion
4. **Facebook** : Publicités ciblées au Congo

### 2. Gagner 50 000FCFA rapidement

1. **Offre de lancement** : Pack premium à 2 500FCFA
2. **Boost gratuit** : Pour les 50 premiers prestataires
3. **Bouche à oreille** : Encourager le partage WhatsApp

### 3. Version 2 et 3

**Version 2:**
- Application mobile (React Native)
- Paiement Mobile Money intégré
- Système de notation et avis

**Version 3:**
- Expansion vers d'autres pays d'Afrique centrale
- IA pour recommandations personnalisées
- Marketplace pour pièces détachées

---

## 🤝 Contribuer

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📝 License

Ce projet est sous licence MIT.

---

## 📞 Contact

- **Email** : ibaracrepin2@gmail.com
- **WhatsApp** : +242 06 507 21 14
- **Adresse** : Brazzaville, Congo

---

**Fait avec ❤️ au Congo Brazzaville 🇨🇬**
