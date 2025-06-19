from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

@dataclass
class UserProfile:
    id: Optional[int] = None
    user_id: int = None
    profile_type: str = 'standard'
    preferences: Dict = None
    accessibility_settings: Dict = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = self.get_default_preferences()
        if self.accessibility_settings is None:
            self.accessibility_settings = self.get_default_accessibility()
    
    def get_default_preferences(self):
        defaults = {
            'standard': {
                'notification_style': 'standard',
                'reminder_frequency': 'normal',
                'daily_goal': 5,
                'preferred_times': ['09:00', '13:00', '18:00']
            },
            'adhd': {
                'notification_style': 'gentle_persistent',
                'reminder_frequency': 'frequent',
                'break_reminders': True,
                'hyperfocus_protection': True,
                'daily_goal': 3,
                'preferred_times': ['10:00', '14:00', '16:00', '19:00'],
                'dopamine_rewards': True,
                'visual_cues': True
            },
            'student': {
                'notification_style': 'academic',
                'study_mode': True,
                'pomodoro_enabled': True,
                'exam_mode': False,
                'daily_goal': 8,
                'preferred_times': ['08:00', '10:00', '14:00', '16:00', '20:00'],
                'assignment_tracking': True
            },
            'gentle': {
                'notification_style': 'soft',
                'reminder_frequency': 'minimal',
                'calm_colors': True,
                'meditation_breaks': True,
                'daily_goal': 2,
                'preferred_times': ['10:00', '15:00'],
                'positive_reinforcement': True
            },
            'senior': {
                'notification_style': 'clear_simple',
                'large_text': True,
                'high_contrast': True,
                'voice_reminders': True,
                'daily_goal': 3,
                'preferred_times': ['09:00', '12:00', '17:00'],
                'simple_interface': True,
                'medication_reminders': True
            }
        }
        return defaults.get(self.profile_type, defaults['standard'])
    
    def get_default_accessibility(self):
        return {
            'large_text': False,
            'high_contrast': False,
            'reduced_motion': False,
            'voice_enabled': False,
            'keyboard_navigation': False,
            'color_blind_friendly': False
        }

@dataclass
class FocusSession:
    id: Optional[int] = None
    user_id: int = None
    session_type: str = 'pomodoro'
    duration_minutes: int = 25
    break_duration: int = 5
    completed: bool = False
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    notes: Optional[str] = None

# Association tables for many-to-many relationships
reminder_shares = db.Table('reminder_shares',
    db.Column('reminder_id', db.Integer, db.ForeignKey('reminder.id'), primary_key=True),
    db.Column('user_email', db.String(120), db.ForeignKey('user.email'), primary_key=True)
)

note_shares = db.Table('note_shares',
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True),
    db.Column('user_email', db.String(120), db.ForeignKey('user.email'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    app_mode = db.Column(db.String(20), default='DEFAULT')
    
    # Relationships
    reminders = db.relationship('Reminder', backref='owner', lazy='dynamic')
    notes = db.relationship('Note', backref='creator', lazy='dynamic')
    
    # Reminders shared with this user
    shared_reminders = db.relationship('Reminder', 
        secondary=reminder_shares,
        backref=db.backref('shared_with', lazy='dynamic'),
        lazy='dynamic')
    
    # Notes shared with this user
    shared_notes = db.relationship('Note',
        secondary=note_shares,
        backref=db.backref('shared_with', lazy='dynamic'),
        lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Reminder {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'owner_email': self.owner.email if self.owner else None,
            'shared_with': [user.email for user in self.shared_with]
        }

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Note {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'creator_email': self.creator.email if self.creator else None,
            'shared_with': [user.email for user in self.shared_with]
        }
