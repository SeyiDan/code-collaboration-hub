import unittest
from app import create_app, db
from app.models.user import User
from app.models.project import Project, Collaboration

class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_password_setter(self):
        u = User(username='test', email='test@example.com')
        u.set_password('cat')
        self.assertTrue(u.password_hash is not None)
        
    def test_no_password_getter(self):
        u = User(username='test', email='test@example.com')
        u.set_password('cat')
        with self.assertRaises(AttributeError):
            u.password
            
    def test_password_verification(self):
        u = User(username='test', email='test@example.com')
        u.set_password('cat')
        self.assertTrue(u.check_password('cat'))
        self.assertFalse(u.check_password('dog'))
        
    def test_project_relationship(self):
        u = User(username='test', email='test@example.com')
        u.set_password('cat')
        db.session.add(u)
        db.session.commit()
        
        p = Project(title='Test Project', owner_id=u.id)
        db.session.add(p)
        db.session.commit()
        
        self.assertEqual(u.projects.count(), 1)
        self.assertEqual(u.projects.first().title, 'Test Project')

class TestProjectModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(username='test', email='test@example.com')
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_project_creation(self):
        p = Project(title='Test Project', 
                   description='This is a test project',
                   language='python',
                   owner_id=self.user.id)
        db.session.add(p)
        db.session.commit()
        
        self.assertEqual(Project.query.count(), 1)
        self.assertEqual(Project.query.first().title, 'Test Project')
        self.assertEqual(Project.query.first().language, 'python')
        
    def test_collaboration(self):
        # Create a second user
        user2 = User(username='collaborator', email='collab@example.com')
        user2.set_password('password')
        db.session.add(user2)
        
        # Create a project
        p = Project(title='Collab Project', owner_id=self.user.id)
        db.session.add(p)
        db.session.commit()
        
        # Add collaboration
        collab = Collaboration(user_id=user2.id, project_id=p.id, permission='write')
        db.session.add(collab)
        db.session.commit()
        
        # Check relationships
        self.assertEqual(p.collaborations.count(), 1)
        self.assertEqual(p.collaborations.first().user_id, user2.id)
        self.assertEqual(user2.collaborations.first().project_id, p.id)
        self.assertEqual(p.collaborator_count, 1)
        
if __name__ == '__main__':
    unittest.main() 