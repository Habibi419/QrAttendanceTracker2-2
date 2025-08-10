from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):
    """Admin user model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f"<Admin {self.username}>"

class Session(db.Model):
    """Model for attendance sessions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    token = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)  # When the QR code expires
    is_active = db.Column(db.Boolean, default=True)  # Is the session still active
    attendances = db.relationship('Attendance', backref='session', lazy=True)
    
    def is_expired(self):
        """Check if the session has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<Session {self.name}>"

class Attendance(db.Model):
    """Model for attendance records"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    student_id = db.Column(db.String(50), nullable=False)
    reg_number = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 addresses can be longer
    
    # Ensure a student can only mark attendance once per session
    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='uix_session_student'),
    )
    
    def __repr__(self):
        return f"<Attendance {self.name} ({self.student_id})>"
