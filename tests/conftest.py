import pytest
import tempfile
import os
from app import app, db
from werkzeug.security import generate_password_hash
import uuid

@pytest.fixture(scope='function')
def client():
    """Test client for Flask app with isolated database"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Use temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Create app context first
    with app.app_context():
        # Drop all tables first to ensure clean state
        db.drop_all()
        db.create_all()
        
        # Then create test client
        with app.test_client() as client:
            yield client
            
            # Cleanup - drop all tables
            db.drop_all()
        
        # Cleanup temp file
        os.close(db_fd)
        os.unlink(db_path)

@pytest.fixture(scope='function')
def app_context():
    """Application context for testing"""
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def db_session():
    """Database session for testing"""
    with app.app_context():
        # Drop all tables first to ensure clean state
        db.drop_all()
        # Create all tables for testing
        db.create_all()
        yield db.session
        # Cleanup - drop all tables
        db.drop_all()

@pytest.fixture(scope='function')
def sample_user(db_session):
    """Create a unique sample user for testing"""
    from app import User
    
    # Generate unique identifiers
    unique_id = str(uuid.uuid4())[:8]
    username = f'testuser_{unique_id}'
    email = f'test_{unique_id}@example.com'
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash('testpass123'),
        is_admin=False,
        package_type='temel',
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(scope='function')
def sample_admin_user(db_session):
    """Create a unique sample admin user for testing"""
    from app import User
    
    # Generate unique identifiers
    unique_id = str(uuid.uuid4())[:8]
    username = f'admin_{unique_id}'
    email = f'admin_{unique_id}@example.com'
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash('admin123'),
        is_admin=True,
        package_type='pro',
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(scope='function')
def sample_course(db_session):
    """Create a unique sample course for testing"""
    from app import Course
    
    # Generate unique identifiers
    unique_id = str(uuid.uuid4())[:8]
    code = f'TEST_{unique_id}'
    
    course = Course(
        name=f'Test Course {unique_id}',
        code=code,
        grade=1,
        semester='Güz',
        description='Test course description',
        credits=3
    )
    db_session.add(course)
    db_session.commit()
    return course

@pytest.fixture
def auth_headers(sample_user):
    """Authentication headers for testing protected routes"""
    return {'Authorization': f'Bearer {sample_user.id}'}
