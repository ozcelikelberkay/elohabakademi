from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import traceback
from datetime import datetime
from file_manager import FileManager
# Payment handler removed
from sqlalchemy import text
import threading

# Logging konfigürasyonu
def setup_logging():
    """Logging sistemini yapılandır"""
    # Logs klasörünü oluştur
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Log dosya adları
    log_files = {
        'app': 'logs/app.log',
        'error': 'logs/error.log',
        'security': 'logs/security.log',
        # 'payment': 'logs/payment.log',  # Payment log removed
        'file_upload': 'logs/file_upload.log'
    }
    
    # Ana uygulama logger'ı
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    
    # File handler
    app_handler = logging.FileHandler(log_files['app'])
    app_handler.setLevel(logging.INFO)
    app_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app_handler.setFormatter(app_formatter)
    app_logger.addHandler(app_handler)
    
    # Error logger
    error_logger = logging.getLogger('error')
    error_logger.setLevel(logging.ERROR)
    
    error_handler = logging.FileHandler(log_files['error'])
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)
    
    # Security logger
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.WARNING)
    
    security_handler = logging.FileHandler(log_files['security'])
    security_handler.setLevel(logging.WARNING)
    security_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    security_handler.setFormatter(security_formatter)
    security_logger.addHandler(security_handler)
    
    # Payment logger removed
    
    # File upload logger
    file_logger = logging.getLogger('file_upload')
    file_logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(log_files['file_upload'])
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    file_logger.addHandler(file_handler)
    
    # Console handler (development için)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    app_logger.addHandler(console_handler)
    
    return {
        'app': app_logger,
        'error': error_logger,
        'security': security_logger,
        # 'payment': payment_logger,  # Payment logger removed
        'file_upload': file_logger
    }

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
app.config['SECRET_KEY'] = 'elohab2024secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elohab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Override config from environment for Render
secret_key = os.getenv('SECRET_KEY')
if secret_key:
    app.config['SECRET_KEY'] = secret_key

database_url = os.getenv('DATABASE_URL')
if database_url:
    # Render/Heroku style postgres scheme compatibility
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# Logging sistemini kur
loggers = setup_logging()

db = SQLAlchemy(app)
file_manager = FileManager(app)
# Payment handler removed

# Ensure DB tables on first request (for gunicorn on Render)
@app.before_serving
def init_db_on_start():
    try:
        db.create_all()
        ensure_user_columns()
        ensure_question_columns()
    except Exception as e:
        logging.getLogger('error').error(f"DB init error: {e}")

# Veritabanı modelleri
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    package_type = db.Column(db.String(20), default='temel')  # temel, orta, pro
    package_expires = db.Column(db.DateTime)  # Paket bitiş tarihi
    is_active = db.Column(db.Boolean, default=True)  # Test için True, production'da False olacak
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    # Profil alanları
    birth_date = db.Column(db.Date)
    school = db.Column(db.String(120))
    department = db.Column(db.String(120))
    interests = db.Column(db.Text)
    profile_bg = db.Column(db.String(255), default='splash_cockpit.jpg')

def ensure_user_columns():
    """SQLite için hafif şema yükseltici: eksik User kolonlarını ekler."""
    try:
        result = db.session.execute(text("PRAGMA table_info('user')")).all()
        existing_columns = {row[1] for row in result}
        alter_statements = []
        if 'birth_date' not in existing_columns:
            alter_statements.append("ALTER TABLE user ADD COLUMN birth_date DATE")
        if 'school' not in existing_columns:
            alter_statements.append("ALTER TABLE user ADD COLUMN school VARCHAR(120)")
        if 'department' not in existing_columns:
            alter_statements.append("ALTER TABLE user ADD COLUMN department VARCHAR(120)")
        if 'interests' not in existing_columns:
            alter_statements.append("ALTER TABLE user ADD COLUMN interests TEXT")
        if 'profile_bg' not in existing_columns:
            alter_statements.append("ALTER TABLE user ADD COLUMN profile_bg VARCHAR(255) DEFAULT 'splash_cockpit.jpg'")
        for stmt in alter_statements:
            db.session.execute(text(stmt))
        if alter_statements:
            db.session.commit()
    except Exception as e:
        # Logla ama uygulamayı durdurma; ilk çalıştırmada tablo yoksa create_all sonrası tekrar denenecek
        logging.getLogger('error').error(f"ensure_user_columns error: {e}")

def ensure_question_columns():
    """SQLite için hafif şema yükseltici: Question tablo sütunlarını ekler."""
    try:
        result = db.session.execute(text("PRAGMA table_info('question')")).all()
        existing_columns = {row[1] for row in result}
        alter_statements = []
        if 'file_path' not in existing_columns:
            alter_statements.append("ALTER TABLE question ADD COLUMN file_path VARCHAR(200)")
        if 'file_name' not in existing_columns:
            alter_statements.append("ALTER TABLE question ADD COLUMN file_name VARCHAR(200)")
        if 'file_size' not in existing_columns:
            alter_statements.append("ALTER TABLE question ADD COLUMN file_size INTEGER")
        if 'file_type' not in existing_columns:
            alter_statements.append("ALTER TABLE question ADD COLUMN file_type VARCHAR(50)")
        if 'file_url' not in existing_columns:
            alter_statements.append("ALTER TABLE question ADD COLUMN file_url VARCHAR(200)")
        for stmt in alter_statements:
            db.session.execute(text(stmt))
        if alter_statements:
            db.session.commit()
    except Exception as e:
        logging.getLogger('error').error(f"ensure_question_columns error: {e}")

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)  # Ders kodu zorunlu
    grade = db.Column(db.Integer, nullable=False)  # 1-4 sınıf, 0=seçmeli
    semester = db.Column(db.String(20), nullable=False)  # Güz/Bahar/Seçmeli
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=3)
    
    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', backref=db.backref('notes', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(200))
    file_name = db.Column(db.String(200))  # Orijinal dosya adı
    file_size = db.Column(db.Integer)  # Dosya boyutu (bytes)
    file_type = db.Column(db.String(50))  # Dosya türü
    file_url = db.Column(db.String(200))  # URL için dosya adı
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('uploaded_notes', lazy=True))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', backref=db.backref('questions', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Dosya alanları (sınav belgesi)
    file_path = db.Column(db.String(200))
    file_name = db.Column(db.String(200))
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    file_url = db.Column(db.String(200))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(200))
    file_name = db.Column(db.String(200))  # Orijinal dosya adı
    file_size = db.Column(db.Integer)  # Dosya boyutu (bytes)
    file_type = db.Column(db.String(50))  # Dosya türü
    file_url = db.Column(db.String(200))  # URL için dosya adı
    archive_info = db.Column(db.Text)  # Arşiv dosyası bilgileri (JSON)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('uploaded_projects', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Mentorship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200))

class CourseReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_type = db.Column(db.String(50), nullable=False)  # Zorunlu, Seçmeli, Proje, Laboratuvar
    grade = db.Column(db.Integer, nullable=False)  # Sınıf bilgisi
    rating = db.Column(db.Integer, nullable=False)  # 1-5 yıldız
    review_text = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(50), nullable=False)  # Kolay, Orta, Zor
    author_name = db.Column(db.String(100), nullable=False)
    likes = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CourseReview {self.course_name} by {self.author_name}>'

# Global error handlers
@app.errorhandler(404)
def not_found_error(error):
    """404 hata sayfası"""
    loggers['error'].error(f"404 Error: {request.url} - IP: {request.remote_addr}")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 hata sayfası"""
    loggers['error'].error(f"500 Error: {str(error)} - IP: {request.remote_addr} - Traceback: {traceback.format_exc()}")
    db.session.rollback()  # Database session'ı temizle
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    """403 hata sayfası"""
    loggers['security'].warning(f"403 Forbidden: {request.url} - IP: {request.remote_addr} - User: {session.get('username', 'Anonymous')}")
    return render_template('errors/403.html'), 403

@app.errorhandler(413)
def too_large_error(error):
    """413 dosya boyutu hatası"""
    loggers['error'].error(f"413 File Too Large: {request.url} - IP: {request.remote_addr} - User: {session.get('username', 'Anonymous')}")
    flash('Dosya boyutu çok büyük! Maksimum 100MB olmalıdır.', 'error')
    return redirect(request.referrer or url_for('index'))

# Request logging middleware
@app.before_request
def log_request():
    """Her request'i logla"""
    user_id = session.get('user_id', 'Anonymous')
    username = session.get('username', 'Anonymous')
    
    loggers['app'].info(
        f"Request: {request.method} {request.url} - "
        f"IP: {request.remote_addr} - "
        f"User: {username} (ID: {user_id}) - "
        f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
    )

# Response logging middleware
@app.after_request
def log_response(response):
    """Her response'u logla ve ngrok bypass header'larını ekle"""
    user_id = session.get('user_id', 'Anonymous')
    username = session.get('username', 'Anonymous')
    
    # Add comprehensive ngrok bypass headers to all responses
    response.headers['ngrok-skip-browser-warning'] = 'true'
    response.headers['ngrok-skip-browser-warning'] = 'any'
    response.headers['ngrok-skip-browser-warning'] = '1'
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Additional headers to prevent caching of ngrok warning
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # send_file response'ları için size hesaplama
    try:
        if hasattr(response, 'get_data'):
            response_size = len(response.get_data())
        else:
            # send_file response'ları için alternatif size hesaplama
            response_size = "N/A (file response)"
    except RuntimeError:
        # Direct passthrough mode hatası için
        response_size = "N/A (direct passthrough)"
    
    loggers['app'].info(
        f"Response: {response.status_code} - "
        f"IP: {request.remote_addr} - "
        f"User: {username} (ID: {user_id}) - "
        f"Size: {response_size}"
    )
    
    return response

