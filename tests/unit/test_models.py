import pytest
from datetime import datetime, timedelta

class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self, db_session):
        """Test basic user creation"""
        from app import User
        
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password',
            package_type='temel',
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.is_active is True
    
    def test_user_package_expiration(self, db_session):
        """Test user package expiration logic"""
        from app import User
        
        # Create user with expired package
        expired_date = datetime.now() - timedelta(days=1)
        user = User(
            username='expireduser',
            email='expired@example.com',
            password_hash='hash',
            package_type='temel',
            package_expires=expired_date,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.package_expires < datetime.now()
        assert user.is_active is False

class TestCourseModel:
    """Test Course model functionality"""
    
    def test_course_creation(self, db_session):
        """Test basic course creation"""
        from app import Course
        
        course = Course(
            name='Test Course',
            code='TEST101',
            grade=1,
            semester='Güz',
            description='Test description',
            credits=3
        )
        db_session.add(course)
        db_session.commit()
        
        assert course.id is not None
        assert course.name == 'Test Course'
        assert course.code == 'TEST101'
        assert course.grade == 1
    
    def test_course_repr(self, db_session):
        """Test course string representation"""
        from app import Course
        
        course = Course(
            name='Test Course',
            code='TEST101',
            grade=1,
            semester='Güz'
        )
        db_session.add(course)
        db_session.commit()
        
        assert str(course) == '<Course TEST101: Test Course>'

class TestNoteModel:
    """Test Note model functionality"""
    
    def test_note_creation(self, db_session, sample_user, sample_course):
        """Test basic note creation"""
        from app import Note
        
        note = Note(
            title='Test Note',
            content='Test content',
            course_id=sample_course.id,
            uploaded_by=sample_user.id
        )
        db_session.add(note)
        db_session.commit()
        
        assert note.id is not None
        assert note.title == 'Test Note'
        assert note.content == 'Test content'
        assert note.course_id == sample_course.id
        assert note.uploaded_by == sample_user.id

class TestQuestionModel:
    """Test Question model functionality"""
    
    def test_question_creation(self, db_session, sample_course):
        """Test basic question creation"""
        from app import Question
        
        question = Question(
            question_text='What is testing?',
            answer='Testing is verification',
            year=2024,
            course_id=sample_course.id
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.question_text == 'What is testing?'
        assert question.answer == 'Testing is verification'
        assert question.year == 2024

class TestProjectModel:
    """Test Project model functionality"""
    
    def test_project_creation(self, db_session, sample_user):
        """Test basic project creation"""
        from app import Project
        
        project = Project(
            title='Test Project',
            description='Test description',
            grade=2,
            uploaded_by=sample_user.id
        )
        db_session.add(project)
        db_session.commit()
        
        assert project.id is not None
        assert project.title == 'Test Project'
        assert project.description == 'Test description'
        assert project.grade == 2
