from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # user, admin, superadmin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assignee_uid', backref='assignee', lazy='dynamic')
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by_uid', backref='creator', lazy='dynamic')
    task_updates = db.relationship('TaskUpdate', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary, optionally including sensitive data"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data

    def has_role(self, role):
        """Check if user has a specific role or higher"""
        role_hierarchy = {'user': 1, 'admin': 2, 'superadmin': 3}
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(role, 0)
        return user_level >= required_level

    @staticmethod
    def create_user(username, email, password, display_name, role='user'):
        """Create a new user with hashed password"""
        user = User(
            username=username,
            email=email,
            display_name=display_name,
            role=role
        )
        user.set_password(password)
        return user

