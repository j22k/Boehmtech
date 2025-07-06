from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, in_progress, completed, cancelled
    priority = db.Column(db.String(10), nullable=False, default='medium')  # low, medium, high, urgent
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    assignee_uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by_uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    updates = db.relationship('TaskUpdate', backref='task', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Task {self.title}>'

    def to_dict(self, include_updates=False):
        """Convert task to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'assignee_uid': self.assignee_uid,
            'created_by_uid': self.created_by_uid,
            'assignee': self.assignee.to_dict() if self.assignee else None,
            'creator': self.creator.to_dict() if self.creator else None
        }
        
        if include_updates:
            data['updates'] = [update.to_dict() for update in self.updates.order_by(TaskUpdate.created_at.desc())]
            
        return data

    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.due_date
        return False

    def update_status(self, new_status):
        """Update task status and timestamp"""
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if new_status in valid_statuses:
            self.status = new_status
            self.updated_at = datetime.utcnow()
            return True
        return False

    @staticmethod
    def get_tasks_by_user(user_id, status=None):
        """Get tasks assigned to a specific user"""
        query = Task.query.filter_by(assignee_uid=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Task.due_date.asc()).all()

    @staticmethod
    def get_tasks_by_creator(creator_id, status=None):
        """Get tasks created by a specific user"""
        query = Task.query.filter_by(created_by_uid=creator_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Task.created_at.desc()).all()

    @staticmethod
    def get_overdue_tasks():
        """Get all overdue tasks"""
        return Task.query.filter(
            Task.due_date < datetime.utcnow(),
            Task.status.notin_(['completed', 'cancelled'])
        ).all()


class TaskUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    screenshot_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    updated_by_uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<TaskUpdate {self.id} for Task {self.task_id}>'

    def to_dict(self):
        """Convert task update to dictionary"""
        return {
            'id': self.id,
            'comment': self.comment,
            'url': self.url,
            'screenshot_path': self.screenshot_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'task_id': self.task_id,
            'updated_by_uid': self.updated_by_uid,
            'author': self.author.to_dict() if self.author else None
        }

