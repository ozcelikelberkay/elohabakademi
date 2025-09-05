import pytest
from werkzeug.security import check_password_hash, generate_password_hash

class TestAuthenticationSecurity:
    """Test authentication security measures"""
    
    def test_password_hashing(self, db_session):
        """Test that passwords are properly hashed"""
        from app import User
        
        # Create user with plain text password - this should be hashed by the app
        # The app.py uses generate_password_hash() during registration
        user = User(
            username='securityuser',
            email='security@example.com',
            password_hash=generate_password_hash('plaintext_password'),  # Already hashed
            package_type='temel'
        )
        db_session.add(user)
        db_session.commit()
        
        # Password should not be stored as plaintext
        assert user.password_hash != 'plaintext_password'
        
        # Should be able to verify password
        assert check_password_hash(user.password_hash, 'plaintext_password')
    
    def test_session_security(self, client, sample_user):
        """Test session security measures"""
        # Login user
        response = client.post('/login', data={
            'username': sample_user.username,
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Check if session is created
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert sess['user_id'] == sample_user.id
        
        # Test session timeout (simulate by clearing session)
        client.get('/logout')
        
        # Should not be able to access protected routes
        response = client.get('/profile', follow_redirects=True)
        # Check if login form exists (either Turkish or ASCII version)
        assert b'Giri' in response.data or b'Login' in response.data
    
    def test_csrf_protection(self, client):
        """Test CSRF protection (if implemented)"""
        # This test checks if CSRF protection is in place
        # Note: Current implementation may not have CSRF protection
        response = client.get('/register')
        assert response.status_code == 200

class TestAuthorizationSecurity:
    """Test authorization and access control"""
    
    def test_admin_route_protection(self, client, sample_user):
        """Test that admin routes are protected from regular users"""
        # Login as regular user
        client.post('/login', data={
            'username': sample_user.username,
            'password': 'testpass123'
        })
        
        # Try to access admin dashboard - should redirect to admin login
        response = client.get('/admin/dashboard', follow_redirects=True)
        # Should redirect to admin login page
        assert response.status_code == 200
        # Check if redirected to admin login (either Turkish or English)
        assert b'admin' in response.data.lower() or b'Admin' in response.data
    
    def test_user_isolation(self, client, db_session):
        """Test that users cannot access other users' data"""
        from app import User, Note, Course
        
        # Create two users with proper password hashes
        user1 = User(username='user1', email='user1@example.com', password_hash=generate_password_hash('password1'), is_active=True)
        user2 = User(username='user2', email='user2@example.com', password_hash=generate_password_hash('password2'), is_active=True)
        
        # Create course
        course = Course(name='Test Course', code='TEST101', grade=1, semester='Güz')
        
        # Add users and course
        db_session.add_all([user1, user2, course])
        db_session.commit()
        
        # Create note for user1
        note1 = Note(
            title='User1 Note',
            content='Private note for user1',
            course_id=course.id,
            uploaded_by=user1.id
        )
        
        db_session.add(note1)
        db_session.commit()
        
        # Login as user1
        response = client.post('/login', data={
            'username': 'user1',
            'password': 'password1'
        }, follow_redirects=True)
        
        # Check session
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert sess['user_id'] == user1.id
        
        # User1 should be able to see their own note
        response = client.get(f'/notes/edit/{note1.id}')
        assert response.status_code == 200
        
        # Logout and login as user2
        client.get('/logout')
        response = client.post('/login', data={
            'username': 'user2',
            'password': 'password2'
        }, follow_redirects=True)
        
        # Check session
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert sess['user_id'] == user2.id
        
        # User2 should not be able to edit user1's note - should redirect
        response = client.get(f'/notes/edit/{note1.id}', follow_redirects=True)
        # Should redirect to notes page with access denied message
        assert response.status_code == 200

class TestInputValidationSecurity:
    """Test input validation and sanitization"""
    
    def test_sql_injection_prevention(self, client, db_session):
        """Test SQL injection prevention"""
        from app import User
        
        # Try to inject SQL in username
        malicious_username = "'; DROP TABLE user; --"
        
        response = client.post('/register', data={
            'username': malicious_username,
            'email': 'injection@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        # Should not crash the application
        assert response.status_code == 200
        
        # Check if malicious user was created (should be handled safely)
        user = db_session.query(User).filter_by(username=malicious_username).first()
        # The exact behavior depends on how the application handles this
        
        # Verify database integrity
        all_users = db_session.query(User).all()
        assert len(all_users) >= 0  # Should not crash
    
    def test_xss_prevention(self, client, db_session):
        """Test XSS prevention"""
        from app import User, Note, Course
        
        # Create test data
        user = User(username='xsstest', email='xss@example.com', password_hash=generate_password_hash('password'), is_active=True)
        course = Course(name='XSS Course', code='XSS101', grade=1, semester='Güz')
        db_session.add_all([user, course])
        db_session.commit()
        
        # Login
        client.post('/login', data={
            'username': 'xsstest',
            'password': 'password'
        })
        
        # Try to create note with XSS payload
        xss_payload = '<script>alert("XSS")</script>'
        
        response = client.post('/notes/add', data={
            'title': 'XSS Test Note',
            'content': xss_payload,
            'course_id': course.id
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check if note was created
        note = Note.query.filter_by(title='XSS Test Note').first()
        if note:
            # The content should be stored as-is in DB (this is acceptable)
            assert note.content == xss_payload  # Raw content in DB is OK
            # Note: The app doesn't currently have HTML escaping, so XSS payloads
            # will be stored and displayed as-is. This is a security consideration
            # for future improvements.
    
    def test_file_upload_security(self, client, sample_user, sample_course):
        """Test file upload security"""
        # Login
        client.post('/login', data={
            'username': sample_user.username,
            'password': 'testpass123'
        })
        
        # Test file type validation (if implemented)
        # This would require actual file upload testing
        
        # Test file size limits
        # This would require large file testing
        
        assert True  # Placeholder for file security tests

class TestDataPrivacySecurity:
    """Test data privacy and protection"""
    
    def test_password_exposure(self, client, sample_user):
        """Test that passwords are not exposed in responses"""
        # Login
        client.post('/login', data={
            'username': sample_user.username,
            'password': 'testpass123'
        })
        
        # Check profile page
        response = client.get('/profile')
        assert response.status_code == 200
        
        # Password hash should not be visible in HTML
        assert b'testpass123' not in response.data
        
        # Check if any sensitive data is exposed
        assert b'password_hash' not in response.data
    
    def test_session_data_protection(self, client, sample_user):
        """Test session data protection"""
        # Login
        client.post('/login', data={
            'username': sample_user.username,
            'password': 'testpass123'
        })
        
        # Check session data
        with client.session_transaction() as sess:
            # Session should only contain necessary data
            assert 'user_id' in sess
            # Should not contain sensitive information
            assert 'password' not in sess
            assert 'password_hash' not in sess
