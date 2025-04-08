# modules/pages/documentation.py

import streamlit as st
from ..ui import load_css, display_logo

def documentation_page():
    """Display the application documentation for administrators"""
    # Security check - only allow admins to view documentation
    if st.session_state.role != "admin":
        st.error("You do not have permission to access this page.")
        st.button("Return to Quiz", on_click=lambda: navigate_to("quiz"))
        return

    # Apply custom CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Display logo
    display_logo()
    
    st.title("Forklift Operator Quiz App Documentation")
    
    # Create an expandable section for each part of the documentation
    with st.expander("Overview", expanded=True):
        st.markdown("""
        The Forklift Operator Quiz App is a comprehensive web-based application designed for safety training and assessment 
        of forklift operators in manufacturing environments. The app allows operators to test their knowledge of safety 
        protocols, track their progress, earn certificates for passing scores, and maintain compliance with OSHA standards.
        Administrators can manage questions, view detailed analytics on operator performance, and administer user accounts.
        """)
    
    with st.expander("User Guide"):
        st.markdown("### Registration and Login")
        st.markdown("""
        1. **Registration**:
           - Click the "Register" tab on the login page
           - Fill in username, password, and full name
           - Click "Register" to create your account
           - All new self-registered users receive "operator" role

        2. **Login**:
           - Enter your username and password
           - Click "Login" to access the application
        """)
        
        st.markdown("### Dashboard")
        st.markdown("""
        1. **Overview**:
           - The dashboard is your home page after logging in
           - View your certification status
           - See your quiz performance statistics
           - Access quick links to main features
           
        2. **Navigation**:
           - Use the sidebar to navigate between different sections
           - Dashboard, Quiz, Scores, and additional options for admins
        """)
        
        st.markdown("### Taking a Quiz")
        st.markdown("""
        1. **Starting a Quiz**:
           - Click "Take Quiz" in the navigation menu
           - Configure quiz settings (number of questions, categories, time limit)
           - Click "Start Quiz" to begin
           
        2. **During the Quiz**:
           - Read each question carefully
           - Select your answer from the provided options
           - Click "Submit Answer" to check your answer
           - Review feedback and explanation
           - Click "Next Question" to proceed (or "Previous" to review earlier questions)
           - Watch the timer if time limits are enabled
           
        3. **Completing the Quiz**:
           - After answering all questions, view your final score
           - See performance breakdown by category
           - Review incorrect answers
           - Download a certificate if you achieved a passing score (80% or higher by default)
        """)
        
        st.markdown("### Viewing Scores")
        st.markdown("""
        1. **Score Overview**:
           - Navigate to the Scores page using the sidebar
           - View your latest quiz score
           - Check your score progression over time (line chart)
           - Review statistics (best score, average score)
           
        2. **Detailed Analysis**:
           - See all your quiz attempts in the table
           - Track improvement over time
           - Identify areas for further study
        """)
        
        st.markdown("### Certificates")
        st.markdown("""
        1. **Earning Certificates**:
           - Achieve a passing score (configurable, default 80%)
           - Certificate is generated automatically after passing
           
        2. **Managing Certificates**:
           - Download certificates in HTML format
           - Each certificate has a unique verification ID
           - Certificates include expiry date based on system settings
        """)
        
        st.markdown("### Logging Out")
        st.markdown("""
        1. Click "Logout" in the sidebar to end your session
        """)
    
    with st.expander("Administrator Guide"):
        st.markdown("### Admin Dashboard")
        st.markdown("""
        1. **Key Metrics**:
           - View overall system statistics
           - Monitor quiz completion rates
           - Track passing percentages
           - Analyze user activity
           
        2. **Performance Analytics**:
           - View performance by category
           - Identify top performers
           - Analyze most challenging questions
           - Monitor score trends over time
           
        3. **Export Data**:
           - Download comprehensive score data
           - Export user performance summaries
        """)
        
        st.markdown("### Managing Questions")
        st.markdown("""
        1. **Question Import/Export**:
           - Import questions from CSV files
           - Option to replace all existing questions
           - Export questions filtered by category
           - Download question templates
           
        2. **Adding Questions**:
           - Create new questions with multiple-choice options
           - Assign categories and difficulty levels
           - Provide explanations for correct answers
           
        3. **Editing Questions**:
           - Modify existing questions
           - Update answer options
           - Change category or difficulty
           - Improve explanations
           
        4. **Deleting Questions**:
           - Remove individual questions
           - Batch delete questions
           - Filter questions by category or difficulty
        """)
        
        st.markdown("### Managing Users")
        st.markdown("""
        1. **User Overview**:
           - View all users with filtering options
           - See quiz performance statistics
           - Monitor login activity
           
        2. **Adding Users**:
           - Create user accounts with specific roles
           - Set initial passwords
           - Assign operator or admin privileges
           
        3. **Password Management**:
           - Reset user passwords
           - Generate secure random passwords
           - Enforce password complexity requirements
           
        4. **Removing Users**:
           - Delete user accounts
           - Safety checks to prevent removing all administrators
           
        5. **Managing Quiz Results**:
           - Clear results for specific users
           - Reset all quiz history if needed
        """)
        
        st.markdown("### System Settings")
        st.markdown("""
        1. **Application Settings**:
           - Set company name
           - Configure passing score threshold
           - Set certificate validity period
           - Enable/disable self-registration
           
        2. **Quiz Settings**:
           - Configure default time limits
           - Set default number of questions
           - Enable category performance tracking
           
        3. **Security Settings**:
           - Password reset requirements
           - Password expiration policy
        """)
        
        st.markdown("### Branding")
        st.markdown("""
        1. **Logo Management**:
           - Upload custom company logo
           - Preview logo appearance
           - Remove existing logo
           
        2. **Certificate Customization**:
           - Preview certificate design
           - See how certificates appear to users
        """)
    
    with st.expander("Features"):
        st.markdown("### Core Features")
        st.markdown("""
        1. **Authentication System**
           - User registration and login
           - Role-based access control (admin vs. operator)
           - Password hashing for security
           - Password complexity requirements

        2. **Dashboard**
           - Personalized user dashboard
           - Certification status tracking
           - Performance metrics
           - Quick navigation

        3. **Quiz Module**
           - Configurable quiz parameters
           - Category filtering
           - Time limits
           - Randomized question ordering
           - Immediate feedback with explanations
           - Progress tracking
           - Navigation between questions
           - Pass/fail scoring with certificate generation

        4. **Score Tracking**
           - Historical record of all quiz attempts
           - Progress visualization with charts
           - Category performance breakdown
           - Achievement tracking (best scores, averages)

        5. **Administrator Tools**
           - Comprehensive dashboard with analytics
           - Question management (add, edit, import/export)
           - User management (add, reset passwords, remove)
           - Score management and data export
           - System configuration
           - Company branding customization

        6. **Professional Certificates**
           - Customizable completion certificates
           - Company logo integration
           - Unique certificate IDs
           - Expiration dates
           - Downloadable in HTML format
        """)
    
    with st.expander("Troubleshooting"):
        st.markdown("### Common Issues")
        st.markdown("""
        1. **Login Problems**
           - Ensure username and password are correct
           - Check if account exists
           - Admin can reset password if forgotten
           
        2. **Quiz Not Starting**
           - Ensure questions exist in the system
           - Check if category filters are set correctly
           - Verify question count doesn't exceed available questions
           
        3. **Certificate Not Generated**
           - Verify passing score threshold has been met
           - Check if certificate system is properly configured
           - Ensure proper permissions for file access

        4. **Error: Cannot connect to Streamlit server**
           - Ensure you've installed all dependencies
           - Check if another application is using port 8501
           - Restart your computer and try again

        5. **Error: Module not found**
           - Ensure your virtual environment is activated
           - Verify all dependencies are installed
           - Check if you're running from the correct directory

        6. **Missing data files**
           - The application should create necessary files on first run
           - Ensure the app has write permissions to the data directory
        """)
    
    with st.expander("Technical Information"):
        st.markdown("### System Architecture")
        st.markdown("""
        1. **Frontend**
           - Built with Streamlit
           - Responsive design for various devices
           - Modern UI components
           
        2. **Backend**
           - Python-based application logic
           - File-based data storage (JSON)
           - Module-based organization
           
        3. **Security**
           - Password hashing with SHA-256
           - Role-based access control
           - Session management
           
        4. **Data Management**
           - JSON data storage
           - Automatic backups
           - Data export capabilities
        """)
        
        st.markdown("### Deployment Options")
        st.markdown("""
        1. **Local Deployment**
           - Run on local machine for single-office use
           - Requires Python environment
           
        2. **Server Deployment**
           - Deploy on company intranet
           - Multiple users can access simultaneously
           
        3. **Cloud Deployment**
           - Deploy on Streamlit Cloud
           - Accessible from anywhere
           - May require additional security measures
        """)
        
        st.markdown("### Data Storage")
        st.markdown("""
        The application uses JSON files for data storage:
        
        - `users.json`: User accounts and authentication data
        - `questions.json`: Quiz questions and answer options
        - `scores.json`: Quiz attempt history and performance data
        - `settings.json`: Application configuration settings
        
        All files are stored in the `data/` directory. Backups are automatically created in `data/backups/` when files are modified.
        """)