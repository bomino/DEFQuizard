import os
import json
import datetime
import hashlib

# File paths for backward compatibility
DATA_DIR = "data"
USER_DB_FILE = os.path.join(DATA_DIR, "users.json")
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
USER_SETTINGS_DIR = os.path.join(DATA_DIR, "user_settings")
ASSETS_DIR = "assets"
LOGO_PATH = os.path.join(ASSETS_DIR, "XLC1.png")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# Import database operations - using a try/except to handle circular imports
try:
    from .database.operations import (
        get_all_users, get_user, save_user, delete_user,
        get_all_questions, get_question, save_questions, add_question, update_question, delete_question,
        get_all_scores, get_user_scores, save_quiz_score, clear_all_scores, clear_user_scores,
        get_all_settings, save_settings, get_setting, set_setting
    )
    
    # Flag to indicate whether we're using the database
    USE_DATABASE = True
except ImportError:
    # If database module is not available, fall back to JSON files
    USE_DATABASE = False

# File utility functions for backward compatibility and migration
def read_json_file(file_path, default=None):
    """
    Read JSON from a file with error handling
    
    Args:
        file_path (str): Path to the JSON file
        default: Default value to return if file doesn't exist or has errors
        
    Returns:
        The parsed JSON data or the default value
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return default
    except json.JSONDecodeError:
        # Create a backup of the corrupted file
        if os.path.exists(file_path):
            backup_file = os.path.join(
                BACKUP_DIR, 
                f"{os.path.basename(file_path)}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            with open(file_path, "r") as src, open(backup_file, "w") as dst:
                dst.write(src.read())
        
        return default

def write_json_file(file_path, data):
    """
    Write JSON to a file with error handling and atomic writing
    
    Args:
        file_path (str): Path to save the JSON file
        data: Data to save as JSON
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write to a temporary file first
        temp_file = f"{file_path}.tmp"
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)
        
        # Replace the original file (atomic operation)
        if os.path.exists(file_path):
            # Create backup
            backup_file = os.path.join(
                BACKUP_DIR, 
                f"{os.path.basename(file_path)}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            with open(file_path, "r") as src, open(backup_file, "w") as dst:
                dst.write(src.read())
        
        # Rename temp file to target file
        os.replace(temp_file, file_path)
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False

# Create necessary directories
def ensure_directories():
    """Create all required directories for the application"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(USER_SETTINGS_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

# Initialize data files if they don't exist
def initialize_data_files():
    """Initialize default data files if they don't exist"""
    global USE_DATABASE
    if USE_DATABASE:
        # Initialize the database schema and default data
        try:
            from .database.connection import init_db
            from .database.migrate import migrate_data
            
            # Initialize the database
            init_db()
            
            # Check if we need to migrate existing data
            from .database.models import User
            from .database.connection import get_db_session, close_db_session
            
            session = get_db_session()
            admin_exists = False
            try:
                # Check if admin user exists in database
                admin_exists = session.query(User).filter_by(username="admin").first() is not None
            finally:
                close_db_session()
            
            # If admin doesn't exist but JSON files do, migrate data
            if not admin_exists and (
                os.path.exists(USER_DB_FILE) or 
                os.path.exists(QUESTIONS_FILE) or 
                os.path.exists(SCORES_FILE) or 
                os.path.exists(SETTINGS_FILE)
            ):
                migrate_data()
            elif not admin_exists:
                # If no admin user and no JSON files, create default admin
                from .auth import hash_password
                
                default_users = {
                    "admin": {
                        "password": hash_password("admin123"),
                        "role": "admin",
                        "name": "Admin User",
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "last_login": None
                    }
                }
                
                # Create admin user in database
                save_user("admin", default_users["admin"])
                
                # Create default settings
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
                save_settings(default_settings)
                
                # Create default questions
                default_questions = [
                    {
                        "id": 1,
                        "question": "What should you do before operating a forklift?",
                        "options": [
                            "Check fuel only", 
                            "Full pre-shift inspection", 
                            "Test horn", 
                            "Load immediately"
                        ],
                        "answer": 1,
                        "explanation": "OSHA requires a pre-shift inspection for safety.",
                        "category": "Safety",
                        "difficulty": "Basic"
                    },
                    {
                        "id": 2,
                        "question": "What is the proper way to approach an intersection with a forklift?",
                        "options": [
                            "Speed up to get through quickly", 
                            "Honk and proceed without stopping", 
                            "Slow down, honk, and look both ways", 
                            "Always come to a complete stop"
                        ],
                        "answer": 2,
                        "explanation": "Slowing down, honking, and looking both ways ensures visibility and warns pedestrians of your approach.",
                        "category": "Operation",
                        "difficulty": "Intermediate"
                    },
                    {
                        "id": 3,
                        "question": "When parking a forklift at the end of a shift, you should:",
                        "options": [
                            "Leave the forks raised for easy access next shift", 
                            "Park anywhere convenient", 
                            "Lower the forks to the ground, set the brake, and turn off the engine", 
                            "Leave the key in the ignition for the next operator"
                        ],
                        "answer": 2,
                        "explanation": "Lowering forks, setting the brake, and turning off the engine are essential safety protocols for parking.",
                        "category": "Safety",
                        "difficulty": "Basic"
                    }
                ]
                save_questions(default_questions)
        
        except ImportError:
            # If database module is not available, fall back to file initialization
            USE_DATABASE = False
            initialize_json_files()
    else:
        # Use JSON files
        initialize_json_files()

def initialize_json_files():
    """Initialize JSON data files if they don't exist (legacy method)"""
    # Import hash_password here to avoid circular imports
    from .auth import hash_password
    
    # Default admin user
    if not os.path.exists(USER_DB_FILE):
        default_users = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin",
                "name": "Admin User",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": None
            }
        }
        write_json_file(USER_DB_FILE, default_users)
    
    # Default questions
    if not os.path.exists(QUESTIONS_FILE):
        default_questions = [
            {
                "id": 1,
                "question": "What should you do before operating a forklift?",
                "options": [
                    "Check fuel only", 
                    "Full pre-shift inspection", 
                    "Test horn", 
                    "Load immediately"
                ],
                "answer": 1,
                "explanation": "OSHA requires a pre-shift inspection for safety.",
                "category": "Safety",
                "difficulty": "Basic"
            },
            {
                "id": 2,
                "question": "What is the proper way to approach an intersection with a forklift?",
                "options": [
                    "Speed up to get through quickly", 
                    "Honk and proceed without stopping", 
                    "Slow down, honk, and look both ways", 
                    "Always come to a complete stop"
                ],
                "answer": 2,
                "explanation": "Slowing down, honking, and looking both ways ensures visibility and warns pedestrians of your approach.",
                "category": "Operation",
                "difficulty": "Intermediate"
            },
            {
                "id": 3,
                "question": "When parking a forklift at the end of a shift, you should:",
                "options": [
                    "Leave the forks raised for easy access next shift", 
                    "Park anywhere convenient", 
                    "Lower the forks to the ground, set the brake, and turn off the engine", 
                    "Leave the key in the ignition for the next operator"
                ],
                "answer": 2,
                "explanation": "Lowering forks, setting the brake, and turning off the engine are essential safety protocols for parking.",
                "category": "Safety",
                "difficulty": "Basic"
            }
        ]
        write_json_file(QUESTIONS_FILE, default_questions)
    
    # Empty scores file
    if not os.path.exists(SCORES_FILE):
        write_json_file(SCORES_FILE, [])
    
    # Default application settings
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "company_name": "Your Company",
            "passing_score": 80,
            "certificate_validity_days": 365,
            "enable_self_registration": True,
            "default_quiz_time_limit": 0,  # 0 means no time limit
            "default_quiz_questions": 10,
            "track_categories": True,
            "require_reset_password": True,
            "password_expiry_days": 90,
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        write_json_file(SETTINGS_FILE, default_settings)

