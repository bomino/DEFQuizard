import streamlit as st
import os

# Import modules
from modules.ui import initialize_session_state, show_sidebar, load_css
from modules.data_manager import ensure_directories, initialize_data_files
from modules.pages.login import login_page
from modules.pages.quiz import quiz_page
from modules.pages.scores import scores_page
from modules.pages.dashboard import dashboard_page
from modules.pages.documentation import documentation_page
from modules.pages.admin import admin_page

# Check if database module is available
try:
    from modules.database.connection import init_db
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False

# Configure the app with improved settings
st.set_page_config(
    page_title="Forklift Operator Training",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.osha.gov/powered-industrial-trucks',
        'About': "Forklift Operator Training and Certification System\nVersion 3.0"
    }
)

# Initialize app data and state
def initialize_app():
    """Ensure all required directories and data files exist"""
    # Ensure directories exist
    ensure_directories()
    
    # Initialize database if available
    if USE_DATABASE:
        init_db()
    
    # Initialize data files with defaults if they don't exist
    initialize_data_files()
    
    # Initialize session state for user tracking
    initialize_session_state()
    
    # Apply custom CSS for modern UI
    st.markdown(load_css(), unsafe_allow_html=True)

# Main app function with enhanced routing
def main():
    # Initialize the app
    initialize_app()
    
    # Show the sidebar for navigation if authenticated
    if st.session_state.authenticated:
        show_sidebar()
    
    # Render the appropriate page based on state and role
    if not st.session_state.authenticated:
        login_page()
    else:
        # Default to dashboard
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "dashboard"
        
        # Route to appropriate page
        if st.session_state.current_page == "dashboard":
            dashboard_page()
        elif st.session_state.current_page == "quiz":
            quiz_page()
        elif st.session_state.current_page == "scores":
            scores_page()
        elif st.session_state.current_page == "documentation" and st.session_state.role == "admin":
            documentation_page()
        elif st.session_state.current_page == "admin" and st.session_state.role == "admin":
            admin_page()
        else:
            # If invalid page, redirect to dashboard
            st.session_state.current_page = "dashboard"
            dashboard_page()

# Run the app
if __name__ == "__main__":
    main()