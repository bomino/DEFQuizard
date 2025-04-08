# Database package initialization
"""
This package provides SQLite database support for the Forklift Operator Training application.

It includes:
- Database models
- Connection management
- Data access operations
- Migration utilities
"""

from .connection import get_db_session, close_db_session, init_db
from .models import User, Question, Score, Setting