# Load data functions 
# These functions now dispatch to either database or JSON file methods
def load_users():
    """Load users from database or JSON file"""
    if USE_DATABASE:
        return get_all_users()
    else:
        return read_json_file(USER_DB_FILE, {})

def load_questions():
    """Load questions from database or JSON file"""
    if USE_DATABASE:
        return get_all_questions()
    else:
        return read_json_file(QUESTIONS_FILE, [])

def load_scores():
    """Load scores from database or JSON file"""
    if USE_DATABASE:
        return get_all_scores()
    else:
        return read_json_file(SCORES_FILE, [])

def load_settings():
    """Load application settings from database or JSON file"""
    if USE_DATABASE:
        return get_all_settings()
    else:
        return read_json_file(SETTINGS_FILE, {})

def load_user_settings(username):
    """Load user-specific settings"""
    # User settings are still file-based for now
    user_settings_file = os.path.join(USER_SETTINGS_DIR, f"{username}.json")
    return read_json_file(user_settings_file, {})

# Save data functions
def save_users(users):
    """Save users to database or JSON file"""
    if USE_DATABASE:
        # Database requires saving each user separately
        success = True
        for username, user_data in users.items():
            if not save_user(username, user_data):
                success = False
        return success
    else:
        return write_json_file(USER_DB_FILE, users)