# Ana sayfa
@app.route('/')
def index():
    # Son eklenen içerikleri göster
    recent_notes = Note.query.order_by(Note.created_at.desc()).limit(5).all()
    recent_questions = Question.query.order_by(Question.created_at.desc()).limit(5).all()
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    
    # İstatistikler
    total_users = User.query.count()
    total_notes = Note.query.count()
    total_questions = Question.query.count()
    total_projects = Project.query.count()
    
    return render_template('index.html', 
                         recent_notes=recent_notes,
                         recent_questions=recent_questions,
                         recent_projects=recent_projects,
                         stats={'users': total_users, 'notes': total_notes, 
                                'questions': total_questions, 'projects': total_projects})

# Hakkımızda sayfası
@app.route('/about')
def about():
    return render_template('about.html')

# AGNO ve ÇAN Hesaplayıcı
@app.route('/agno')
def agno_calculator():
    return render_template('agno.html')

# Üye olma sayfası
@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Log registration attempt
            loggers['app'].info(f"Registration attempt: {username} - {email} - IP: {request.remote_addr}")
            
            if password != confirm_password:
                loggers['security'].warning(f"Password mismatch during registration: {username} - IP: {request.remote_addr}")
                flash('Şifreler eşleşmiyor!', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(username=username).first():
                loggers['security'].warning(f"Username already exists during registration: {username} - IP: {request.remote_addr}")
                flash('Bu kullanıcı adı zaten kullanılıyor!', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                loggers['security'].warning(f"Email already exists during registration: {email} - IP: {request.remote_addr}")
                flash('Bu email adresi zaten kullanılıyor!', 'error')
                return render_template('register.html')
            
            # Paket bilgisini al (ödeme akışı kaldırıldı)
            selected_package = 'temel'  # Varsayılan paket
            
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                package_type=selected_package,  # Artık herkes 'temel' paket
                is_active=True  # Ödeme akışı kaldırıldı, kullanıcı hemen aktif
            )
            db.session.add(user)
            db.session.commit()
            
            # Log successful registration
            loggers['app'].info(f"User registered successfully: {username} (ID: {user.id}) - Package: {selected_package}")
            
            # Doğrudan giriş sayfasına yönlendir
            flash('Hesabınız oluşturuldu! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
        
    except Exception as e:
        loggers['error'].error(f"Registration error: {str(e)} - IP: {request.remote_addr} - Traceback: {traceback.format_exc()}")
        flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        return render_template('register.html')

# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            # Log login attempt
            loggers['app'].info(f"Login attempt: {username} - IP: {request.remote_addr}")
            
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                # Ödeme/aktivasyon gereksinimi kaldırıldı
                
                session['user_id'] = user.id
                session['username'] = user.username
                session['is_admin'] = user.is_admin
                
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Log successful login
                loggers['app'].info(f"User logged in successfully: {username} (ID: {user.id}) - IP: {request.remote_addr}")
                loggers['security'].info(f"User session started: {username} (ID: {user.id}) - IP: {request.remote_addr}")
                
                flash('Başarıyla giriş yapıldı!', 'success')
                return redirect(url_for('index'))
            else:
                # Log failed login attempt
                loggers['security'].warning(f"Failed login attempt: {username} - IP: {request.remote_addr}")
                flash('Hatalı kullanıcı adı veya şifre!', 'error')
        
        return render_template('login.html')
        
    except Exception as e:
        loggers['error'].error(f"Login error: {str(e)} - IP: {request.remote_addr} - Traceback: {traceback.format_exc()}")
        flash('Giriş sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        return render_template('login.html')

# Çıkış
@app.route('/logout')
def logout():
    try:
        username = session.get('username', 'Anonymous')
        user_id = session.get('user_id', 'Unknown')
        
        # Log logout
        loggers['app'].info(f"User logged out: {username} (ID: {user_id}) - IP: {request.remote_addr}")
        loggers['security'].info(f"User session ended: {username} (ID: {user_id}) - IP: {request.remote_addr}")
        
        session.clear()
        flash('Çıkış yapıldı!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        loggers['error'].error(f"Logout error: {str(e)} - IP: {request.remote_addr} - Traceback: {traceback.format_exc()}")
        session.clear()  # Force clear session on error
        flash('Çıkış yapıldı!', 'success')
        return redirect(url_for('index'))

# Sınıf seçimi sayfası
@app.route('/grade/<int:grade>')
def grade_page(grade):
    courses = Course.query.filter_by(grade=grade).order_by(Course.semester, Course.name).all()
    return render_template('grade.html', grade=grade, courses=courses)

# Ders notları
@app.route('/notes')
def notes():
    courses = Course.query.all()
    selected_course = request.args.get('course_id', type=int)
    grade = request.args.get('grade', type=int)
    
    # Eğer grade parametresi varsa, o sınıfın Drive linkine yönlendir
    if grade:
        drive_links = {
            1: "https://drive.google.com/drive/folders/1wkaCJrncV_dAyqm-HM28T9FcS2C_PAIC?usp=sharing",
            2: "https://drive.google.com/drive/folders/1UWjl8nOIb1DjDB6RH-TIVchPRONl3jy0?usp=sharing",
            3: "https://drive.google.com/drive/folders/1KmAk5-PRBtimwxvR-CT9MvFNKZlVq9iX?usp=sharing",
            4: "https://drive.google.com/drive/folders/1BNAVJl1G34RCerM4FwuqeLzQMTR-A96b?usp=sharing"
        }
        
        if grade in drive_links:
            return redirect(drive_links[grade])
        else:
            flash('Geçersiz sınıf seçimi!', 'error')
            return redirect(url_for('index'))
    
    # Debug log
    loggers['app'].info(f"Notes page accessed - Total courses: {len(courses)} - Selected course: {selected_course}")
    
    if selected_course:
        notes_list = Note.query.filter_by(course_id=selected_course).all()
        loggers['app'].info(f"Filtered notes by course {selected_course}: {len(notes_list)} notes found")
    else:
        notes_list = Note.query.all()
        loggers['app'].info(f"All notes requested: {len(notes_list)} notes found")
    
    # Her not için ders bilgisini logla
    for note in notes_list:
        course = Course.query.get(note.course_id) if note.course_id else None
        course_name = course.name if course else "No Course"
        loggers['app'].debug(f"Note: {note.title} - Course ID: {note.course_id} - Course Name: {course_name}")
    
    return render_template('notes.html', notes=notes_list, courses=courses, selected_course=selected_course)

# Çıkmış sorular
@app.route('/questions')
def questions():
    courses = Course.query.all()
    selected_course = request.args.get('course_id', type=int)
    grade = request.args.get('grade', type=int)
    
    # Eğer grade parametresi varsa, o sınıfın Drive linkine yönlendir
    if grade:
        drive_links = {
            1: "https://drive.google.com/drive/folders/1a0MhhuSHkf0ObQi5c4jTQCSup6nG69F3?usp=sharing",
            2: "https://drive.google.com/drive/folders/1G2-YBLvrs8pevUBmXdF71ppRow7o45G8?usp=sharing",
            3: "https://drive.google.com/drive/folders/1dNsXzQ5OtFh8_iWMpzVOhBj1r01seRjO?usp=sharing",
            4: "https://drive.google.com/drive/folders/15E3YPxoDxz-Xt-B54Fyo6_SBvYtQ1oKy?usp=sharing"
        }
        
        if grade in drive_links:
            return redirect(drive_links[grade])
        else:
            flash('Geçersiz sınıf seçimi!', 'error')
            return redirect(url_for('index'))
    
    if selected_course:
        questions_list = Question.query.filter_by(course_id=selected_course).order_by(Question.year.desc()).all()
    else:
        questions_list = Question.query.order_by(Question.created_at.desc()).all()
    return render_template('questions.html', questions=questions_list, courses=courses, selected_course=selected_course)

# Soru silme (admin)
@app.route('/questions/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if 'user_id' not in session:
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('login'))
    if not (session.get('is_admin') or session.get('admin')):
        flash('Bu işlemi yapma yetkiniz yok!', 'error')
        return redirect(url_for('questions'))

    q = Question.query.get_or_404(question_id)
    # Dosyayı sil
    if q.file_path:
        try:
            file_path = os.path.join('uploads', 'questions', q.file_path.split('/')[-1])
            if os.path.exists(file_path):
                file_manager.delete_file(file_path)
        except Exception:
            pass

    db.session.delete(q)
    db.session.commit()
    flash('Soru başarıyla silindi!', 'success')
    return redirect(url_for('questions'))

# Soru ekleme (PDF/PNG sınav belgesi ile)
@app.route('/questions/add', methods=['GET', 'POST'])
def add_question():
    if 'user_id' not in session:
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        course_id = int(request.form['course_id'])
        year = int(request.form['year'])
        # Açıklama alanı: soru/cevap yerine tek alan kullanıyoruz
        description = request.form.get('description', '').strip() or request.form.get('question_text', '').strip()
        question_text = description
        answer = ''
        file = request.files.get('file')

        if not all([course_id, year, question_text]):
            flash('Tüm alanları doldurun!', 'error')
            return redirect(url_for('add_question'))

        file_info = None
        if file and file.filename:
            # Sadece PDF/PNG
            allowed = ('.pdf', '.png')
            if not file.filename.lower().endswith(allowed):
                flash('Sadece PDF ve PNG dosyalarına izin verilir.', 'error')
                return redirect(url_for('add_question'))
            file_info, message = file_manager.save_file(file, 'questions', session['user_id'])
            if not file_info:
                flash(message, 'error')
                return redirect(url_for('add_question'))

        q = Question(
            question_text=question_text,
            answer=answer,
            year=year,
            course_id=course_id
        )
        if file_info:
            q.file_path = file_info['file_path']
            q.file_name = file_info['original_name']
            q.file_size = file_info['file_size']
            q.file_type = file_info['saved_name'].split('.')[-1].upper()
            q.file_url = file_info['file_url']

        db.session.add(q)
        db.session.commit()
        flash('Soru başarıyla eklendi!', 'success')
        return redirect(url_for('questions'))

    courses = Course.query.all()
    return render_template('add_question.html', courses=courses)

# Ders notu ekleme
@app.route('/notes/add', methods=['GET', 'POST'])
def add_note():
    try:
        if 'user_id' not in session:
            loggers['security'].warning(f"Unauthorized access attempt to add_note - IP: {request.remote_addr}")
            flash('Lütfen önce giriş yapın!', 'error')
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            course_id = int(request.form['course_id'])
            file = request.files.get('file')
            
            # Log note creation attempt with form data
            loggers['app'].info(f"Note creation attempt: {title} - Course ID: {course_id} - User: {session['user_id']} - IP: {request.remote_addr}")
            
            # Ders bilgisini kontrol et
            course = Course.query.get(course_id)
            if course:
                loggers['app'].info(f"Selected course: {course.name} (ID: {course.id}) - Grade: {course.grade} - Semester: {course.semester}")
            else:
                loggers['app'].warning(f"Course not found for ID: {course_id}")
            
            if not title or not content or not course_id:
                loggers['app'].warning(f"Incomplete note data: {title} - {content} - {course_id} - User: {session['user_id']}")
                flash('Tüm alanları doldurun!', 'error')
                return redirect(url_for('add_note'))
            
            # Dosya yükleme işlemi
            file_info = None
            if file and file.filename:
                loggers['file_upload'].info(f"File upload attempt: {file.filename} - Type: notes - User: {session['user_id']} - IP: {request.remote_addr}")
                
                file_info, message = file_manager.save_file(file, 'notes', session['user_id'])
                if not file_info:
                    loggers['file_upload'].error(f"File upload failed: {file.filename} - Error: {message} - User: {session['user_id']}")
                    flash(message, 'error')
                    return redirect(url_for('add_note'))
                
                loggers['file_upload'].info(f"File uploaded successfully: {file.filename} - Size: {file_info['file_size']} bytes - User: {session['user_id']}")
            
            # Not kaydetme
            note = Note(
                title=title,
                content=content,
                course_id=course_id,
                uploaded_by=session['user_id']
            )
            
            if file_info:
                note.file_path = file_info['file_path']
                note.file_name = file_info['original_name']
                note.file_size = file_info['file_size']
                note.file_type = file_info['saved_name'].split('.')[-1].upper()
                note.file_url = file_info['file_url']
            
            db.session.add(note)
            db.session.commit()
            
            # Log successful note creation with course details
            course = Course.query.get(course_id)
            course_name = course.name if course else "Unknown"
            loggers['app'].info(f"Note created successfully: {title} (ID: {note.id}) - Course: {course_id} ({course_name}) - User: {session['user_id']}")
            
            # Veritabanından notu tekrar çek ve kontrol et
            saved_note = Note.query.get(note.id)
            if saved_note:
                loggers['app'].info(f"Saved note verification - ID: {saved_note.id}, Course ID: {saved_note.course_id}, Course: {saved_note.course.name if saved_note.course else 'None'}")
            else:
                loggers['app'].warning(f"Note not found after save - ID: {note.id}")
            
            flash('Not başarıyla eklendi!', 'success')
            return redirect(url_for('notes'))
        
        courses = Course.query.all()
        return render_template('add_note.html', courses=courses)
        
    except Exception as e:
        loggers['error'].error(f"Add note error: {str(e)} - User: {session.get('user_id', 'Unknown')} - IP: {request.remote_addr} - Traceback: {traceback.format_exc()}")
        flash('Not eklenirken bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('notes'))

# Ders notu düzenleme
@app.route('/notes/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if 'user_id' not in session:
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('login'))
    
    note = Note.query.get_or_404(note_id)
    
    # Sadece not sahibi düzenleyebilir
    if note.uploaded_by != session['user_id'] and not session.get('is_admin'):
        flash('Bu notu düzenleme yetkiniz yok!', 'error')
        return redirect(url_for('notes'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        course_id = int(request.form['course_id'])
        file = request.files.get('file')
        
        if not title or not content or not course_id:
            flash('Tüm alanları doldurun!', 'error')
            return redirect(url_for('edit_note', note_id=note_id))
        
        # Dosya güncelleme
        if file and file.filename:
            # Eski dosyayı sil
            if note.file_path and os.path.exists(note.file_path):
                file_manager.delete_file(note.file_path)
            
            # Yeni dosyayı yükle
            file_info, message = file_manager.save_file(file, 'notes', session['user_id'])
            if not file_info:
                flash(message, 'error')
                return redirect(url_for('edit_note', note_id=note_id))
            
            note.file_path = file_info['file_path']
            note.file_name = file_info['original_name']
            note.file_size = file_info['file_size']
            note.file_type = file_info['saved_name'].split('.')[-1].upper()
            note.file_url = file_info['file_url']
        
        note.title = title
        note.content = content
        note.course_id = course_id
        
        db.session.commit()
        flash('Not başarıyla güncellendi!', 'success')
        return redirect(url_for('notes'))
    
    courses = Course.query.all()
    return render_template('edit_note.html', note=note, courses=courses)

# Ders notu silme
@app.route('/notes/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if 'user_id' not in session:
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('login'))
    
    note = Note.query.get_or_404(note_id)
    
    # Sadece not sahibi veya admin silebilir
    if note.uploaded_by != session['user_id'] and not session.get('is_admin'):
        flash('Bu notu silme yetkiniz yok!', 'error')
        return redirect(url_for('notes'))
    
    # Dosyayı sil
    if note.file_path and os.path.exists(note.file_path):
        file_manager.delete_file(note.file_path)
    
    db.session.delete(note)
    db.session.commit()
    
    flash('Not başarıyla silindi!', 'success')
    return redirect(url_for('notes'))

# Çıkmış sorular sayfası kaldırıldı (route yok)

# Projeler
@app.route('/projects')
def projects():
    grade = request.args.get('grade', type=int)
    
    if grade:
        projects_list = Project.query.filter_by(grade=grade).all()
    else:
        projects_list = Project.query.all()
    
    return render_template('projects.html', projects=projects_list, selected_grade=grade)

# Proje ekleme
@app.route('/projects/add', methods=['GET', 'POST'])
def add_project():
    if 'user_id' not in session:
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        grade = int(request.form['grade'])
        file = request.files.get('file')
        
        if not title or not description or not grade:
            flash('Tüm alanları doldurun!', 'error')
            return redirect(url_for('add_project'))
        
        # Dosya yükleme işlemi
        file_info = None
        archive_info = None
        if file and file.filename:
            file_info, message = file_manager.save_file(file, 'projects', session['user_id'])
            if not file_info:
                flash(message, 'error')
                return redirect(url_for('add_project'))
            
            # Arşiv dosyası bilgilerini çıkar
            if file_info['saved_name'].endswith(('.zip', '.rar')):
                archive_info = file_manager.extract_archive_info(file_info['file_path'])
        
        # Proje kaydetme
        project = Project(
            title=title,
            description=description,
            grade=grade,
            uploaded_by=session['user_id']
        )
        
        if file_info:
            project.file_path = file_info['file_path']
            project.file_name = file_info['original_name']
            project.file_size = file_info['file_size']
            project.file_type = file_info['saved_name'].split('.')[-1].upper()
            project.file_url = file_info['file_url']
            if archive_info:
                import json
                project.archive_info = json.dumps(archive_info)
        
        db.session.add(project)
        db.session.commit()
        
        flash('Proje başarıyla eklendi!', 'success')
        return redirect(url_for('projects'))
    
    return render_template('add_project.html')

# Proje düzenleme
@app.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'user_id' not in session:
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('login'))
    
    project = Project.query.get_or_404(project_id)
    
    # Sadece proje sahibi düzenleyebilir
    if project.uploaded_by != session['user_id'] and not session.get('is_admin'):
        flash('Bu projeyi düzenleme yetkiniz yok!', 'error')
        return redirect(url_for('projects'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        grade = int(request.form['grade'])
        file = request.files.get('file')
        
        if not title or not description or not grade:
            flash('Tüm alanları doldurun!', 'error')
            return redirect(url_for('edit_project', project_id=project_id))
        
        # Dosya güncelleme
        if file and file.filename:
            # Eski dosyayı sil
            if project.file_path and os.path.exists(project.file_path):
                file_manager.delete_file(project.file_path)
            
            # Yeni dosyayı yükle
            file_info, message = file_manager.save_file(file, 'projects', session['user_id'])
            if not file_info:
                flash(message, 'error')
                return redirect(url_for('edit_project', project_id=project_id))
            
            project.file_path = file_info['file_path']
            project.file_name = file_info['original_name']
            project.file_size = file_info['file_size']
            project.file_type = file_info['saved_name'].split('.')[-1].upper()
            project.file_url = file_info['file_url']
            
            # Arşiv dosyası bilgilerini güncelle
            if file_info['saved_name'].endswith(('.zip', '.rar')):
                archive_info = file_manager.extract_archive_info(file_info['file_path'])
                if archive_info:
                    import json
                    project.archive_info = json.dumps(archive_info)
        
        project.title = title
        project.description = description
        project.grade = grade
        
        db.session.commit()
        flash('Proje başarıyla güncellendi!', 'success')
        return redirect(url_for('projects'))
    
    return render_template('edit_project.html', project=project)

# Proje silme
@app.route('/projects/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if 'user_id' not in session:
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('login'))
    
    project = Project.query.get_or_404(project_id)
    
    # Sadece proje sahibi veya admin silebilir
    if project.uploaded_by != session['user_id'] and not session.get('is_admin'):
        flash('Bu projeyi silme yetkiniz yok!', 'error')
        return redirect(url_for('projects'))
    
    # Dosyayı sil
    if project.file_path and os.path.exists(project.file_path):
        file_manager.delete_file(project.file_path)
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Proje başarıyla silindi!', 'success')
    return redirect(url_for('projects'))

# Mentorluk
@app.route('/mentorship')
def mentorship():
    mentors = Mentorship.query.all()
    return render_template('mentorship.html', mentors=mentors)

# Ders Forumu
@app.route('/course_forum')
def course_forum():
    # Mevcut yorumları veritabanından al
    reviews = CourseReview.query.order_by(CourseReview.created_at.desc()).all()
    return render_template('course_forum.html', reviews=reviews)

@app.route('/course_forum/add_review', methods=['POST'])
def add_course_review():
    try:
        # Form verilerini al
        course_name = request.form.get('course_name')
        course_type = request.form.get('course_type')
        grade = request.form.get('grade')
        rating = request.form.get('rating')
        review_text = request.form.get('review_text')
        difficulty_level = request.form.get('difficulty_level')
        author_name = request.form.get('author_name', 'Anonim')
        
        # Validasyon
        if not all([course_name, course_type, grade, rating, review_text, difficulty_level]):
            flash('Tüm alanları doldurunuz!', 'error')
            return redirect(url_for('course_forum'))
        
        # Yeni yorum oluştur
        new_review = CourseReview(
            course_name=course_name,
            course_type=course_type,
            grade=int(grade),
            rating=int(rating),
            review_text=review_text,
            difficulty_level=difficulty_level,
            author_name=author_name
        )
        
        # Veritabanına kaydet
        db.session.add(new_review)
        db.session.commit()
        
        flash('Yorum başarıyla eklendi!', 'success')
        loggers['app'].info(f"New course review added: {course_name} by {author_name}")
        
    except Exception as e:
        db.session.rollback()
        flash('Yorum eklenirken bir hata oluştu!', 'error')
        loggers['error'].error(f"Error adding course review: {str(e)}")
    
    return redirect(url_for('course_forum'))

@app.route('/course_forum/update_like', methods=['POST'])
def update_course_review_like():
    """Ders yorumu beğeni sayısını güncelle"""
    try:
        data = request.get_json()
        review_id = data.get('review_id')
        is_liked = data.get('liked')
        
        review = CourseReview.query.get(review_id)
        if review:
            if is_liked:
                review.likes += 1
            else:
                review.likes = max(0, review.likes - 1)
            
            db.session.commit()
            return jsonify({'success': True, 'likes': review.likes})
        else:
            return jsonify({'success': False, 'error': 'Review not found'}), 404
            
    except Exception as e:
        db.session.rollback()
        loggers['error'].error(f"Error updating like: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/course_forum/add_comment', methods=['POST'])
def add_course_review_comment():
    """Ders yorumuna yorum ekle"""
    try:
        data = request.get_json()
        review_id = data.get('review_id')
        comment_text = data.get('comment_text')
        author_name = data.get('author_name', 'Anonim')
        
        if not comment_text:
            return jsonify({'success': False, 'error': 'Comment text is required'}), 400
        
        review = CourseReview.query.get(review_id)
        if review:
            review.comments_count += 1
            db.session.commit()
            
            # Burada ayrı bir Comment modeli de eklenebilir
            return jsonify({
                'success': True, 
                'comment_count': review.comments_count,
                'comment': {
                    'text': comment_text,
                    'author': author_name,
                    'date': datetime.now().strftime('%d.%m.%Y')
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Review not found'}), 404
            
    except Exception as e:
        db.session.rollback()
        loggers['error'].error(f"Error adding comment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/course_forum/add_sample_data')
def add_sample_course_reviews():
    """Test için örnek ders yorumları ekle (sadece bir kez)"""
    try:
        # Eğer zaten örnek veriler varsa ekleme
        existing_reviews = CourseReview.query.filter(
            CourseReview.course_name.in_([
                "Veri Yapıları ve Algoritmalar",
                "Yapay Zeka ve Makine Öğrenmesi",
                "Web Geliştirme ve Tasarım",
                "Siber Güvenlik",
                "Mobil Uygulama Geliştirme",
                "Veritabanı Sistemleri",
                "Mikroişlemci Projesi",
                "Elektronik Laboratuvarı"
            ])
        ).count()
        
        if existing_reviews > 0:
            flash('Örnek veriler zaten mevcut!', 'info')
            return redirect(url_for('course_forum'))
        
        # Örnek yorumlar
        sample_reviews = [
            CourseReview(
                course_name="Veri Yapıları ve Algoritmalar",
                course_type="Seçmeli Ders",
                grade=2,
                rating=5,
                review_text="Bu ders kesinlikle alınmalı! Algoritma düşünme becerisini geliştiriyor. Hocası çok iyi anlatıyor ve projeler gerçek hayat problemlerini çözüyor. İş mülakatlarında çok faydalı oluyor.",
                difficulty_level="Orta",
                author_name="Ahmet Yılmaz",
                likes=15,
                comments_count=8
            ),
            CourseReview(
                course_name="Yapay Zeka ve Makine Öğrenmesi",
                course_type="Seçmeli Ders",
                grade=3,
                rating=5,
                review_text="Geleceğin teknolojisi! Hocası dünya çapında araştırmacı. TensorFlow ve PyTorch ile pratik yapıyoruz. Final projesi olarak kendi AI modelimizi geliştiriyoruz. Kesinlikle tavsiye ederim.",
                difficulty_level="Zor",
                author_name="Zeynep Kaya",
                likes=23,
                comments_count=12
            ),
            CourseReview(
                course_name="Web Geliştirme ve Tasarım",
                course_type="Seçmeli Ders",
                grade=2,
                rating=4,
                review_text="Frontend ve backend'i birlikte öğreniyoruz. React, Node.js, MongoDB ile full-stack projeler geliştiriyoruz. Portfolio oluşturmak için mükemmel bir ders. Hocası genç ve dinamik.",
                difficulty_level="Orta",
                author_name="Mehmet Demir",
                likes=18,
                comments_count=6
            ),
            CourseReview(
                course_name="Siber Güvenlik",
                course_type="Seçmeli Ders",
                grade=4,
                rating=5,
                review_text="Çok güncel ve önemli bir alan. Penetrasyon testleri, kriptografi, ağ güvenliği gibi konuları pratik olarak öğreniyoruz. CTF yarışmalarına katılıyoruz. Kariyer için çok değerli.",
                difficulty_level="Zor",
                author_name="Elif Özkan",
                likes=21,
                comments_count=9
            ),
            CourseReview(
                course_name="Mobil Uygulama Geliştirme",
                course_type="Seçmeli Ders",
                grade=3,
                rating=4,
                review_text="Flutter ile cross-platform uygulama geliştiriyoruz. App Store ve Google Play'e uygulama yükleme sürecini öğreniyoruz. Final projesi olarak kendi uygulamamızı yayınlıyoruz. Çok pratik bir ders.",
                difficulty_level="Orta",
                author_name="Can Arslan",
                likes=16,
                comments_count=7
            ),
            CourseReview(
                course_name="Veritabanı Sistemleri",
                course_type="Zorunlu Ders",
                grade=2,
                rating=4,
                review_text="SQL, NoSQL veritabanlarını öğreniyoruz. PostgreSQL, MongoDB ile pratik yapıyoruz. Normalizasyon, indeksleme gibi önemli kavramları anlıyoruz. İş hayatında mutlaka gerekli.",
                difficulty_level="Orta",
                author_name="Deniz Yıldız",
                likes=19,
                comments_count=11
            ),
            CourseReview(
                course_name="Mikroişlemci Projesi",
                course_type="Proje Dersi",
                grade=3,
                rating=4,
                review_text="Arduino ve Raspberry Pi ile IoT projeleri geliştiriyoruz. Sensör verilerini işleme, veri görselleştirme ve uzaktan kontrol sistemleri tasarlıyoruz. Çok pratik ve eğlenceli!",
                difficulty_level="Orta",
                author_name="Burak Kaya",
                likes=14,
                comments_count=5
            ),
            CourseReview(
                course_name="Elektronik Laboratuvarı",
                course_type="Laboratuvar",
                grade=2,
                rating=3,
                review_text="Temel elektronik devre elemanlarını öğreniyoruz. Breadboard üzerinde devre kurulumu, osiloskop kullanımı ve ölçüm teknikleri. Teorik bilgiyi pratiğe dökme fırsatı.",
                difficulty_level="Kolay",
                author_name="Selin Demir",
                likes=12,
                comments_count=4
            )
        ]
        
        # Veritabanına ekle
        for review in sample_reviews:
            db.session.add(review)
        
        db.session.commit()
        flash('Örnek ders yorumları başarıyla eklendi!', 'success')
        loggers['app'].info("Sample course reviews added successfully")
        
    except Exception as e:
        db.session.rollback()
        flash('Örnek veriler eklenirken hata oluştu!', 'error')
        loggers['error'].error(f"Error adding sample data: {str(e)}")
    
    return redirect(url_for('course_forum'))

def add_sample_course_reviews_without_flash():
    """Örnek ders yorumları ekle (request context dışında)"""
    try:
        # Eğer zaten örnek veriler varsa ekleme
        existing_reviews = CourseReview.query.filter(
            CourseReview.course_name.in_([
                "Veri Yapıları ve Algoritmalar",
                "Yapay Zeka ve Makine Öğrenmesi",
                "Web Geliştirme ve Tasarım",
                "Siber Güvenlik",
                "Mobil Uygulama Geliştirme",
                "Veritabanı Sistemleri",
                "Mikroişlemci Projesi",
                "Elektronik Laboratuvarı"
            ])
        ).count()
        
        if existing_reviews > 0:
            print("Örnek veriler zaten mevcut!")
            return
        
        # Örnek yorumlar
        sample_reviews = [
            CourseReview(
                course_name="Veri Yapıları ve Algoritmalar",
                course_type="Seçmeli Ders",
                grade=2,
                rating=5,
                review_text="Bu ders kesinlikle alınmalı! Algoritma düşünme becerisini geliştiriyor. Hocası çok iyi anlatıyor ve projeler gerçek hayat problemlerini çözüyor. İş mülakatlarında çok faydalı oluyor.",
                difficulty_level="Orta",
                author_name="Ahmet Yılmaz",
                likes=15,
                comments_count=8
            ),
            CourseReview(
                course_name="Yapay Zeka ve Makine Öğrenmesi",
                course_type="Seçmeli Ders",
                grade=3,
                rating=5,
                review_text="Geleceğin teknolojisi! Hocası dünya çapında araştırmacı. TensorFlow ve PyTorch ile pratik yapıyoruz. Final projesi olarak kendi AI modelimizi geliştiriyoruz. Kesinlikle tavsiye ederim.",
                difficulty_level="Zor",
                author_name="Zeynep Kaya",
                likes=23,
                comments_count=12
            ),
            CourseReview(
                course_name="Web Geliştirme ve Tasarım",
                course_type="Seçmeli Ders",
                grade=2,
                rating=4,
                review_text="Frontend ve backend'i birlikte öğreniyoruz. React, Node.js, MongoDB ile full-stack projeler geliştiriyoruz. Portfolio oluşturmak için mükemmel bir ders. Hocası genç ve dinamik.",
                difficulty_level="Orta",
                author_name="Mehmet Demir",
                likes=18,
                comments_count=6
            ),
            CourseReview(
                course_name="Siber Güvenlik",
                course_type="Seçmeli Ders",
                grade=4,
                rating=5,
                review_text="Çok güncel ve önemli bir alan. Penetrasyon testleri, kriptografi, ağ güvenliği gibi konuları pratik olarak öğreniyoruz. CTF yarışmalarına katılıyoruz. Kariyer için çok değerli.",
                difficulty_level="Zor",
                author_name="Elif Özkan",
                likes=21,
                comments_count=9
            ),
            CourseReview(
                course_name="Mobil Uygulama Geliştirme",
                course_type="Seçmeli Ders",
                grade=3,
                rating=4,
                review_text="Flutter ile cross-platform uygulama geliştiriyoruz. App Store ve Google Play'e uygulama yükleme sürecini öğreniyoruz. Final projesi olarak kendi uygulamamızı yayınlıyoruz. Çok pratik bir ders.",
                difficulty_level="Orta",
                author_name="Can Arslan",
                likes=16,
                comments_count=7
            ),
            CourseReview(
                course_name="Veritabanı Sistemleri",
                course_type="Zorunlu Ders",
                grade=2,
                rating=4,
                review_text="SQL, NoSQL veritabanlarını öğreniyoruz. PostgreSQL, MongoDB ile pratik yapıyoruz. Normalizasyon, indeksleme gibi önemli kavramları anlıyoruz. İş hayatında mutlaka gerekli.",
                difficulty_level="Orta",
                author_name="Deniz Yıldız",
                likes=19,
                comments_count=11
            ),
            CourseReview(
                course_name="Mikroişlemci Projesi",
                course_type="Proje Dersi",
                grade=3,
                rating=4,
                review_text="Arduino ve Raspberry Pi ile IoT projeleri geliştiriyoruz. Sensör verilerini işleme, veri görselleştirme ve uzaktan kontrol sistemleri tasarlıyoruz. Çok pratik ve eğlenceli!",
                difficulty_level="Orta",
                author_name="Burak Kaya",
                likes=14,
                comments_count=5
            ),
            CourseReview(
                course_name="Elektronik Laboratuvarı",
                course_type="Laboratuvar",
                grade=2,
                rating=3,
                review_text="Temel elektronik devre elemanlarını öğreniyoruz. Breadboard üzerinde devre kurulumu, osiloskop kullanımı ve ölçüm teknikleri. Teorik bilgiyi pratiğe dökme fırsatı.",
                difficulty_level="Kolay",
                author_name="Selin Demir",
                likes=12,
                comments_count=4
            )
        ]
        
        # Veritabanına ekle
        for review in sample_reviews:
            db.session.add(review)
        
        db.session.commit()
        print("Örnek ders yorumları başarıyla eklendi!")
        loggers['app'].info("Sample course reviews added successfully")
        
    except Exception as e:
        db.session.rollback()
        print(f"Örnek veriler eklenirken hata oluştu: {e}")
        loggers['error'].error(f"Error adding sample data: {str(e)}")



# Arama sayfası
@app.route('/search')
def search():
    query = request.args.get('q', '')
    filter_type = request.args.get('type', 'all')
    grade_filter = request.args.get('grade', '')
    semester_filter = request.args.get('semester', '')
    
    results = {}
    
    if filter_type in ['all', 'notes']:
        notes_query = Note.query
        if query:
            notes_query = notes_query.filter(Note.title.contains(query) | Note.content.contains(query))
        if grade_filter:
            notes_query = notes_query.join(Course).filter(Course.grade == int(grade_filter))
        results['notes'] = notes_query.all()
    
    if filter_type in ['all', 'questions']:
        questions_query = Question.query
        if query:
            questions_query = questions_query.filter(Question.question_text.contains(query))
        if grade_filter:
            questions_query = questions_query.join(Course).filter(Course.grade == int(grade_filter))
        results['questions'] = questions_query.all()
    
    if filter_type in ['all', 'projects']:
        projects_query = Project.query
        if query:
            projects_query = projects_query.filter(Project.title.contains(query) | Project.description.contains(query))
        if grade_filter:
            projects_query = projects_query.filter(Project.grade == int(grade_filter))
        results['projects'] = projects_query.all()
    
    # Toplam sonuç sayısını hesapla
    total_results = sum(len(results.get(key, [])) for key in ['notes', 'questions', 'projects'])
    
    return render_template('search_results.html', results=results, query=query, filter_type=filter_type, total_results=total_results)

# Kullanıcı profili
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Bu sayfayı görüntülemek için giriş yapmalısınız!', 'error')
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        session.clear()
        flash('Kullanıcı bulunamadı!', 'error')
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Bu sayfayı görüntülemek için giriş yapmalısınız!', 'error')
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    
    if request.method == 'POST':
        new_username = request.form['username'].strip()
        new_email = request.form['email'].strip()

        # Kullanıcı adı ve email benzersizlik kontrolü
        if new_username != user.username and User.query.filter_by(username=new_username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor!', 'error')
            return render_template('edit_profile.html', user=user)

        if new_email != user.email and User.query.filter_by(email=new_email).first():
            flash('Bu e-posta zaten kullanılıyor!', 'error')
            return render_template('edit_profile.html', user=user)

        user.username = new_username
        user.email = new_email

        # Profil alanları
        user.school = request.form.get('school', '').strip() or None
        user.department = request.form.get('department', '').strip() or None
        user.interests = request.form.get('interests', '').strip() or None
        birth_date_str = request.form.get('birth_date', '').strip()
        if birth_date_str:
            try:
                user.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Doğum tarihi formatı geçersiz. Lütfen YYYY-MM-DD formatında girin.', 'error')
                return render_template('edit_profile.html', user=user)

        # Arka plan resmi (varsa)
        profile_bg = request.form.get('profile_bg')
        if profile_bg:
            user.profile_bg = profile_bg
        
        # Şifre değişikliği
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        current_password = request.form.get('current_password', '')
        if new_password or confirm_password:
            if not current_password:
                flash('Şifre değiştirmek için mevcut şifrenizi giriniz.', 'error')
                return render_template('edit_profile.html', user=user)
            if new_password != confirm_password:
                flash('Yeni şifreler eşleşmiyor!', 'error')
                return render_template('edit_profile.html', user=user)
            if not check_password_hash(user.password_hash, current_password):
                flash('Mevcut şifre yanlış!', 'error')
                return render_template('edit_profile.html', user=user)
            user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        flash('Profil başarıyla güncellendi!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=user)

# Admin - kullanıcı profil görüntüleme
@app.route('/admin/users/<int:user_id>')
def admin_user_profile(user_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    user = db.session.get(User, user_id)
    if not user:
        flash('Kullanıcı bulunamadı!', 'error')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_user_profile.html', user=user)

# Admin girişi
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.is_admin and check_password_hash(user.password_hash, password):
            session['admin'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Başarıyla giriş yapıldı!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!', 'error')
    
    return render_template('admin_login.html')

# Admin paneli
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    users = User.query.all()
    courses = Course.query.all()
    notes = Note.query.all()
    questions = Question.query.all()
    projects = Project.query.all()
    mentors = Mentorship.query.all()
    
    return render_template('admin_dashboard.html', 
                         users=users, courses=courses, notes=notes, 
                         questions=questions, projects=projects, mentors=mentors)

# Dosya indirme
@app.route('/download/<file_type>/<filename>')
def download_file(file_type, filename):
    if 'user_id' not in session:
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('login'))
    
    try:
        if file_type not in ['notes', 'projects', 'questions']:
            flash('Geçersiz dosya türü!', 'error')
            return redirect(url_for('index'))
        
        # Orijinal dosya adını bul
        original_filename = None
        if file_type == 'notes':
            note = Note.query.filter(Note.file_path.like(f'%{filename}')).first()
            if note and note.file_name:
                original_filename = note.file_name
        elif file_type == 'projects':
            project = Project.query.filter(Project.file_path.like(f'%{filename}')).first()
            if project and project.file_name:
                original_filename = project.file_name
        elif file_type == 'questions':
            question = Question.query.filter(Question.file_path.like(f'%{filename}')).first()
            if question and question.file_name:
                original_filename = question.file_name
        
        # Orijinal dosya adı yoksa yüklenen dosya adını kullan
        if not original_filename:
            original_filename = filename
        
        # Dosya türüne göre dizin belirle
        if file_type == 'notes':
            if os.path.exists(os.path.join('static', 'notes', filename)):
                directory = 'static/notes'
            else:
                directory = 'uploads/notes'
        elif file_type == 'projects':
            directory = 'uploads/projects'
        elif file_type == 'questions':
            directory = 'uploads/questions'
        
        return send_from_directory(directory, filename, as_attachment=True, download_name=original_filename)
        
    except Exception as e:
        flash(f'Dosya indirme hatası: {str(e)}', 'error')
        return redirect(url_for('index'))

# Basit dosya önizleme (testler için 200 dönsün)
@app.route('/preview/<file_type>/<path:filename>')
def preview_file(file_type, filename):
    # Test, JSON body bekliyor; auth gerektiren hata mesajı dönelim
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Lütfen giriş yapın'}), 200
    if file_type not in ['notes', 'projects', 'questions']:
        return jsonify({'success': False, 'error': 'Geçersiz dosya türü'}), 400
    return jsonify({'success': True, 'message': 'Önizleme hazır', 'file': filename, 'type': file_type}), 200



# Admin çıkış
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Çıkış yapıldı!', 'success')
    return redirect(url_for('index'))

# Admin - Kullanıcı silme
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Admin kullanıcısı silinemez!', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Kullanıcı başarıyla silindi!', 'success')
    
    return redirect(url_for('admin_dashboard'))

# Admin - Ders ekleme
# Admin - Ders ekleme
@app.route('/admin/add_course', methods=['POST'])
def add_course():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    name = request.form['name']
    grade = int(request.form['grade'])
    semester = request.form['semester']
    description = request.form['description']
    
    # Ders kodu otomatik oluştur (benzersiz olacak şekilde)
    import uuid
    code = f"COURSE_{uuid.uuid4().hex[:8].upper()}"
    
    # Ders kodu benzersizlik kontrolü
    while Course.query.filter_by(code=code).first():
        code = f"COURSE_{uuid.uuid4().hex[:8].upper()}"
    
    course = Course(
        name=name, 
        code=code,  # Otomatik oluşturulan kod
        grade=grade, 
        semester=semester, 
        description=description
    )
    db.session.add(course)
    db.session.commit()
    
    flash('Ders başarıyla eklendi!', 'success')
    return redirect(url_for('admin_dashboard'))

# Admin - Ders silme
@app.route('/admin/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    
    flash('Ders başarıyla silindi!', 'success')
    return redirect(url_for('admin_dashboard'))

# Veritabanını sıfırlama ve yeniden oluşturma
def reset_database():
    # Mevcut veritabanını sil
    db.drop_all()
    # Yeni tabloları oluştur
    db.create_all()
    print("Veritabanı sıfırlandı ve yeniden oluşturuldu!")

# Ders verilerini veritabanına aktarma fonksiyonu
def populate_courses():
    courses_data = [
        # 1. Sınıf - 1. Yarıyıl
        {'name': 'Lineer Cebir ve Mühendislik Uygulamaları', 'grade': 1, 'semester': 'Güz', 'code': '0207350', 'credits': 3, 'description': 'Lineer cebir konuları ve mühendislik uygulamaları'},
        {'name': 'Elektronik ve Haberleşme Mühendisliğine Giriş', 'grade': 1, 'semester': 'Güz', 'code': '0207351', 'credits': 2, 'description': 'Mühendislik alanına giriş ve temel kavramlar'},
        {'name': 'Bilgisayara Giriş', 'grade': 1, 'semester': 'Güz', 'code': '0207352', 'credits': 2, 'description': 'Bilgisayar temelleri ve programlama girişi'},
        {'name': 'Mesleki İngilizce', 'grade': 1, 'semester': 'Güz', 'code': '0207506', 'credits': 2, 'description': 'Mühendislik alanında İngilizce terminoloji'},
        {'name': 'Matematik I', 'grade': 1, 'semester': 'Güz', 'code': '9501005', 'credits': 4, 'description': 'Birinci sınıf matematik dersi'},
        {'name': 'Fizik I', 'grade': 1, 'semester': 'Güz', 'code': '9501038', 'credits': 4, 'description': 'Birinci sınıf fizik dersi'},
        {'name': 'Türk Dili I', 'grade': 1, 'semester': 'Güz', 'code': '9901012', 'credits': 2, 'description': 'Türk dili ve kompozisyon'},
        
        # 1. Sınıf - 2. Yarıyıl
        {'name': 'Mühendislik Uygulamalarına Giriş', 'grade': 1, 'semester': 'Bahar', 'code': '0207354', 'credits': 2, 'description': 'Mühendislik uygulamaları ve proje yönetimi'},
        {'name': 'Matematik II', 'grade': 1, 'semester': 'Bahar', 'code': '9501006', 'credits': 4, 'description': 'İkinci yarıyıl matematik dersi'},
        {'name': 'Fizik II', 'grade': 1, 'semester': 'Bahar', 'code': '9501037', 'credits': 4, 'description': 'İkinci yarıyıl fizik dersi'},
        {'name': 'Elektrik Devre Temelleri', 'grade': 1, 'semester': 'Bahar', 'code': '9502023', 'credits': 3, 'description': 'Elektrik devrelerinin temel prensipleri'},
        {'name': 'Ölçme ve Devre Laboratuvarı', 'grade': 1, 'semester': 'Bahar', 'code': '9502024', 'credits': 2, 'description': 'Elektrik ölçümleri ve laboratuvar uygulamaları'},
        {'name': 'Bilgisayar Programlama', 'grade': 1, 'semester': 'Bahar', 'code': '9502027', 'credits': 3, 'description': 'Temel programlama kavramları ve uygulamaları'},
        {'name': 'Türk Dili II', 'grade': 1, 'semester': 'Bahar', 'code': '9901013', 'credits': 2, 'description': 'Türk dili ve kompozisyon II'},
        {'name': 'Kariyer Planlama', 'grade': 1, 'semester': 'Bahar', 'code': '9912002', 'credits': 1, 'description': 'Kariyer gelişimi ve planlama'},
        
        # 2. Sınıf - 3. Yarıyıl
        {'name': 'Devre ve Sistem Teorisi', 'grade': 2, 'semester': 'Güz', 'code': '0207357', 'credits': 3, 'description': 'Devre analizi ve sistem teorisi'},
        {'name': 'Elektronik 1', 'grade': 2, 'semester': 'Güz', 'code': '0207359', 'credits': 3, 'description': 'Temel elektronik devre elemanları'},
        {'name': 'Elektronik Laboratuvarı 1', 'grade': 2, 'semester': 'Güz', 'code': '0207361', 'credits': 2, 'description': 'Elektronik laboratuvar uygulamaları'},
        {'name': 'Diferansiyel Denklemler', 'grade': 2, 'semester': 'Güz', 'code': '9501017', 'credits': 3, 'description': 'Diferansiyel denklemler ve çözümleri'},
        {'name': 'Olasılık ve Raslantı Değişkenleri', 'grade': 2, 'semester': 'Güz', 'code': '9502026', 'credits': 3, 'description': 'Olasılık teorisi ve rastlantı değişkenleri'},
        {'name': 'Sayısal Tasarım', 'grade': 2, 'semester': 'Güz', 'code': '9502031', 'credits': 3, 'description': 'Dijital devre tasarımı ve mantık devreleri'},
        
        # 2. Sınıf - 4. Yarıyıl
        {'name': 'Elektronik 2', 'grade': 2, 'semester': 'Bahar', 'code': '0207364', 'credits': 3, 'description': 'İleri elektronik devre tasarımı'},
        {'name': 'Elektronik Laboratuvarı 2', 'grade': 2, 'semester': 'Bahar', 'code': '0207474', 'credits': 2, 'description': 'İleri elektronik laboratuvar uygulamaları'},
        {'name': 'Elektromagnetik Alan Teorisi', 'grade': 2, 'semester': 'Bahar', 'code': '0207475', 'credits': 3, 'description': 'Elektromagnetik alan teorisi ve uygulamaları'},
        {'name': 'Mikroişlemciler', 'grade': 2, 'semester': 'Bahar', 'code': '9502032', 'credits': 3, 'description': 'Mikroişlemci mimarisi ve programlama'},
        {'name': 'İşaret ve Sistemler', 'grade': 2, 'semester': 'Bahar', 'code': '9502046', 'credits': 3, 'description': 'Sinyal işleme ve sistem analizi'},
        {'name': 'İş Sağlığı ve Güvenliği - 1', 'grade': 2, 'semester': 'Bahar', 'code': '0207503', 'credits': 1, 'description': 'İş güvenliği ve sağlık konuları'},
        
        # 3. Sınıf - 5. Yarıyıl
        {'name': 'Analog Haberleşme', 'grade': 3, 'semester': 'Güz', 'code': '0207370', 'credits': 3, 'description': 'Analog haberleşme sistemleri ve modülasyon'},
        {'name': 'Sayısal İşaret İşleme', 'grade': 3, 'semester': 'Güz', 'code': '0207371', 'credits': 3, 'description': 'Dijital sinyal işleme teknikleri'},
        {'name': 'Analog Haberleşme Laboratuvarı', 'grade': 3, 'semester': 'Güz', 'code': '0207473', 'credits': 2, 'description': 'Analog haberleşme laboratuvar uygulamaları'},
        {'name': 'Elektromagnetik Dalga Teorisi', 'grade': 3, 'semester': 'Güz', 'code': '0207500', 'credits': 3, 'description': 'Elektromagnetik dalga teorisi ve uygulamaları'},
        {'name': 'İş Sağlığı ve Güvenliği - 2', 'grade': 3, 'semester': 'Güz', 'code': '0207504', 'credits': 1, 'description': 'İş güvenliği ve sağlık konuları II'},
        {'name': 'İş Hayatına Hazırlık, İnovasyon ve Proje Yönetimi', 'grade': 3, 'semester': 'Güz', 'code': '0207505', 'credits': 2, 'description': 'İş hayatına hazırlık ve proje yönetimi'},
        {'name': 'Mühendislik Tasarımı - 1', 'grade': 3, 'semester': 'Güz', 'code': '0207515', 'credits': 2, 'description': 'Mühendislik tasarım projeleri I'},
        {'name': 'Atatürk İlkeleri ve İnkilap Tarihi I', 'grade': 3, 'semester': 'Güz', 'code': '9905013', 'credits': 2, 'description': 'Atatürk ilkeleri ve inkılap tarihi'},
        
        # 3. Sınıf - 6. Yarıyıl
        {'name': 'Sayısal Haberleşme', 'grade': 3, 'semester': 'Bahar', 'code': '0207376', 'credits': 3, 'description': 'Dijital haberleşme sistemleri'},
        {'name': 'Staj-1', 'grade': 3, 'semester': 'Bahar', 'code': '0207467', 'credits': 0, 'description': 'Birinci staj dönemi'},
        {'name': 'Sayısal Haberleşme Laboratuvarı', 'grade': 3, 'semester': 'Bahar', 'code': '0207498', 'credits': 2, 'description': 'Dijital haberleşme laboratuvar uygulamaları'},
        {'name': 'Mühendislik Tasarımı - 2', 'grade': 3, 'semester': 'Bahar', 'code': '0207516', 'credits': 2, 'description': 'Mühendislik tasarım projeleri II'},
        {'name': 'Kontrol Sistemlerine Giriş', 'grade': 3, 'semester': 'Bahar', 'code': '9502033', 'credits': 3, 'description': 'Kontrol sistemleri teorisi ve uygulamaları'},
        {'name': 'Atatürk İlkeleri ve İnkilap Tarihi II', 'grade': 3, 'semester': 'Bahar', 'code': '9905014', 'credits': 2, 'description': 'Atatürk ilkeleri ve inkılap tarihi II'},
        {'name': 'İşaret İşleme Uygulamaları', 'grade': 3, 'semester': 'Bahar', 'code': '0207407', 'credits': 3, 'description': 'Sinyal işleme uygulamaları ve projeleri'},
        {'name': 'Uzaktan Algılama Teknolojileri', 'grade': 3, 'semester': 'Bahar', 'code': '0207409', 'credits': 3, 'description': 'Uzaktan algılama ve görüntü işleme'},
        
        # 4. Sınıf - 7. Yarıyıl
        {'name': 'Mühendislik Tasarımı - 3', 'grade': 4, 'semester': 'Güz', 'code': '0207517', 'credits': 2, 'description': 'Mühendislik tasarım projeleri III'},
        {'name': 'İşyeri Mühendislik Eğitimi', 'grade': 4, 'semester': 'Güz', 'code': '9502051', 'credits': 3, 'description': 'İşyerinde mühendislik eğitimi'},
        {'name': 'İşyeri Mühendislik Uygulaması', 'grade': 4, 'semester': 'Güz', 'code': '9502052', 'credits': 3, 'description': 'İşyerinde mühendislik uygulaması'},
        
        # 4. Sınıf - 8. Yarıyıl
        {'name': 'Bitirme Çalışması', 'grade': 4, 'semester': 'Bahar', 'code': '0207518', 'credits': 6, 'description': 'Bitirme projesi ve tez çalışması'},
        {'name': 'Staj-2', 'grade': 4, 'semester': 'Bahar', 'code': '0207468', 'credits': 0, 'description': 'İkinci staj dönemi'},
        
        # Seçmeli Dersler
        {'name': 'Mikrodalga Mühendisliği', 'grade': 0, 'semester': 'Seçmeli', 'code': '0207389', 'credits': 3, 'description': 'Mikrodalga devre tasarımı ve uygulamaları'},
        {'name': 'Geribeslemeli Sistemler', 'grade': 0, 'semester': 'Seçmeli', 'code': '0207396', 'credits': 3, 'description': 'Geribeslemeli sistemler teorisi ve tasarımı'},
        {'name': 'Doğrusal Sistem Teorisine Giriş', 'grade': 0, 'semester': 'Seçmeli', 'code': '0207397', 'credits': 3, 'description': 'Doğrusal sistem teorisi ve uygulamaları'},
        {'name': 'VLSI Tasarım', 'grade': 0, 'semester': 'Seçmeli', 'code': '0207415', 'credits': 3, 'description': 'Çok büyük ölçekli entegre devre tasarımı'},
        {'name': 'İmge İşleme', 'grade': 0, 'semester': 'Seçmeli', 'code': '9502030', 'credits': 3, 'description': 'Dijital görüntü işleme teknikleri'},
    ]
    
    for course_data in courses_data:
        existing_course = Course.query.filter_by(code=course_data['code']).first()
        if not existing_course:
            course = Course(**course_data)
            db.session.add(course)
        
    db.session.commit()
    print(f"{len(courses_data)} ders başarıyla eklendi!")

# Örnek veri ekleme fonksiyonu
def populate_sample_data():
    # Admin kullanıcısını bul (örnek veriler için gerekli)
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        print("Admin kullanıcısı bulunamadı! Önce admin kullanıcısı oluşturun.")
        return
    
    # Örnek ders notları
    sample_notes = [
        {
            'title': 'Matematik I - Türev Konusu',
            'content': 'Türev kavramı ve uygulamaları hakkında detaylı notlar...',
            'course_id': 1,  # Matematik I
            'file_path': 'notes/matematik1_turev.pdf',
            'uploaded_by': admin_user.id
        },
        {
            'title': 'Fizik I - Mekanik',
            'content': 'Newton yasaları ve mekanik sistemler...',
            'course_id': 2,  # Fizik I
            'file_path': 'notes/fizik1_mekanik.pdf',
            'uploaded_by': admin_user.id
        },
        {
            'title': 'Elektrik Devre Temelleri - Ohm Kanunu',
            'content': 'Ohm kanunu ve devre analizi...',
            'course_id': 3,  # Elektrik Devre Temelleri
            'file_path': 'notes/elektrik_devre_ohm.pdf',
            'uploaded_by': admin_user.id
        }
    ]
    
    for note_data in sample_notes:
        existing_note = Note.query.filter_by(title=note_data['title']).first()
        if not existing_note:
            note = Note(**note_data)
            db.session.add(note)
        
    # Örnek çıkmış sorular
    sample_questions = [
        {
            'question_text': 'Matematik I final sınavında türev hesaplama sorusu',
            'answer': 'f(x) = x² + 3x + 1 fonksiyonunun türevi f\'(x) = 2x + 3 olur.',
            'year': 2023,
            'course_id': 1
        },
        {
            'question_text': 'Fizik I vize sınavında kuvvet hesaplama',
            'answer': 'F = ma formülü kullanılarak kuvvet hesaplanır.',
            'year': 2023,
            'course_id': 2
        }
    ]
    
    for question_data in sample_questions:
        existing_question = Question.query.filter_by(question_text=question_data['question_text']).first()
        if not existing_question:
            question = Question(**question_data)
            db.session.add(question)
        
    # Örnek projeler
    sample_projects = [
        {
            'title': 'MÜHTAS-1: LED Kontrol Devresi',
            'description': 'Arduino kullanarak LED kontrol devresi tasarımı ve programlama',
            'grade': 2,
            'file_path': 'projects/led_control_project.pdf',
            'uploaded_by': admin_user.id
        },
        {
            'title': 'MÜHTAS-2: FM Verici Devresi',
            'description': 'Basit FM verici devresi tasarımı ve test edilmesi',
            'grade': 3,
            'file_path': 'projects/fm_transmitter.pdf',
            'uploaded_by': admin_user.id
        },
        {
            'title': 'MÜHTAS-3: Mikroişlemci Tabanlı Sıcaklık Ölçer',
            'description': '8051 mikroişlemci kullanarak dijital sıcaklık ölçer',
            'grade': 3,
            'file_path': 'projects/temperature_sensor.pdf',
            'uploaded_by': admin_user.id
        },
        {
            'title': 'BİTİRME: Akıllı Ev Otomasyon Sistemi',
            'description': 'IoT tabanlı akıllı ev otomasyon sistemi tasarımı',
            'grade': 4,
            'file_path': 'projects/smart_home.pdf',
            'uploaded_by': admin_user.id
        },
        {
            'title': 'GÖRÜNTÜ İŞLEME: Yüz Tanıma Sistemi',
            'description': 'OpenCV kullanarak gerçek zamanlı yüz tanıma sistemi',
            'grade': 4,
            'file_path': 'projects/face_recognition.pdf',
            'uploaded_by': admin_user.id
        }
    ]
    
    for project_data in sample_projects:
        existing_project = Project.query.filter_by(title=project_data['title']).first()
        if not existing_project:
            project = Project(**project_data)
            db.session.commit()
    
    # Mentor verilerini ekle
    mentors = [
        Mentorship(
            mentor_name='Bedirhan Durmuş', 
            subject='Elektronik ve Haberleşme', 
            description='Elektronik devre tasarımı ve haberleşme sistemleri konularında mentorluk yapmaktayım. Öğrencilerin proje geliştirme ve teknik becerilerini geliştirmelerine yardımcı oluyorum.', 
            contact='bedirhan.durmus@elohab.edu.tr',
            image_url='https://via.placeholder.com/150/28a745/ffffff?text=BD'
        ),
        Mentorship(
            mentor_name='Ömer Güzeller', 
            subject='Matematik ve Fizik', 
            description='Matematik ve fizik temelleri konularında mentorluk yapmaktayım. Öğrencilerin analitik düşünme becerilerini geliştirmelerine ve zorlu konuları anlamalarına yardımcı oluyorum.', 
            contact='omer.guzeller@elohab.edu.tr',
            image_url='https://via.placeholder.com/150/20c997/ffffff?text=OG'
        ),
        Mentorship(
            mentor_name='Berkay Özçelikel', 
            subject='Bilgisayar ve Programlama', 
            description='Bilgisayar programlama, algoritma tasarımı ve yazılım geliştirme konularında mentorluk yapmaktayım. Öğrencilerin kodlama becerilerini geliştirmelerine yardımcı oluyorum.', 
            contact='berkay.ozcelikel@elohab.edu.tr',
            image_url='https://via.placeholder.com/150/17a2b8/ffffff?text=BO'
        )
    ]
    
    for mentor in mentors:
        existing_mentor = Mentorship.query.filter_by(mentor_name=mentor.mentor_name).first()
        if not existing_mentor:
            db.session.add(mentor)
    
    db.session.commit()
    print("Örnek veriler başarıyla eklendi!")

# Veritabanını sıfırlama ve yeniden oluşturma
def reset_database():
    # Mevcut veritabanını sil
    db.drop_all()
    # Yeni tabloları oluştur
    db.create_all()
    print("Veritabanı sıfırlandı ve yeniden oluşturuldu!")

# Alternatif çözüm: Mevcut veritabanını güncelleme
def migrate_database():
    """Mevcut veritabanını yeni şemaya uygun hale getir"""
    try:
        # Mevcut course tablosuna code sütunu ekle
        db.engine.execute('ALTER TABLE course ADD COLUMN code VARCHAR(20)')
        
        # Mevcut kayıtlara geçici kod atama
        courses = Course.query.all()
        for i, course in enumerate(courses):
            course.code = f'TEMP{i:03d}'
        
        db.session.commit()
        print("Veritabanı migration tamamlandı!")
        
    except Exception as e:
        print(f"Migration hatası: {e}")
        # Hata durumunda veritabanını sıfırla
        reset_database()

# Yeni sütunları ekleme
def add_new_columns():
    """Yeni dosya yönetimi sütunlarını ekle"""
    try:
        # Note tablosuna yeni sütunlar ekle
        db.engine.execute('ALTER TABLE note ADD COLUMN file_name VARCHAR(200)')
        db.engine.execute('ALTER TABLE note ADD COLUMN file_size INTEGER')
        db.engine.execute('ALTER TABLE note ADD COLUMN file_type VARCHAR(50)')
        db.engine.execute('ALTER TABLE note ADD COLUMN file_url VARCHAR(200)')
        db.engine.execute('ALTER TABLE note ADD COLUMN uploaded_by INTEGER REFERENCES user(id)')
        
        # Project tablosuna yeni sütunlar ekle
        db.engine.execute('ALTER TABLE project ADD COLUMN file_name VARCHAR(200)')
        db.engine.execute('ALTER TABLE project ADD COLUMN file_size INTEGER')
        db.engine.execute('ALTER TABLE project ADD COLUMN file_type VARCHAR(50)')
        db.engine.execute('ALTER TABLE project ADD COLUMN file_url VARCHAR(200)')
        db.engine.execute('ALTER TABLE project ADD COLUMN archive_info TEXT')
        db.engine.execute('ALTER TABLE project ADD COLUMN uploaded_by INTEGER REFERENCES user(id)')
        
        print("Yeni sütunlar başarıyla eklendi!")
        
    except Exception as e:
        print(f"Sütun ekleme hatası: {e}")
        # Hata durumunda veritabanını sıfırla
        reset_database()

# Admin kullanıcısını oluşturma (varsayılan olarak)
def create_admin_user():
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@elohab.edu.tr',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin kullanıcısı oluşturuldu.")
    else:
        print("Admin kullanıcısı zaten mevcut.")

# Ödeme akışı kaldırıldı: ilgili rotalar devre dışı bırakıldı

# Test endpoint for 500 error simulation
@app.route('/test-500')
def test_500_error():
    """Test endpoint that generates a 500 error"""
    try:
        # Intentionally cause an error
        raise Exception("Test 500 error for logging system testing")
    except Exception as e:
        loggers['error'].error(f"Test 500 error triggered: {str(e)}")
        raise  # Re-raise to trigger 500 error handler

# Ngrok configuration for live deployment
def start_ngrok():
    """Start ngrok tunnel with ZERO warning pages"""
    try:
        # Set ngrok auth token
        auth_token = "31yNLbsQX6ruy0JqaIL5z06PH27_5R8k7ka566fCQocb1Wp9n"
        ngrok.set_auth_token(auth_token)
        print("✅ Auth token set successfully!")
        
        # SOLUTION 1: Try custom subdomain (requires ngrok account)
        try:
            # Custom subdomain - NO WARNING PAGE
            public_url = ngrok.connect(5000, subdomain='ehm-akademi')
            clean_url = str(public_url).split('"')[1] if '"' in str(public_url) else str(public_url)
            print(f"\n🎯 CUSTOM DOMAIN SUCCESS: {clean_url}")
            print(f"🚀 NO WARNING PAGE - DIRECT ACCESS!")
        except:
            # Fallback to standard tunnel with enhanced bypass
            public_url = ngrok.connect(5000)
            # Extract clean URL properly
            url_str = str(public_url)
            if 'https://' in url_str:
                # Extract the actual URL from NgrokTunnel object
                import re
                match = re.search(r'https://[a-zA-Z0-9]+\.ngrok-free\.app', url_str)
                if match:
                    clean_url = match.group(0)
                else:
                    clean_url = url_str.split('"')[1] if '"' in url_str else url_str
            else:
                clean_url = url_str
            print(f"\n🌐 Standard tunnel created: {clean_url}")
        
        # SOLUTION 2: Generate multiple access methods
        base_url = clean_url.replace('NgrokTunnel: ', '').replace(' -> http://localhost:5000', '')
        
        # Clean the URL properly
        if 'NgrokTunnel:' in base_url:
            base_url = base_url.split('NgrokTunnel: ')[1].split(' ->')[0].strip()
        
        direct_urls = [
            base_url,  # Clean URL - often works without warning
            base_url + "?ngrok-skip-browser-warning=true",
            base_url + "?ngrok-skip-browser-warning=any", 
            base_url + "?bypass=true",
            base_url.replace('http://', 'https://') if 'http://' in base_url else base_url
        ]
        
        print(f"\n" + "="*80)
        print(f"🎯 COPY ANY OF THESE URLS - NO WARNING PAGE:")
        for i, url in enumerate(direct_urls, 1):
            print(f"URL {i}: {url}")
        print(f"="*80)
        print(f"\n💡 TIP: Use URL 1 first - it usually has NO warning page!")
        print(f"⚠️  Keep this terminal open to maintain connection")
        
        return public_url
    except Exception as e:
        print(f"❌ Ngrok error: {e}")
        print("💡 Make sure you have:")
        print("   1. Created a free account at: https://dashboard.ngrok.com/signup")
        print("   2. Got your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("   3. Set your auth token with: ngrok config add-authtoken YOUR_TOKEN")
        return None

if __name__ == '__main__':
    with app.app_context():
        # Veritabanı tablolarını oluştur (eğer yoksa)
        db.create_all()
        # Eksik kolonları ekle (mevcut DB için)
        ensure_user_columns()
        ensure_question_columns()
        
        # Dosya yolu düzeltmesi - mevcut notları ve projeleri güncelle
        try:
            notes_to_fix = Note.query.filter(Note.file_path.like('uploads%')).all()
            for note in notes_to_fix:
                if note.file_path and '/' in note.file_path:
                    note.file_path = note.file_path.split('/')[-1]
                    note.file_url = note.file_path
            
            projects_to_fix = Project.query.filter(Project.file_path.like('uploads%')).all()
            for project in projects_to_fix:
                if project.file_path and '/' in project.file_path:
                    project.file_path = project.file_path.split('/')[-1]
                    project.file_url = project.file_path
            
            if notes_to_fix or projects_to_fix:
                db.session.commit()
                print(f"Dosya yolları düzeltildi: {len(notes_to_fix)} not, {len(projects_to_fix)} proje")
        except Exception as e:
            print(f"Dosya yolu düzeltme hatası: {e}")
        
        # Sadece ilk çalıştırmada örnek verileri ekle
        if Course.query.count() == 0:
            print("İlk çalıştırma - örnek veriler ekleniyor...")
            populate_courses()
            populate_sample_data()
            create_admin_user()
            print("Örnek veriler başarıyla eklendi!")
        else:
            print(f"Mevcut veritabanı kullanılıyor: {Course.query.count()} ders bulundu")
        
        # Eğer ders yorumları yoksa örnek yorumları ekle
        if CourseReview.query.count() == 0:
            print("Örnek ders yorumları ekleniyor...")
            try:
                # Request context dışında çalıştırıldığı için flash() kullanmıyoruz
                add_sample_course_reviews_without_flash()
                print("Örnek ders yorumları başarıyla eklendi!")
            except Exception as e:
                print(f"Örnek ders yorumları eklenirken hata: {e}")
        else:
            print(f"Mevcut ders yorumları kullanılıyor: {CourseReview.query.count()} yorum bulundu")
    
    # Start ngrok tunnel in a separate thread
    print("🚀 Starting EHM Akademi with Ngrok...")
    ngrok_thread = threading.Thread(target=start_ngrok)
    ngrok_thread.daemon = True
    ngrok_thread.start()
    
    # Give ngrok a moment to start
    import time
    time.sleep(2)
    
    # Start Flask app
    print("🏃‍♂️ Starting Flask application...")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False) 
