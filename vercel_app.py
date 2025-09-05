from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import traceback
from datetime import datetime
from file_manager import FileManager
from sqlalchemy import text

# Vercel için özel konfigürasyon
app = Flask(__name__, static_folder='assets', static_url_path='/assets')
app.config['SECRET_KEY'] = 'elohab2024secretkey'

# Vercel'de SQLite yerine PostgreSQL veya başka bir veritabanı kullanılmalı
# Şimdilik SQLite ile devam ediyoruz ama production'da değiştirilmeli
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elohab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Note model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Project model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Grade model
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Hakkında sayfası
@app.route('/about')
def about():
    return render_template('about.html')

# Kayıt ol
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor!')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Bu email zaten kullanılıyor!')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Giriş yap
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Başarıyla giriş yaptınız!')
            return redirect(url_for('index'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre!')
    
    return render_template('login.html')

# Çıkış yap
@app.route('/logout')
def logout():
    session.clear()
    flash('Başarıyla çıkış yaptınız!')
    return redirect(url_for('index'))

# Profil sayfası
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

# Notlar sayfası
@app.route('/notes')
def notes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_notes = Note.query.filter_by(user_id=session['user_id']).order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=user_notes)

# Projeler sayfası
@app.route('/projects')
def projects():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_projects = Project.query.filter_by(user_id=session['user_id']).order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=user_projects)

# Sorular sayfası
@app.route('/questions')
def questions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_questions = Question.query.filter_by(user_id=session['user_id']).order_by(Question.created_at.desc()).all()
    return render_template('questions.html', questions=user_questions)

# Not ekle
@app.route('/add_note', methods=['GET', 'POST'])
def add_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        note = Note(title=title, content=content, user_id=session['user_id'])
        db.session.add(note)
        db.session.commit()
        
        flash('Not başarıyla eklendi!')
        return redirect(url_for('notes'))
    
    return render_template('add_note.html')

# Proje ekle
@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        project = Project(title=title, description=description, user_id=session['user_id'])
        db.session.add(project)
        db.session.commit()
        
        flash('Proje başarıyla eklendi!')
        return redirect(url_for('projects'))
    
    return render_template('add_project.html')

# Soru ekle
@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        question = Question(title=title, content=content, user_id=session['user_id'])
        db.session.add(question)
        db.session.commit()
        
        flash('Soru başarıyla eklendi!')
        return redirect(url_for('questions'))
    
    return render_template('add_question.html')

# Admin dashboard
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    users = User.query.all()
    notes = Note.query.all()
    projects = Project.query.all()
    questions = Question.query.all()
    
    return render_template('admin_dashboard.html', 
                         users=users, notes=notes, 
                         projects=projects, questions=questions)

# Vercel için gerekli
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
