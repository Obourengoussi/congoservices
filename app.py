# CongoServices - Application Principale
# ============================================
# Plateforme de mise en relation de services locaux au Congo Brazzaville
# Startup: CongoServices - "Trouvez les meilleurs prestataires au Congo"
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import CSRFProtect
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from config import Config
from models import db, User, Prestataire, Video, Comment, Payment, Contact, VideoLike
import os
import uuid

# ============================================
# CONFIGURATION FLASK
# ============================================
app = Flask(__name__)
app.config.from_object(Config)

# 🔐 Protection CSRF (IMPORTANT)
csrf = CSRFProtect(app)

# DB
db.init_app(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter.'

# 🔐 Headers sécurité (anti-hacking navigateur)
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Créer dossier upload
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ============================================
# FONCTIONS UTILITAIRES
# ============================================
@login_manager.user_loader
def load_user(user_id):
    """Charge l'utilisateur pour Flask-Login"""
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_uploaded_file(file, subfolder=''):
    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()

    # 🔐 Empêche fichiers dangereux
    if ext not in app.config['ALLOWED_EXTENSIONS']:
        return None

    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    folder = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, unique_filename)

    # 🔐 limite taille déjà gérée par config
    file.save(filepath)

    return unique_filename


def get_statistics():
    """Récupère les statistiques du site"""
    stats = {
        'total_users': User.query.count(),
        'total_prestataires': Prestataire.query.count(),
        'validated_prestataires': Prestataire.query.filter_by(is_validated=True).count(),
        'total_videos': Video.query.count(),
        'active_videos': Video.query.filter_by(is_active=True).count(),
        'total_views': db.session.query(db.func.sum(Video.views)).scalar() or 0,
        'total_likes': db.session.query(db.func.sum(Video.likes)).scalar() or 0,
    }
    return stats


# ============================================
# ROUTES - PAGE D'ACCUEIL
# ============================================
@app.route('/')
def index():
    """Page d'accueil principale"""
    # Récupérer les prestataires vedettes (premium ou boostés)
    featured_prestataires = Prestataire.query.filter(
        (Prestataire.is_premium == True) | (Prestataire.is_boosted == True)
    ).filter(Prestataire.is_validated == True).order_by(
        Prestataire.views.desc()
    ).limit(6).all()
    
    # Récupérer les dernières vidéos
    latest_videos = Video.query.filter_by(is_active=True).order_by(
        Video.created_at.desc()
    ).limit(10).all()
    
    # Catégories pour le menu
    categories = app.config['SERVICE_CATEGORIES']
    
    return render_template('index.html',
                         featured_prestataires=featured_prestataires,
                         latest_videos=latest_videos,
                         categories=categories)


