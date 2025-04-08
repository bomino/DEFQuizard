# Forklift Operator Training Application

A comprehensive web application for training and assessing forklift operators on safety protocols and operational procedures, with certification management and advanced analytics.

![Forklift Training App Screenshot](assets/app_screenshot.png)

## Features

- **Interactive Quiz System**
  - Configurable quizzes with category filtering
  - Time limits and progress tracking
  - Immediate feedback and explanations
  - Question randomization

- **Dashboard & Analytics**
  - Personalized user dashboard
  - Performance metrics and progress visualization
  - Category-based performance analysis
  - Certification status tracking

- **Certification Management**
  - Automatic certificate generation for passing scores
  - Customizable certificate templates
  - Expiration tracking and renewal reminders
  - Unique verification IDs

- **Admin Controls**
  - Comprehensive analytics dashboard
  - Question management with import/export
  - User management and access control
  - System configuration and branding
  - Score data management

- **Modern UI/UX**
  - Responsive design for all devices
  - Intuitive navigation
  - Visual feedback and progress indicators
  - Company branding integration
  
- **SQLite Database**
  - Robust data storage solution
  - Improved data integrity and security
  - Better performance with larger datasets
  - Enhanced backup and recovery options
  - Advanced database management tools

## Project Overview

The Forklift Operator Training Application helps manufacturing facilities train and certify their forklift operators in compliance with OSHA regulations. The system provides:

- **Safety Compliance**: Test knowledge of OSHA regulations and best practices
- **Performance Tracking**: Monitor operator progress and identify knowledge gaps
- **Certification Management**: Automatically generate and track training certificates
- **Administration Tools**: Manage questions, users, and system settings
- **Data Analysis**: Gain insights from training performance data
- **Database Management**: Reliable SQLite-based data storage with management tools

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/forklift-training-app.git
cd forklift-training-app

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Project Structure

```
forklift_app/
│
├── app.py                 # Main application file
├── requirements.txt       # Dependencies
├── migrate_to_sqlite.py   # Migration utility script
│
├── assets/                # Static files
│   └── logo.png           # Company logo (when uploaded)
│
├── data/                  # Data storage
│   ├── forklift_training.db # SQLite database file
│   ├── users.json         # Legacy user credentials (optional)
│   ├── questions.json     # Legacy quiz questions (optional)
│   ├── scores.json        # Legacy quiz scores (optional)
│   ├── settings.json      # Legacy application settings (optional)
│   └── backups/           # Automatic backups
│
└── modules/               # Application modules
    ├── __init__.py
    ├── auth.py            # Authentication functions
    ├── data_manager.py    # Data access layer
    ├── ui.py              # UI components and styling
    ├── certificate.py     # Certificate generation
    ├── database/          # Database modules
    │   ├── __init__.py
    │   ├── connection.py  # Database connection management
    │   ├── models.py      # SQLAlchemy models
    │   ├── operations.py  # Database operations
    │   └── migrate.py     # Data migration utilities
    ├── pages/             # Page modules
    │   ├── __init__.py
    │   ├── login.py       # Login page
    │   ├── dashboard.py   # Dashboard page
    │   ├── quiz.py        # Quiz page
    │   ├── scores.py      # Scores page
    │   ├── documentation.py # Documentation page
    │   ├── admin.py       # Admin panel
    │   └── admin_db.py    # Database management interface
    └── utils.py           # Utility functions
```

## SQLite Migration

The application supports both JSON file storage and SQLite database storage:

1. **Default Mode**: On first run, the application will use SQLite if requirements are installed
2. **Migration Tool**: `migrate_to_sqlite.py` script to migrate from JSON files to SQLite database
3. **Backwards Compatibility**: Will fall back to JSON files if SQLite requirements are not available

### Migrating from JSON to SQLite

```bash
# Make sure you have SQLAlchemy installed
pip install sqlalchemy alembic

# Run the migration script
python migrate_to_sqlite.py
```

## User Roles

- **Operators**: Take quizzes, view scores, download certificates, track progress
- **Administrators**: Manage questions, view analytics, manage users, configure system settings

## Default Admin Login

- Username: `admin`
- Password: `admin123`

**Important**: Change the default admin password after first login.

## Customization

The application supports several customization options:

- **Company Branding**: Upload your company logo
- **Certificate Design**: Customize certificate appearance
- **Quiz Settings**: Configure passing score, time limits, question counts
- **System Behavior**: Set certificate validity, registration options, security policies
- **Database Settings**: Configure backup frequency and optimize database performance

## Deployment

This application is configured for easy deployment:

1. **Local Deployment**:
   - Follow the installation instructions above
   - Suitable for single-location training

2. **Server Deployment**:
   - Deploy on an internal server for company-wide access
   - Ensure proper file permissions for data directory

3. **Streamlit Cloud**:
   - Push the project to a GitHub repository
   - Connect the repository to Streamlit Cloud
   - Specify `app.py` as the main file

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Streamlit for the web framework
- SQLAlchemy for ORM functionality
- OSHA for forklift safety guidelines and standards