def save_questions(questions):
    """Save questions to database or JSON file"""
    if USE_DATABASE:
        return save_questions(questions)
    else:
        return write_json_file(QUESTIONS_FILE, questions)

def save_scores(scores):
    """Save scores to database or JSON file"""
    if USE_DATABASE:
        # This is complicated because we'd need to clear and readd all scores
        # Instead, we'll just write to the JSON file for backward compatibility
        return write_json_file(SCORES_FILE, scores)
    else:
        return write_json_file(SCORES_FILE, scores)

def save_settings(settings):
    """Save application settings to database or JSON file"""
    if USE_DATABASE:
        return save_settings(settings)
    else:
        return write_json_file(SETTINGS_FILE, settings)

def save_user_settings(username, settings):
    """Save user-specific settings"""
    # User settings are still file-based for now
    user_settings_file = os.path.join(USER_SETTINGS_DIR, f"{username}.json")
    return write_json_file(user_settings_file, settings)

# The rest of the functions can remain largely the same, calling either
# database or file-based storage based on the USE_DATABASE flag

# Quiz score functions
def save_quiz_score(username, score, max_score, categories=None, time_taken=None):
    """
    Save quiz score with enhanced details
    
    Args:
        username (str): Username of the user
        score (int): Number of correct answers
        max_score (int): Total number of questions
        categories (dict, optional): Category-wise performance
        time_taken (float, optional): Time taken to complete the quiz in seconds
    """
    if USE_DATABASE:
        return save_quiz_score(username, score, max_score, categories, time_taken)
    else:
        scores = load_scores()
        
        # Calculate percentage
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        # Generate a unique ID for the quiz attempt
        quiz_id = hashlib.md5(f"{username}_{datetime.datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        # Create score data with enhanced details
        score_data = {
            "id": quiz_id,
            "username": username,
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "passed": percentage >= load_settings().get("passing_score", 80),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "time_taken": time_taken  # Time in seconds if timed quiz
        }
        
        # Add category-wise performance if provided
        if categories:
            score_data["categories"] = categories
        
        scores.append(score_data)
        return write_json_file(SCORES_FILE, scores)

def get_user_scores(username, limit=None):
    """
    Get scores for a specific user
    
    Args:
        username (str): Username to get scores for
        limit (int, optional): Limit the number of scores returned
        
    Returns:
        list: List of score objects for the user, sorted by timestamp
    """
    if USE_DATABASE:
        return get_user_scores(username, limit)
    else:
        scores = load_scores()
        user_scores = [s for s in scores if s["username"] == username]
        
        # Sort by timestamp (newest first)
        user_scores.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit the number of results if specified
        if limit and isinstance(limit, int) and limit > 0:
            user_scores = user_scores[:limit]
            
        return user_scores

def get_score_statistics(username=None):
    """
    Get statistics on quiz scores
    
    Args:
        username (str, optional): If provided, get stats for this user only
        
    Returns:
        dict: Dictionary with score statistics
    """
    scores = load_scores()
    
    # Filter by username if provided
    if username:
        scores = [s for s in scores if s["username"] == username]
    
    if not scores:
        return {
            "total_attempts": 0,
            "avg_score": 0,
            "pass_rate": 0,
            "highest_score": 0,
            "lowest_score": 0,
            "recent_trend": "No data"
        }
    
    # Calculate statistics
    total_attempts = len(scores)
    avg_score = sum(s.get("percentage", 0) for s in scores) / total_attempts if total_attempts > 0 else 0
    passing_score = load_settings().get("passing_score", 80)
    passed_count = sum(1 for s in scores if s.get("percentage", 0) >= passing_score)
    pass_rate = (passed_count / total_attempts) * 100 if total_attempts > 0 else 0
    highest_score = max(s.get("percentage", 0) for s in scores) if scores else 0
    lowest_score = min(s.get("percentage", 0) for s in scores) if scores else 0
    
    # Calculate recent trend (last 5 scores)
    recent_scores = sorted(scores, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
    if len(recent_scores) >= 2:
        oldest_recent = recent_scores[-1].get("percentage", 0)
        newest_recent = recent_scores[0].get("percentage", 0)
        if newest_recent > oldest_recent:
            recent_trend = "Improving"
        elif newest_recent < oldest_recent:
            recent_trend = "Declining"
        else:
            recent_trend = "Stable"
    else:
        recent_trend = "Not enough data"
    
    return {
        "total_attempts": total_attempts,
        "avg_score": avg_score,
        "pass_rate": pass_rate,
        "highest_score": highest_score,
        "lowest_score": lowest_score,
        "recent_trend": recent_trend
    }

def get_category_statistics():
    """
    Get statistics on performance by category
    
    Returns:
        dict: Dictionary with category statistics
    """
    scores = load_scores()
    categories = {}
    
    for score in scores:
        if "categories" in score:
            for category, data in score["categories"].items():
                if category not in categories:
                    categories[category] = {
                        "total_questions": 0,
                        "correct_answers": 0
                    }
                
                categories[category]["total_questions"] += data["total"]
                categories[category]["correct_answers"] += data["correct"]
    
    # Calculate percentages
    for category in categories:
        total = categories[category]["total_questions"]
        correct = categories[category]["correct_answers"]
        categories[category]["percentage"] = (correct / total) * 100 if total > 0 else 0
    
    return categories

def generate_certificate_id(username, score, date):
    """
    Generate a unique certificate ID
    
    Args:
        username (str): Username
        score (float): Score percentage
        date (str): Date of completion
        
    Returns:
        str: Unique certificate ID
    """
    cert_string = f"{username}_{score}_{date}"
    return hashlib.md5(cert_string.encode()).hexdigest()[:8].upper()

def verify_certificate(cert_id):
    """
    Verify if a certificate ID is valid
    
    Args:
        cert_id (str): Certificate ID to verify
        
    Returns:
        dict or None: Certificate data if valid, None otherwise
    """
    scores = load_scores()
    
    for score in scores:
        if score.get("id") == cert_id or score.get("certificate_id") == cert_id:
            return {
                "valid": True,
                "username": score.get("username"),
                "score": score.get("percentage"),
                "date": score.get("timestamp"),
                "passed": score.get("passed", False)
            }
    
    return None

# These functions use the database functions if available
def clear_all_scores():
    """
    Clear all quiz scores from the system
    """
    if USE_DATABASE:
        return clear_all_scores()
    else:
        return write_json_file(SCORES_FILE, [])

def clear_user_scores(username):
    """
    Clear quiz scores for a specific user
    
    Args:
        username (str): Username of the user whose scores will be deleted
    
    Returns:
        bool: True if successful, False otherwise
    """
    if USE_DATABASE:
        return clear_user_scores(username)
    else:
        scores = load_scores()
        filtered_scores = [s for s in scores if s["username"] != username]
        return write_json_file(SCORES_FILE, filtered_scores)
