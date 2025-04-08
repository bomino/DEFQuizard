import os
import json
import datetime
from sqlalchemy.orm import Session
from .connection import get_db_session, close_db_session, init_db
from .models import User, Question, Score, Setting
from ..data_manager import (
    USER_DB_FILE, QUESTIONS_FILE, SCORES_FILE, SETTINGS_FILE,
    read_json_file
)

def migrate_data():
    """
    Migrate data from JSON files to SQLite database
    
    Returns:
        dict: Dictionary with migration statistics
    """
    # Initialize the database
    init_db()
    
    # Statistics
    stats = {
        "users": 0,
        "questions": 0,
        "scores": 0,
        "settings": 0
    }
    
    session = get_db_session()
    try:
        # Migrate users
        if os.path.exists(USER_DB_FILE):
            users_data = read_json_file(USER_DB_FILE, {})
            for username, user_data in users_data.items():
                # Convert string timestamps to datetime objects
                created_at = None
                if "created_at" in user_data and user_data["created_at"]:
                    try:
                        created_at = datetime.datetime.strptime(user_data["created_at"], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        created_at = datetime.datetime.now()
                
                last_login = None
                if "last_login" in user_data and user_data["last_login"]:
                    try:
                        last_login = datetime.datetime.strptime(user_data["last_login"], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        last_login = None
                
                # Create user object
                user = User(
                    username=username,
                    password=user_data.get("password", ""),
                    name=user_data.get("name", ""),
                    role=user_data.get("role", "operator"),
                    created_at=created_at or datetime.datetime.now(),
                    last_login=last_login
                )
                session.add(user)
                stats["users"] += 1
        
        # Migrate questions
        if os.path.exists(QUESTIONS_FILE):
            questions_data = read_json_file(QUESTIONS_FILE, [])
            for q_data in questions_data:
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
                stats["questions"] += 1
        
        # Migrate scores
        if os.path.exists(SCORES_FILE):
            scores_data = read_json_file(SCORES_FILE, [])
            for score_data in scores_data:
                # Convert timestamp string to datetime
                timestamp = None
                if "timestamp" in score_data and score_data["timestamp"]:
                    try:
                        timestamp = datetime.datetime.strptime(score_data["timestamp"], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        timestamp = datetime.datetime.now()
                
                # Generate ID if not present
                score_id = score_data.get("id")
                if not score_id:
                    import hashlib
                    score_id = hashlib.md5(f"{score_data.get('username')}_{score_data.get('timestamp')}".encode()).hexdigest()[:10]
                
                # Create score object
                score = Score(
                    id=score_id,
                    username=score_data.get("username"),
                    score=score_data.get("score"),
                    max_score=score_data.get("max_score"),
                    percentage=score_data.get("percentage"),
                    passed=score_data.get("passed", False),
                    timestamp=timestamp or datetime.datetime.now(),
                    time_taken=score_data.get("time_taken"),
                    categories=score_data.get("categories")
                )
                session.add(score)
                stats["scores"] += 1
        
        # Migrate settings
        if os.path.exists(SETTINGS_FILE):
            settings_data = read_json_file(SETTINGS_FILE, {})
            for key, value in settings_data.items():
                setting = Setting(key=key, value=value)
                session.add(setting)
                stats["settings"] += 1
        
        # Commit all changes
        session.commit()
        return stats
    
    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        close_db_session()

def verify_migration():
    """
    Verify that the migration was successful by comparing counts
    
    Returns:
        dict: Dictionary with verification results
    """
    results = {
        "success": True,
        "users": {"json": 0, "db": 0},
        "questions": {"json": 0, "db": 0},
        "scores": {"json": 0, "db": 0},
        "settings": {"json": 0, "db": 0}
    }
    
    session = get_db_session()
    try:
        # Check users
        if os.path.exists(USER_DB_FILE):
            users_data = read_json_file(USER_DB_FILE, {})
            results["users"]["json"] = len(users_data)
        
        db_users_count = session.query(User).count()
        results["users"]["db"] = db_users_count
        
        # Check questions
        if os.path.exists(QUESTIONS_FILE):
            questions_data = read_json_file(QUESTIONS_FILE, [])
            results["questions"]["json"] = len(questions_data)
        
        db_questions_count = session.query(Question).count()
        results["questions"]["db"] = db_questions_count
        
        # Check scores
        if os.path.exists(SCORES_FILE):
            scores_data = read_json_file(SCORES_FILE, [])
            results["scores"]["json"] = len(scores_data)
        
        db_scores_count = session.query(Score).count()
        results["scores"]["db"] = db_scores_count
        
        # Check settings
        if os.path.exists(SETTINGS_FILE):
            settings_data = read_json_file(SETTINGS_FILE, {})
            results["settings"]["json"] = len(settings_data)
        
        db_settings_count = session.query(Setting).count()
        results["settings"]["db"] = db_settings_count
        
        # Determine success
        for entity in ["users", "questions", "scores", "settings"]:
            if results[entity]["json"] != results[entity]["db"]:
                results["success"] = False
        
        return results
    
    finally:
        close_db_session()

if __name__ == "__main__":
    # Run migration if executed directly
    print("Migrating data from JSON to SQLite...")
    stats = migrate_data()
    print(f"Migration complete. Migrated {stats['users']} users, {stats['questions']} questions, "
          f"{stats['scores']} scores, and {stats['settings']} settings.")
    
    # Verify migration
    verification = verify_migration()
    if verification["success"]:
        print("Migration verified successfully!")
    else:
        print("Migration verification failed. Please check the data.")
    
    print("Verification results:")
    for entity in ["users", "questions", "scores", "settings"]:
        print(f"  {entity.capitalize()}: JSON={verification[entity]['json']}, DB={verification[entity]['db']}")