# CongoServices - Modèles de Base de Données
# ============================================

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

db = SQLAlchemy()

# ============================================
# MODÈLE : UTILISATEUR
# ============================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='utilisateur')
    is_premium = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relations
    prestataire = db.relationship('Prestataire', backref='user', uselist=False, lazy=True)
    videos = db.relationship('Video', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    video_likes = db.relationship('VideoLike', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_prestataire(self):
        return self.role == 'prestataire'

    def __repr__(self):
        return f'<User {self.username}>'


# ============================================
# MODÈLE : PRESTATAIRE
# ============================================
class Prestataire(db.Model):
    __tablename__ = 'prestataires'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100))
    entreprise = db.Column(db.String(200))
    
    service = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(50), nullable=False)
    
    ville = db.Column(db.String(100), nullable=False)
    quartier = db.Column(db.String(100))
    adresse = db.Column(db.Text)
    
    telephone = db.Column(db.String(20), nullable=False)
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    is_validated = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    is_boosted = db.Column(db.Boolean, default=False)
    boosted_until = db.Column(db.DateTime)
    
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    contacts = db.Column(db.Integer, default=0)
    
    photo = db.Column(db.String(255))
    video_presentation = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    videos = db.relationship('Video', backref='prestataire', lazy=True)
    
    def get_full_name(self):
        return f"{self.prenom} {self.nom}" if self.prenom else self.nom

    def get_whatsapp_link(self):
        if self.whatsapp:
            phone = self.whatsapp.replace(' ', '').replace('-', '')
            if not phone.startswith('+'):
                phone = '+242' + phone.lstrip('0')
            return f"https://wa.me/{phone}?text=Bonjour, je vous ai trouvé sur CongoServices"
        return None

    def __repr__(self):
        return f'<Prestataire {self.nom}>'


# ============================================
# MODÈLE : VIDÉO
# ============================================
class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prestataire_id = db.Column(db.Integer, db.ForeignKey('prestataires.id'))
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_file = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255))
    
    categorie = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(500))
    
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_sponsored = db.Column(db.Boolean, default=False)
    
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    comments = db.relationship('Comment', backref='video', lazy=True)
    video_likes = db.relationship('VideoLike', backref='video', lazy=True)

    def get_video_url(self):
        return f"/static/uploads/{self.video_file}"

    def get_thumbnail_url(self):
        if self.thumbnail:
            return f"/static/uploads/{self.thumbnail}"
        return "/static/img/video-placeholder.jpg"

    def __repr__(self):
        return f'<Video {self.title}>'


# ============================================
# MODÈLE : LIKE VIDÉO (NOUVEAU 🔥)
# ============================================
class VideoLike(db.Model):
    __tablename__ = 'video_likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'video_id', name='unique_like'),
    )

    def __repr__(self):
        return f'<Like user={self.user_id} video={self.video_id}>'


# ============================================
# MODÈLE : COMMENTAIRE
# ============================================
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.id}>'


# ============================================
# MODÈLE : PAIEMENT
# ============================================
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), default='XOF')
    
    status = db.Column(db.String(20), default='pending')
    
    transaction_id = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(20))
    
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='payments')

    def __repr__(self):
        return f'<Payment {self.amount}>'


# ============================================
# MODÈLE : CONTACT
# ============================================
class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prestataire_id = db.Column(db.Integer, db.ForeignKey('prestataires.id'), nullable=False)
    
    type = db.Column(db.String(20))
    is_converted = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='contacts')
    prestataire = db.relationship('Prestataire', backref='contact_requests')

    def __repr__(self):
        return f'<Contact {self.id}>'