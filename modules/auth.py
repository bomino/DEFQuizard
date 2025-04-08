import hashlib
import datetime
from .data_manager import load_users, save_users

# Check if database module is available
try:
    from .database.operations import get_user, save_user, update_user_login
    from .database.connection import get_db_session, close_db_session
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False

def hash_password(password):
    """
    Hash a password using SHA-256
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    """
    Authenticate a user
    
    Args:
        username (str): Username
        password (str): Plain text password
        
    Returns:
        tuple: (is_authenticated, role, name)
    """
    if USE_DATABASE:
        # Use database for authentication
        session = get_db_session()
        try:
            # Get user from database
            user = session.query(User).filter_by(username=username).first()
            
            if user and user.password == hash_password(password):
                # Update last login time
                user.last_login = datetime.datetime.now()
                session.commit()
                
                return True, user.role, user.name
            
            return False, None, None
        finally:
            close_db_session()
    else:
        # Use JSON file for authentication
        users = load_users()
        if username in users and users[username]["password"] == hash_password(password):
            # Update last login time (in-memory only)
            if "last_login" in users[username]:
                users[username]["last_login"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_users(users)
            
            return True, users[username]["role"], users[username]["name"]
        
        return False, None, None

def add_user(username, password, name, role="operator"):
    """
    Add a new user
    
    Args:
        username (str): Username
        password (str): Plain text password
        name (str): User's full name
        role (str): User role (default: "operator")
        
    Returns:
        tuple: (success, message)
    """
    if USE_DATABASE:
        # Use database to add user
        try:
            # Check if user exists
            existing_user = get_user(username)
            if existing_user:
                return False, "Username already exists"
            
            # Create user data
            user_data = {
                "password": hash_password(password),
                "name": name,
                "role": role,
                "created_at": datetime.datetime.now(),
                "last_login": None
            }
            
            # Save user
            if save_user(username, user_data):
                return True, "User added successfully"
            else:
                return False, "Error saving user"
        except Exception as e:
            return False, f"Error: {str(e)}"
    else:
        # Use JSON file to add user
        users = load_users()
        if username in users:
            return False, "Username already exists"
        
        users[username] = {
            "password": hash_password(password),
            "role": role,
            "name": name,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        }
        
        if save_users(users):
            return True, "User added successfully"
        else:
            return False, "Error saving user"