# ============================================
# ROUTES - AUTHENTIFICATION
# ============================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription utilisateur"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'utilisateur')
        
        # Validation
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà utilisé.', 'error')
            return render_template('register.html')
        
        # Créer l'utilisateur
        user = User(email=email, username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Champs requis.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Compte désactivé.', 'error')
                return render_template('login.html')

            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()

            return redirect(url_for('index'))

        flash('Identifiants invalides.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))


# ============================================
# ROUTES - PRESTATAIRES
# ============================================
@app.route('/prestataires')
def liste_prestataires():
    """Liste des prestataires avec filtres"""
    # Paramètres de filtre
    categorie = request.args.get('categorie')
    ville = request.args.get('ville')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    
    # Construction de la requête
    query = Prestataire.query.filter_by(is_validated=True)
    
    if categorie:
        query = query.filter(Prestataire.categorie == categorie)
    
    if ville:
        query = query.filter(Prestataire.ville == ville)
    
    if search:
        query = query.filter(
            (Prestataire.nom.ilike(f'%{search}%')) |
            (Prestataire.service.ilike(f'%{search}%')) |
            (Prestataire.description.ilike(f'%{search}%'))
        )
    
    # Trier: premium/boostés en premier
    query = query.order_by(Prestataire.is_premium.desc(), Prestataire.is_boosted.desc(), Prestataire.views.desc())
    
    # Pagination
    pagination = query.paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    prestataires = pagination.items
    
    return render_template('prestataires/liste.html',
                         prestataires=prestataires,
                         pagination=pagination,
                         categories=app.config['SERVICE_CATEGORIES'],
                         cities=app.config['CITIES'],
                         selected_categorie=categorie,
                         selected_ville=ville,
                         search=search)


@app.route('/prestataire/<int:id>')
def profil_prestataire(id):
    """Profil d'un prestataire"""
    prestataire = Prestataire.query.get_or_404(id)
    
    # Incrémenter les vues
    if current_user.is_authenticated and current_user.id != prestataire.user_id:
        prestataire.views += 1
        db.session.commit()
    
    # Vidéos du prestataire
    videos = Video.query.filter_by(prestataire_id=prestataire.id, is_active=True).all()
    
    return render_template('prestataires/profil.html',
                         prestataire=prestataire,
                         videos=videos)


@app.route('/prestataire/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_prestataire():
    """Ajouter un nouveau prestataire"""
    if request.method == 'POST':
        # Créer le prestataire
        prestataire = Prestataire(
            user_id=current_user.id,
            nom=request.form.get('nom'),
            prenom=request.form.get('prenom'),
            entreprise=request.form.get('entreprise'),
            service=request.form.get('service'),
            description=request.form.get('description'),
            categorie=request.form.get('categorie'),
            ville=request.form.get('ville'),
            quartier=request.form.get('quartier'),
            adresse=request.form.get('adresse'),
            telephone=request.form.get('telephone'),
            whatsapp=request.form.get('whatsapp'),
            email=request.form.get('email'),
        )
        
        # Photo de profil
        if 'photo' in request.files:
            photo_file = save_uploaded_file(request.files['photo'], 'profiles')
            if photo_file:
                prestataire.photo = photo_file
        
        # Par défaut, non validé (en attente de validation admin)
        prestataire.is_validated = False
        
        db.session.add(prestataire)
        
        # Mettre à jour le rôle de l'utilisateur
        if current_user.role == 'utilisateur':
            current_user.role = 'prestataire'
        
        db.session.commit()
        
        flash('Prestataire ajouté! En attente de validation par un administrateur.', 'success')
        return redirect(url_for('index'))
    
    return render_template('prestataires/ajouter.html',
                         categories=app.config['SERVICE_CATEGORIES'],
                         cities=app.config['CITIES'])


@app.route('/prestataire/<int:id>/contact', methods=['POST'])
@login_required
def contact_prestataire(id):
    """Enregistrer une demande de contact"""
    prestataire = Prestataire.query.get_or_404(id)
    
    contact = Contact(
        user_id=current_user.id,
        prestataire_id=prestataire.id,
        type=request.form.get('type', 'whatsapp')
    )
    
    db.session.add(contact)
    prestataire.contacts += 1
    db.session.commit()
    
    # Retourner le lien WhatsApp
    if request.form.get('type') == 'whatsapp':
        return jsonify({'success': True, 'whatsapp_link': prestataire.get_whatsapp_link()})
    
    return jsonify({'success': True})


# ============================================
# ROUTES - VIDÉOS (TIKTOK STYLE)
# ============================================
@app.route('/videos')
def liste_videos():
    """Liste des vidéos (feed style TikTok)"""
    page = request.args.get('page', 1, type=int)
    categorie = request.args.get('categorie')
    
    query = Video.query.filter_by(is_active=True)
    
    if categorie:
        query = query.filter(Video.categorie == categorie)
    
    # Vidéos sponsorisées en premier, puis par date
    query = query.order_by(Video.is_sponsored.desc(), Video.is_featured.desc(), Video.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=app.config['VIDEOS_PER_PAGE'], error_out=False)
    videos = pagination.items
    
    return render_template('videos/liste.html',
                         videos=videos,
                         pagination=pagination,
                         categories=app.config['SERVICE_CATEGORIES'],
                         selected_categorie=categorie)


@app.route('/video/<int:id>')
def voir_video(id):
    """Voir une vidéo spécifique"""
    video = Video.query.get_or_404(id)
    
    # Incrémenter les vues
    video.views += 1
    db.session.commit()
    
    # Vidéos similaires
    similar_videos = Video.query.filter(
        Video.id != video.id,
        Video.categorie == video.categorie,
        Video.is_active == True
    ).limit(5).all()
    
    return render_template('videos/voir.html',
                         video=video,
                         similar_videos=similar_videos)

@app.route('/video/<int:id>/like', methods=['POST'])
@login_required
def like_video(id):
    """Like sécurisé (anti spam / anti double clic)"""
    
    video = Video.query.get_or_404(id)

    try:
        # Vérifier si déjà liké
        existing_like = VideoLike.query.filter_by(
            user_id=current_user.id,
            video_id=video.id
        ).first()

        if existing_like:
            return jsonify({
                'success': False,
                'error': 'Déjà liké'
            }), 400

        # Ajouter le like
        new_like = VideoLike(
            user_id=current_user.id,
            video_id=video.id
        )
        db.session.add(new_like)

        # Incrémenter les compteurs
        video.likes += 1

        if video.prestataire:
            video.prestataire.likes += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'likes': video.likes
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Erreur serveur'
        }), 500

@app.route('/video/<int:id>/share', methods=['POST'])
@login_required
def share_video(id):
    """Partager une vidéo"""
    video = Video.query.get_or_404(id)
    video.shares += 1
    db.session.commit()
    return jsonify({'success': True, 'shares': video.shares})


@app.route('/video/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_video():
    """Ajouter une nouvelle vidéo"""
    if not current_user.is_prestataire() and not current_user.is_admin():
        flash('Seuls les prestataires peuvent ajouter des vidéos.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Récupérer le prestataire
        prestataire = Prestataire.query.filter_by(user_id=current_user.id).first()
        
        if not prestataire:
            flash('Vous devez d\'ajouter un prestataire.', 'error')
            return redirect(url_for('ajouter_prestataire'))
        
        # Sauvegarder la vidéo
        if 'video' in request.files:
            video_file = save_uploaded_file(request.files['video'], 'videos')
            if not video_file:
                flash('Format de vidéo non autorisé. Utilisez MP4, WebM ou OGG.', 'error')
                return render_template('videos/ajouter.html', categories=app.config['SERVICE_CATEGORIES'])
        
        # Sauvegarder la miniature
        thumbnail_file = None
        if 'thumbnail' in request.files:
            thumbnail_file = save_uploaded_file(request.files['thumbnail'], 'thumbnails')
        
        # Créer la vidéo
        video = Video(
            user_id=current_user.id,
            prestataire_id=prestataire.id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            video_file=video_file,
            thumbnail=thumbnail_file,
            categorie=request.form.get('categorie'),
            tags=request.form.get('tags')
        )
        
        db.session.add(video)
        db.session.commit()
        
        flash('Vidéo ajoutée avec succès!', 'success')
        return redirect(url_for('liste_videos'))
    
    return render_template('videos/ajouter.html',
                         categories=app.config['SERVICE_CATEGORIES'])


# ============================================
# ROUTES - DASHBOARD PRESTATAIRE
# ============================================
@app.route('/prestataire/dashboard')
@login_required
def prestatione_dashboard():
    """Dashboard du prestataire"""
    if not current_user.is_prestataire() and not current_user.is_admin():
        flash('Accès refusé.', 'error')
        return redirect(url_for('index'))
    
    prestataire = Prestataire.query.filter_by(user_id=current_user.id).first()
    
    if not prestataire:
        flash('Vous n\'avez pas de profil prestataire.', 'info')
        return redirect(url_for('ajouter_prestataire'))
    
    # Statistiques
    videos_count = Video.query.filter_by(prestataire_id=prestataire.id).count()
    contacts_count = Contact.query.filter_by(prestataire_id=prestataire.id).count()
    
    return render_template('prestataires/dashboard.html',
                         prestataire=prestataire,
                         videos_count=videos_count,
                         contacts_count=contacts_count)


def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin():
        abort(403)

# ============================================
# ROUTES - ADMIN
# ============================================

@app.route('/admin')
@login_required
def admin_dashboard():
    admin_required()

    stats = get_statistics()

    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    pending_prestataires = Prestataire.query.filter_by(is_validated=False).all()

    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         pending_prestataires=pending_prestataires)


@app.route('/admin/prestataires')
@login_required
def admin_prestataires():
    admin_required()

    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')

    query = Prestataire.query

    if status == 'pending':
        query = query.filter_by(is_validated=False)
    elif status == 'validated':
        query = query.filter_by(is_validated=True)
    elif status == 'premium':
        query = query.filter_by(is_premium=True)

    query = query.order_by(Prestataire.created_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)

    return render_template('admin/prestataires.html',
                         pagination=pagination,
                         status=status)


@app.route('/admin/prestataire/<int:id>/validate', methods=['POST'])
@login_required
def admin_validate_prestataire(id):
    admin_required()

    prestataire = Prestataire.query.get_or_404(id)
    prestataire.is_validated = True
    db.session.commit()

    flash(f'{prestataire.nom} a été validé.', 'success')
    return redirect(url_for('admin_prestataires'))


@app.route('/admin/prestataire/<int:id>/premium', methods=['POST'])
@login_required
def admin_toggle_premium(id):
    admin_required()

    prestataire = Prestataire.query.get_or_404(id)
    action = request.form.get('action')

    if action == 'enable':
        prestataire.is_premium = True
        flash(f'Compte premium activé pour {prestataire.nom}', 'success')
    else:
        prestataire.is_premium = False
        flash(f'Compte premium désactivé pour {prestataire.nom}', 'success')

    db.session.commit()
    return redirect(url_for('admin_prestataires'))


@app.route('/admin/prestataire/<int:id>/boost', methods=['POST'])
@login_required
def admin_boost_prestataire(id):
    admin_required()

    prestataire = Prestataire.query.get_or_404(id)
    days = int(request.form.get('days', 7))

    prestataire.is_boosted = True
    prestataire.boosted_until = datetime.utcnow() + timedelta(days=days)
    db.session.commit()

    flash(f'Visibilité boostée pour {prestataire.nom} pendant {days} jours', 'success')
    return redirect(url_for('admin_prestataires'))


@app.route('/admin/prestataire/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_prestataire(id):
    admin_required()

    prestataire = Prestataire.query.get_or_404(id)
    db.session.delete(prestataire)
    db.session.commit()

    flash('Prestataire supprimé.', 'success')
    return redirect(url_for('admin_prestataires'))


@app.route('/admin/users')
@login_required
def admin_users():
    admin_required()

    page = request.args.get('page', 1, type=int)
    role = request.args.get('role')

    query = User.query

    if role:
        query = query.filter_by(role=role)

    query = query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)

    return render_template('admin/users.html',
                         pagination=pagination,
                         role=role)


@app.route('/admin/user/<int:id>/toggle_active', methods=['POST'])
@login_required
def admin_toggle_user_active(id):
    admin_required()

    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()

    status = 'activé' if user.is_active else 'désactivé'
    flash(f'Utilisateur {status}.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/videos')
@login_required
def admin_videos():
    admin_required()

    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')

    query = Video.query

    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'featured':
        query = query.filter_by(is_featured=True)
    elif status == 'sponsored':
        query = query.filter_by(is_sponsored=True)

    query = query.order_by(Video.created_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)

    return render_template('admin/videos.html',
                         pagination=pagination,
                         status=status)


@app.route('/admin/video/<int:id>/toggle_featured', methods=['POST'])
@login_required
def admin_toggle_video_featured(id):
    admin_required()

    video = Video.query.get_or_404(id)
    video.is_featured = not video.is_featured
    db.session.commit()

    flash('Vidéo mise à jour.', 'success')
    return redirect(url_for('admin_videos'))


@app.route('/admin/video/<int:id>/toggle_sponsored', methods=['POST'])
@login_required
def admin_toggle_video_sponsored(id):
    admin_required()

    video = Video.query.get_or_404(id)
    video.is_sponsored = not video.is_sponsored
    db.session.commit()

    flash('Vidéo mise à jour.', 'success')
    return redirect(url_for('admin_videos'))


@app.route('/admin/video/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_video(id):
    admin_required()

    video = Video.query.get_or_404(id)

    if video.video_file:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video.video_file))
        except:
            pass

    db.session.delete(video)
    db.session.commit()

    flash('Vidéo supprimée.', 'success')
    return redirect(url_for('admin_videos'))


# ============================================
# ROUTES - MONÉTISATION
# ============================================
@app.route('/premium')
def premium():
    """Page d'information Premium"""
    return render_template('premium.html')


@app.route('/payment/create', methods=['POST'])
@login_required
def create_payment():
    """Créer une demande de paiement (simulation Mobile Money)"""
    payment_type = request.form.get('type')  # premium, boost
    amount = int(request.form.get('amount', 5000))
    phone = request.form.get('phone')
    
    # Créer le paiement
    payment = Payment(
        user_id=current_user.id,
        type=payment_type,
        amount=amount,
        phone_number=phone,
        transaction_id=f"PAY-{uuid.uuid4().hex[:12].upper()}",
        status='pending'
    )
    
    db.session.add(payment)
    db.session.commit()
    
    # Simuler le paiement (en production, ce serait via API Mobile Money)
    payment.status = 'completed'
    payment.completed_at = datetime.utcnow()
    
    # Appliquer le bénéfice
    if payment_type == 'premium':
        current_user.is_premium = True
        if current_user.prestataire:
            current_user.prestataire.is_premium = True
    
    db.session.commit()
    
    flash(f'Paiement de {amount}FCFA confirmé!', 'success')
    return redirect(url_for('index'))


# ============================================
# ROUTES - STATIQUES
# ============================================
@app.route('/about')
def about():
    """À propos"""
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Page contact"""
    return render_template('contact.html')


@app.route('/cgu')
def cgu():
    """Conditions générales d'utilisation"""
    return render_template('cgu.html')


# ============================================
# ERREURS
# ============================================
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(413)
def too_large(e):
    return "Fichier trop volumineux (max 100MB)", 413

# ============================================
# CRÉATION DE LA BASE DE DONNÉES
# ============================================
def init_db():
    """Initialise la base de données avec les tables et données par défaut"""
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        
        # Créer l'admin par défaut si inexistant
        if not User.query.filter_by(email='admin@congobrazza.cg').first():
            admin = User(
                email='admin@congobrazza.cg',
                username='admin',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Créer un utilisateur de test
            test_user = User(
                email='test@congobrazza.cg',
                username='testuser',
                role='utilisateur'
            )
            test_user.set_password('test123')
            db.session.add(test_user)
            
            db.session.commit()
            print("✓ Base de données initialisée")
            print("✓ Admin créé: admin@congobrazza.cg / admin123")
            print("✓ Utilisateur test: test@congobrazza.cg / test123")



# ============================================
# POINT D'ENTRÉE
# ============================================
if __name__ == '__main__':
    # Initialiser la base de données
    init_db()
    
    # Lancer le serveur
    app.run(debug=False)

