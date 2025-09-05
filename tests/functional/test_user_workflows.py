import pytest
from datetime import datetime, timedelta

class TestUserRegistrationWorkflow:
    """Test complete user registration workflow"""
    
    def test_complete_registration_workflow(self, client, db_session):
        """Test complete user registration and activation workflow"""
        # Step 1: User visits registration page
        response = client.get('/register')
        assert response.status_code == 200
        
        # Step 2: User fills registration form
        response = client.post('/register', data={
            'username': 'workflowuser',
            'email': 'workflow@example.com',
            'password': 'workflow123',
            'confirm_password': 'workflow123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Step 3: Verify user was created
        from app import User
        user = db_session.query(User).filter_by(username='workflowuser').first()
        assert user is not None
        assert user.email == 'workflow@example.com'
        assert user.is_active is True  # Payment flow removed, users are active immediately
        
        # Step 4: User logs in (should work even if inactive)
        response = client.post('/login', data={
            'username': 'workflowuser',
            'password': 'workflow123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Step 5: Check if user can access basic pages
        response = client.get('/')
        assert response.status_code == 200
        
        # Step 6: Check if user is redirected from protected pages
        response = client.get('/notes', follow_redirects=True)
        assert response.status_code == 200

class TestNoteManagementWorkflow:
    """Test complete note management workflow"""
    
    def test_note_creation_workflow(self, client, sample_user, sample_course, db_session):
        """Test complete note creation workflow"""
        # Step 1: Login as user
        client.post('/login', data={
            'username': sample_user.username,
            'password': 'testpass123'
        })
        
        # Step 2: Visit notes page
        response = client.get('/notes')
        assert response.status_code == 200
        
        # Step 3: Visit add note page
        response = client.get('/notes/add')
        assert response.status_code == 200
        
        # Step 4: Create note
        response = client.post('/notes/add', data={
            'title': 'Workflow Note',
            'content': 'This note was created through workflow testing',
            'course_id': sample_course.id
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Step 5: Verify note was created
        from app import Note
        note = db_session.query(Note).filter_by(title='Workflow Note').first()
        assert note is not None
        assert note.content == 'This note was created through workflow testing'
        assert note.course_id == sample_course.id
        assert note.uploaded_by == sample_user.id
        
        # Step 6: Edit note
        response = client.get(f'/notes/edit/{note.id}')
        assert response.status_code == 200
        
        response = client.post(f'/notes/edit/{note.id}', data={
            'title': 'Updated Workflow Note',
            'content': 'This note was updated through workflow testing',
            'course_id': sample_course.id
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Step 7: Verify note was updated
        updated_note = db_session.get(Note, note.id)
        assert updated_note.title == 'Updated Workflow Note'
        assert updated_note.content == 'This note was updated through workflow testing'

class TestProjectManagementWorkflow:
    """Test complete project management workflow"""
    
    def test_project_creation_workflow(self, client, sample_user, db_session):
        """Test complete project creation workflow"""
        # Step 1: Login as user
        client.post('/login', data={
            'username': sample_user.username,
            'password': 'testpass123'
        })
        
        # Step 2: Visit projects page
        response = client.get('/projects')
        assert response.status_code == 200
        
        # Step 3: Visit add project page
        response = client.get('/projects/add')
        assert response.status_code == 200
        
        # Step 4: Create project
        response = client.post('/projects/add', data={
            'title': 'Workflow Project',
            'description': 'This project was created through workflow testing',
            'grade': 2
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Step 5: Verify project was created
        from app import Project
        project = db_session.query(Project).filter_by(title='Workflow Project').first()
        assert project is not None
        assert project.description == 'This project was created through workflow testing'
        assert project.grade == 2
        assert project.uploaded_by == sample_user.id

class TestSearchWorkflow:
    """Test search functionality workflow"""
    
    def test_search_workflow(self, client, db_session):
        """Test complete search workflow"""
        # Step 1: Create test data
        from app import User, Course, Note, Question
        
        user = User(username='searchuser', email='search@example.com', password_hash='hash')
        course = Course(name='Search Course', code='SEARCH101', grade=1, semester='Güz')
        db_session.add_all([user, course])
        db_session.commit()
        
        note = Note(
            title='Searchable Note',
            content='This note contains searchable content about Python',
            course_id=course.id,
            uploaded_by=user.id
        )
        question = Question(
            question_text='What is Python programming?',
            answer='Python is a high-level programming language',
            year=2024,
            course_id=course.id
        )
        db_session.add_all([note, question])
        db_session.commit()
        
        # Step 2: Perform search
        response = client.get('/search?q=Python')
        assert response.status_code == 200
        
        # Step 3: Verify search results contain expected content
        assert b'Searchable Note' in response.data
        assert b'Python programming' in response.data
        
        # Step 4: Test empty search
        response = client.get('/search?q=')
        assert response.status_code == 200
        
        # Step 5: Test search with no results
        response = client.get('/search?q=NonExistentContent')
        assert response.status_code == 200

class TestUserProfileWorkflow:
    """Test user profile management workflow"""
    
    def test_profile_management_workflow(self, client, sample_user, db_session):
        """Test complete profile management workflow"""
        # Step 1: Login as user
        client.post('/login', data={
            'username': sample_user.username,
            'password': 'testpass123'
        })
        
        # Step 2: Visit profile page
        response = client.get('/profile')
        assert response.status_code == 200
        
        # Step 3: Visit edit profile page
        response = client.get('/profile/edit')
        assert response.status_code == 200
        
        # Step 4: Update profile
        response = client.post('/profile/edit', data={
            'username': 'updateduser',
            'email': 'updated@example.com',
            'current_password': '',      # Boş (şifre değiştirmiyoruz)
            'new_password': '',          # Boş (şifre değiştirmiyoruz)
            'confirm_password': ''       # Boş (şifre değiştirmiyoruz)
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Step 5: Verify profile was updated
        from app import User
        updated_user = db_session.get(User, sample_user.id)
        assert updated_user.username == 'updateduser'
        assert updated_user.email == 'updated@example.com'
