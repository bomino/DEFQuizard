import datetime
import os
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json

Base = declarative_base()

class User(Base):
    """User model for authentication and profile information"""
    __tablename__ = 'users'
    
    username = sa.Column(sa.String, primary_key=True)
    password = sa.Column(sa.String, nullable=False)  # Hashed password
    name = sa.Column(sa.String, nullable=False)
    role = sa.Column(sa.String, nullable=False, default="operator")
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.now)
    last_login = sa.Column(sa.DateTime, nullable=True)
    
    # Relationships
    scores = relationship("Score", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary format for compatibility with existing code"""
        return {
            "username": self.username,
            "password": self.password,
            "name": self.name,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S") if self.last_login else None
        }

class Question(Base):
    """Question model for quiz questions"""
    __tablename__ = 'questions'
    
    id = sa.Column(sa.Integer, primary_key=True)
    question = sa.Column(sa.String, nullable=False)
    options = sa.Column(sa.JSON, nullable=False)  # Store options as JSON array
    answer = sa.Column(sa.Integer, nullable=False)  # Index of the correct answer
    explanation = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String, nullable=False, default="General")
    difficulty = sa.Column(sa.String, nullable=False, default="Intermediate")
    
    def to_dict(self):
        """Convert to dictionary format for compatibility with existing code"""
        return {
            "id": self.id,
            "question": self.question,
            "options": self.options,
            "answer": self.answer,
            "explanation": self.explanation,
            "category": self.category,
            "difficulty": self.difficulty
        }

class Score(Base):
    """Score model for quiz results"""
    __tablename__ = 'scores'
    
    id = sa.Column(sa.String, primary_key=True)  # Unique ID for the quiz attempt
    username = sa.Column(sa.String, sa.ForeignKey("users.username"), nullable=False)
    score = sa.Column(sa.Integer, nullable=False)  # Number of correct answers
    max_score = sa.Column(sa.Integer, nullable=False)  # Total number of questions
    percentage = sa.Column(sa.Float, nullable=False)  # Score percentage
    passed = sa.Column(sa.Boolean, nullable=False, default=False)  # Whether the score is passing
    timestamp = sa.Column(sa.DateTime, default=datetime.datetime.now)
    time_taken = sa.Column(sa.Integer, nullable=True)  # Time in seconds to complete the quiz
    categories = sa.Column(sa.JSON, nullable=True)  # Store category performance as JSON
    
    # Relationships
    user = relationship("User", back_populates="scores")
    
    def to_dict(self):
        """Convert to dictionary format for compatibility with existing code"""
        return {
            "id": self.id,
            "username": self.username,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "passed": self.passed,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
            "time_taken": self.time_taken,
            "categories": self.categories
        }

class Setting(Base):
    """Application settings model"""
    __tablename__ = 'settings'
    
    key = sa.Column(sa.String, primary_key=True)
    value = sa.Column(sa.JSON, nullable=True)  # Store value as JSON to support different types
    updated_at = sa.Column(sa.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    @classmethod
    def get_all_settings(cls, session):
        """Get all settings as a dictionary"""
        settings = {}
        for setting in session.query(cls).all():
            settings[setting.key] = setting.value
        return settings