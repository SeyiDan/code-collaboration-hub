from app import db
from datetime import datetime
import json

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    language = db.Column(db.String(50), default='python')
    content = db.Column(db.Text, default='# New Project\n\n# Start coding here')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, default=False)
    
    # Relationships
    collaborations = db.relationship('Collaboration', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def collaborator_count(self):
        return self.collaborations.count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'language': self.language,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_public': self.is_public,
            'collaborator_count': self.collaborator_count
        }
    
    def __repr__(self):
        return f'<Project {self.title}>'


class Collaboration(db.Model):
    __tablename__ = 'collaborations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    permission = db.Column(db.String(20), default='read')  # read, write, admin
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Collaboration user_id={self.user_id} project_id={self.project_id}>' 