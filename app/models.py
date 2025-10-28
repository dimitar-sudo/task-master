from app import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Personal')
    deadline = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.id}: {self.content[:30]}>'
    
    def is_overdue(self):
        if self.deadline and not self.completed:
            return datetime.utcnow() > self.deadline
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'category': self.category,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'completed': self.completed,
            'date_created': self.date_created.isoformat(),
            'is_overdue': self.is_overdue()
        }
