import os
import json
import datetime
import hashlib
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from .connection import get_db_session, close_db_session
from .models import User, Question, Score, Setting
from ..auth import hash_password  # Import hash_password from auth.py

# Create backup directory
BACKUP_DIR = os.path.join("data", "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

# User operations
def get_all_users():
    """
    Get all users from the database
    
    Returns:
        dict: Dictionary with username as key and user info as value
    """
    session = get_db_session()
    try:
        users = session.query(User).all()
        users_dict = {user.username: user.to_dict() for user in users}
        return users_dict
    finally:
        close_db_session()

def get_user(username):
    """
    Get a specific user by username
    
    Args:
        username (str): Username to look up
        
    Returns:
        dict: User information or None if not found
    """
    session = get_db_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        return user.to_dict() if user else None
    finally:
        close_db_session()

def save_user(username, user_data):
    """
    Save a user to the database
    
    Args:
        username (str): Username
        user_data (dict): User data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        # Check if user exists
        user = session.query(User).filter_by(username=username).first()
        
        if user:
            # Update existing user
            for key, value in user_data.items():
                setattr(user, key, value)
        else:
            # Create new user
            user = User(
                username=username,
                password=user_data.get("password", ""),
                name=user_data.get("name", ""),
                role=user_data.get("role", "operator"),
                created_at=datetime.datetime.now(),
                last_login=None
            )
            session.add(user)
        
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()

def delete_user(username):
    """
    Delete a user from the database
    
    Args:
        username (str): Username to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user:
            session.delete(user)
            session.commit()
            return True
        return False
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()

def update_user_login(username):
    """
    Update a user's last login timestamp
    
    Args:
        username (str): Username to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user:
            user.last_login = datetime.datetime.now()
            session.commit()
            return True
        return False
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()

# Question operations
def get_all_questions():
    """
    Get all questions from the database
    
    Returns:
        list: List of question dictionaries
    """
    session = get_db_session()
    try:
        questions = session.query(Question).all()
        return [question.to_dict() for question in questions]
    finally:
        close_db_session()

def get_question(question_id):
    """
    Get a specific question by ID
    
    Args:
        question_id (int): Question ID to look up
        
    Returns:
        dict: Question information or None if not found
    """
    session = get_db_session()
    try:
        question = session.query(Question).filter_by(id=question_id).first()
        return question.to_dict() if question else None
    finally:
        close_db_session()

def save_questions(questions_list):
    """
    Save a list of questions to the database
    
    Args:
        questions_list (list): List of question dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        # Clear existing questions
        session.query(Question).delete()
        
        # Add new questions
        for q_data in questions_list:
            question = Question(
                id=q_data.get("id"),
                question=q_data.get("question"),
                options=q_data.get("options"),
                answer=q_data.get("answer"),
                explanation=q_data.get("explanation"),
                category=q_data.get("category", "General"),
                difficulty=q_data.get("difficulty", "Intermediate")
            )
            session.add(question)
        
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()

def add_question(question_data):
    """
    Add a single question to the database
    
    Args:
        question_data (dict): Question data to add
        
    Returns:
        int: ID of the new question or None if failed
    """
    session = get_db_session()
    try:
        # Find the highest existing ID
        max_id = session.query(sa.func.max(Question.id)).scalar() or 0
        new_id = max_id + 1
        
        # Create new question
        question = Question(
            id=new_id,
            question=question_data.get("question"),
            options=question_data.get("options"),
            answer=question_data.get("answer"),
            explanation=question_data.get("explanation"),
            category=question_data.get("category", "General"),
            difficulty=question_data.get("difficulty", "Intermediate")
        )
        session.add(question)
        session.commit()
        return new_id
    except SQLAlchemyError:
        session.rollback()
        return None
    finally:
        close_db_session()

def update_question(question_id, question_data):
    """
    Update a question in the database
    
    Args:
        question_id (int): ID of the question to update
        question_data (dict): Updated question data
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        question = session.query(Question).filter_by(id=question_id).first()
        if question:
            # Update fields
            for key, value in question_data.items():
                if hasattr(question, key):
                    setattr(question, key, value)
            
            session.commit()
            return True
        return False
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()

def delete_question(question_id):
    """
    Delete a question from the database
    
    Args:
        question_id (int): ID of the question to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        question = session.query(Question).filter_by(id=question_id).first()
        if question:
            session.delete(question)
            session.commit()
            return True
        return False
    finally:
        close_db_session()

# Score operations
def get_all_scores():
    """
    Get all scores from the database
    
    Returns:
        list: List of score dictionaries
    """
    session = get_db_session()
    try:
        scores = session.query(Score).order_by(Score.timestamp.desc()).all()
        return [score.to_dict() for score in scores]
    finally:
        close_db_session()

def get_user_scores(username, limit=None):
    """
    Get scores for a specific user
    
    Args:
        username (str): Username to get scores for
        limit (int, optional): Limit the number of scores returned
        
    Returns:
        list: List of score dictionaries for the user
    """
    session = get_db_session()
    try:
        query = session.query(Score).filter_by(username=username).order_by(Score.timestamp.desc())
        
        if limit and isinstance(limit, int) and limit > 0:
            query = query.limit(limit)
        
        scores = query.all()
        return [score.to_dict() for score in scores]
    finally:
        close_db_session()

def save_quiz_score(username, score, max_score, categories=None, time_taken=None):
    """
    Save a quiz score to the database
    
    Args:
        username (str): Username
        score (int): Number of correct answers
        max_score (int): Total number of questions
        categories (dict, optional): Category-wise performance
        time_taken (float, optional): Time taken to complete the quiz in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        # Calculate percentage
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        # Generate a unique ID for the quiz attempt
        quiz_id = hashlib.md5(f"{username}_{datetime.datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        # Get passing score from settings
        settings = get_all_settings()
        passing_score = settings.get("passing_score", 80)
        
        # Create new score entry
        score_entry = Score(
            id=quiz_id,
            username=username,
            score=score,
            max_score=max_score,
            percentage=percentage,
            passed=percentage >= passing_score,
            timestamp=datetime.datetime.now(),
            time_taken=time_taken,
            categories=categories
        )
        
        session.add(score_entry)
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()

def clear_all_scores():
    """
    Delete all scores from the database
    
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        session.query(Score).delete()
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()

def clear_user_scores(username):
    """
    Delete all scores for a specific user
    
    Args:
        username (str): Username to clear scores for
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        session.query(Score).filter_by(username=username).delete()
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()

# Settings operations
def get_all_settings():
    """
    Get all application settings
    
    Returns:
        dict: Dictionary of all settings
    """
    session = get_db_session()
    try:
        settings = {}
        for setting in session.query(Setting).all():
            settings[setting.key] = setting.value
        
        # Return default settings if none exist
        if not settings:
            default_settings = {
                "company_name": "Your Company",
                "passing_score": 80,
                "certificate_validity_days": 365,
                "enable_self_registration": True,
                "default_quiz_time_limit": 0,
                "default_quiz_questions": 10,
                "track_categories": True,
                "require_reset_password": True,
                "password_expiry_days": 90,
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return default_settings
        
        return settings
    finally:
        close_db_session()

def save_settings(settings_dict):
    """
    Save application settings
    
    Args:
        settings_dict (dict): Dictionary of settings to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        # Update timestamp
        settings_dict["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Delete existing settings
        session.query(Setting).delete()
        
        # Add new settings
        for key, value in settings_dict.items():
            setting = Setting(key=key, value=value)
            session.add(setting)
        
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()

def get_setting(key, default=None):
    """
    Get a specific setting value
    
    Args:
        key (str): Setting key
        default: Default value if setting doesn't exist
        
    Returns:
        The setting value or default if not found
    """
    session = get_db_session()
    try:
        setting = session.query(Setting).filter_by(key=key).first()
        return setting.value if setting else default
    finally:
        close_db_session()

def set_setting(key, value):
    """
    Set a specific setting value
    
    Args:
        key (str): Setting key
        value: Setting value
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_db_session()
    try:
        setting = session.query(Setting).filter_by(key=key).first()
        
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            session.add(setting)
        
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        close_db_session()