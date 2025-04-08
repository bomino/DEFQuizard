# Forklift Operator Training Application
# Developer Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [Module Descriptions](#module-descriptions)
5. [Data Flow](#data-flow)
6. [Authentication System](#authentication-system)
7. [Quiz System](#quiz-system)
8. [Certificate Generation](#certificate-generation)
9. [SQLite Migration](#sqlite-migration)
10. [Development Guidelines](#development-guidelines)
11. [Testing](#testing)
12. [Deployment](#deployment)
13. [Common Issues](#common-issues)
14. [Author & Maintenance] (#Author & Maintenance Contact Information)

## Overview

The Forklift Operator Training Application is a web-based system for training and certifying forklift operators according to OSHA standards. It provides interactive quizzes, personalized dashboards, certificate generation, and comprehensive admin tools.

### Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Data Storage**: SQLite (with JSON fallback)
- **ORM**: SQLAlchemy
- **Authentication**: Custom implementation with SHA-256 hashing

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
forklift_app/
│
├── app.py                 # Main application entry point
├── migrate_to_sqlite.py   # SQLite migration utility
│
├── modules/               # Core application modules
│   ├── auth.py            # Authentication logic
│   ├── data_manager.py    # Data access layer
│   ├── ui.py              # UI components
│   ├── certificate.py     # Certificate generation
│   ├── utils.py           # Utility functions
│   │
│   ├── database/          # SQLite database modules
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── connection.py  # Connection management
│   │   ├── operations.py  # Database operations
│   │   └── migrate.py     # Migration utilities
│   │
│   └── pages/             # Page modules
│       ├── login.py       # Login page
│       ├── dashboard.py   # Dashboard page
│       ├── quiz.py        # Quiz page
│       ├── scores.py      # Scores page
│       ├── admin.py       # Admin panel
│       └── admin_db.py    # Database management interface
│
└── data/                  # Data storage
    ├── forklift_training.db # SQLite database
    ├── backups/           # Automatic backups
    └── legacy/            # Legacy JSON files (optional)
```

## Database Schema

### Entity-Relationship Diagram

```
+------------------+       +--------------------+
|      User        |       |      Question      |
+------------------+       +--------------------+
| username (PK)    |       | id (PK)            |
| password         |       | question           |
| name             |       | options (JSON)     |
| role             |       | answer             |
| created_at       |       | explanation        |
| last_login       |       | category           |
+------------------+       | difficulty         |
        |                  +--------------------+
        |
        |
        |                  +--------------------+
        +----------------->|       Score        |
                           +--------------------+
                           | id (PK)            |
                           | username (FK)      |
                           | score              |
                           | max_score          |
                           | percentage         |
                           | passed             |
                           | timestamp          |
                           | time_taken         |
                           | categories (JSON)  |
                           +--------------------+
                           
+------------------+       
|     Setting      |       
+------------------+       
| key (PK)         |       
| value (JSON)     |       
| updated_at       |       
+------------------+       
```

### SQLAlchemy Models

The database models are defined in `modules/database/models.py` using SQLAlchemy ORM:

#### User Model

```python
class User(Base):
    __tablename__ = 'users'
    
    username = sa.Column(sa.String, primary_key=True)
    password = sa.Column(sa.String, nullable=False)  # Hashed password
    name = sa.Column(sa.String, nullable=False)
    role = sa.Column(sa.String, nullable=False, default="operator")
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.now)
    last_login = sa.Column(sa.DateTime, nullable=True)
    
    # Relationships
    scores = relationship("Score", back_populates="user", cascade="all, delete-orphan")
```

#### Question Model

```python
class Question(Base):
    __tablename__ = 'questions'
    
    id = sa.Column(sa.Integer, primary_key=True)
    question = sa.Column(sa.String, nullable=False)
    options = sa.Column(sa.JSON, nullable=False)  # Store options as JSON array
    answer = sa.Column(sa.Integer, nullable=False)  # Index of the correct answer
    explanation = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String, nullable=False, default="General")
    difficulty = sa.Column(sa.String, nullable=False, default="Intermediate")
```

#### Score Model

```python
class Score(Base):
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
```

#### Setting Model

```python
class Setting(Base):
    __tablename__ = 'settings'
    
    key = sa.Column(sa.String, primary_key=True)
    value = sa.Column(sa.JSON, nullable=True)  # Store value as JSON to support different types
    updated_at = sa.Column(sa.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
```

## Module Descriptions

### data_manager.py

The data_manager.py module serves as the central data access layer for the application. It abstracts away the storage mechanism (SQLite or JSON) and provides a consistent interface for all data operations.

Key functions:
- `ensure_directories()`: Creates necessary directories
- `initialize_data_files()`: Sets up initial data files or database
- `load_users()`, `load_questions()`, `load_scores()`, `load_settings()`: Load data
- `save_users()`, `save_questions()`, `save_scores()`, `save_settings()`: Save data
- `get_user_scores()`, `get_score_statistics()`, `get_category_statistics()`: Analytics functions

### database/connection.py

Manages SQLite database connections using SQLAlchemy:

```python
# Create database engine
engine = sa.create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def get_db_session():
    """Get a scoped database session"""
    return Session()

def close_db_session():
    """Close the current database session"""
    Session.remove()
```

### database/operations.py

Implements all CRUD operations for the database models:

- User operations: `get_all_users()`, `get_user()`, `save_user()`, `delete_user()`
- Question operations: `get_all_questions()`, `save_questions()`, `add_question()`, etc.
- Score operations: `get_all_scores()`, `save_quiz_score()`, `clear_all_scores()`, etc.
- Setting operations: `get_all_settings()`, `save_settings()`, `get_setting()`, etc.

### auth.py

Handles user authentication and password management:

```python
def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    """Authenticate a user"""
    # Authentication logic with database or file
    # Returns (is_authenticated, role, name)
```

## Data Flow

### Quiz Data Flow

1. **Quiz Setup**:
   - User selects quiz parameters (number of questions, categories, time limit)
   - System loads questions from database/file using `load_questions()`
   - Questions are filtered and randomized based on user parameters

2. **Quiz Execution**:
   - Questions are presented one by one
   - User answers are collected and evaluated
   - Score is calculated as the quiz progresses

3. **Quiz Completion**:
   - Final score is calculated and saved using `save_quiz_score()`
   - Certificate is generated if score meets passing threshold
   - User is redirected to results page

### Question Import Flow

1. **Template Creation**:
   - Admin downloads a CSV template with required columns
   - Template includes: question, option1-4, answer, explanation, category, difficulty

2. **CSV Upload**:
   - Admin uploads the completed CSV file
   - System validates the CSV structure
   - A preview of the data is shown

3. **Import Processing**:
   - System transforms CSV rows into question objects
   - New IDs are generated or existing IDs are preserved based on import mode
   - Questions are saved to the database/file

```python
# CSV to question object transformation
for _, row in df.iterrows():
    new_q = {
        "id": next_id,
        "question": row["question"],
        "options": [row["option1"], row["option2"], row["option3"], row["option4"]],
        "answer": int(row["answer"]),
        "explanation": row["explanation"],
        "category": row.get("category", "General"),
        "difficulty": row.get("difficulty", "Intermediate")
    }
    questions.append(new_q)
    next_id += 1
```

## Authentication System

The authentication system uses a simple username/password approach with SHA-256 hashing:

1. **Registration**:
   - User provides username, password, and name
   - Password is hashed using SHA-256
   - User data is saved to the database/file

2. **Login**:
   - User enters username and password
   - Password is hashed and compared with stored hash
   - If match, user session is created
   - Last login timestamp is updated

3. **Session Management**:
   - Streamlit session_state stores authentication status
   - Role-based access control restricts page access

## Quiz System

The quiz system is designed for flexibility and comprehensive feedback:

### Question Selection

- Questions can be filtered by category
- Random selection ensures varied quiz experiences
- Number of questions is configurable

### Quiz Timer

- Optional time limit for quizzes
- Automatic submission when time expires
- Time taken is recorded with the score

### Performance Tracking

- Overall score percentage
- Category-wise performance
- Correct/incorrect question tracking
- Explanation for each answer

### Result Analysis

- Pass/fail determination based on threshold
- Historical performance comparison
- Certificate generation for passing scores

## Certificate Generation

Certificates are generated using HTML templates:

1. **Data Preparation**:
   - User name, score, date
   - Unique certificate ID generation
   - Company logo embedding (if available)

2. **HTML Generation**:
   - Responsive HTML certificate design
   - CSS styling for professional appearance
   - Base64 encoding for printable and downloadable format

3. **Verification**:
   - Each certificate has a unique ID
   - Verification against score database

## SQLite Migration

The SQLite migration involves moving from JSON file storage to a relational database:

### Migration Process

1. **Initialization**:
   - SQLite database file creation
   - Table schema creation using SQLAlchemy models

2. **Data Transfer**:
   - Reading from JSON files
   - Conversion to appropriate data types
   - Writing to SQLite tables

3. **Verification**:
   - Count comparison between source and destination
   - Data integrity checks

### Migration Utility

The `migrate_to_sqlite.py` script provides a command-line interface for migration:

```bash
# Basic migration
python migrate_to_sqlite.py

# Skip backups
python migrate_to_sqlite.py --no-backup

# Force migration (overwrite existing database)
python migrate_to_sqlite.py --force
```

### Backward Compatibility

The system maintains backward compatibility through:

1. **Dynamic Dispatching**:
   - The data_manager.py checks for SQLite availability
   - Falls back to JSON files if SQLite is unavailable

2. **Data Synchronization**:
   - During transition period, some operations update both systems
   - Ensures data consistency across storage methods

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Include docstrings for all functions and classes
- Use consistent indentation (4 spaces)

### Error Handling

- Use try/except blocks around I/O operations
- Provide meaningful error messages
- Log errors appropriately
- Implement graceful fallbacks

### Session State Management

- Use Streamlit's session_state for user data
- Clear session state when appropriate
- Don't store sensitive information in session_state

### Database Best Practices

- Always use parameterized queries
- Close database sessions after use
- Use transactions for multi-step operations
- Implement connection pooling for high-load scenarios

## Testing

### Unit Testing

- Test each function in isolation
- Mock external dependencies
- Cover edge cases and error conditions

### Integration Testing

- Test interaction between modules
- Verify data flow across system boundaries
- Test with realistic data volumes

### Performance Testing

- Benchmark database operations
- Test with large datasets
- Identify and optimize bottlenecks

## Deployment

### Local Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Server Deployment

1. **Environment Setup**:
   - Python 3.8+ environment
   - Virtual environment recommended
   - Set up systemd service or similar for persistent running

2. **Configuration**:
   - Ensure proper file permissions
   - Configure backup strategy
   - Set up logging

3. **Startup Script Example** (systemd):
   ```ini
   [Unit]
   Description=Forklift Operator Training Application
   After=network.target

   [Service]
   User=appuser
   WorkingDirectory=/path/to/app
   ExecStart=/path/to/venv/bin/streamlit run app.py
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

## Common Issues

### Database Connection Issues

- **Problem**: SQLite database locked errors
- **Solution**: Ensure all connections are properly closed and implement connection pooling

### Data Migration Failures

- **Problem**: Migration script fails part way through
- **Solution**: Use transactions for atomic operations and implement resume functionality

### Memory Usage

- **Problem**: High memory usage with large datasets
- **Solution**: Implement pagination and lazy loading for large queries

### Streamlit Session Expiry

- **Problem**: Session state lost after inactivity
- **Solution**: Implement auto-save functionality and session recovery mechanisms

### Concurrent Access Issues

- **Problem**: Multiple users experiencing data conflicts
- **Solution**: Implement proper locking mechanisms and optimistic concurrency control

### Author & Maintenance Contact Information

## Primary Developer Contact

**Name:** MLawali  
**Email:** [mlawali@vseratexmsp.com]  
**Phone:** [Optional Phone Number]  
**GitHub:** [MLawali]  

## Technical Support

For technical support or questions regarding the application:

**Support Email:** [mlawali@vseratexmsp.com]  
**Issue Tracker:** [https://github.com/bomino/DEFQuizard/issues](https://github.com/bomino/DEFQuizard/issues)  
**Documentation Wiki:** [https://github.com/bomino/DEFQuizard/wiki](https://github.com/bomino/DEFQuizard/wiki)

## Contributing

We welcome contributions to the Forklift Operator Training Application. Please see our [CONTRIBUTING.md](CONTRIBUTING.md) guide for details on how to submit pull requests, coding standards, and development process.

## License Information

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Security Contacts

To report security vulnerabilities, please email:  
[mlawali@vseratexmsp.com](mailto:mlawali@vseratexmsp.com)

Please do not disclose security vulnerabilities publicly until they have been addressed by the team.

## Acknowledgements

Special thanks to all contributors who have helped improve this application:

- [AY]
- [Lawali]


## Version Information

**Current Version:** 3.0.0  
**Last Updated:** April 7, 2025  
**Major Changes:** SQLite database migration