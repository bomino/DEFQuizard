import streamlit as st
import base64
import os
from .data_manager import LOGO_PATH, load_settings

def load_css():
    """
    Load custom CSS for modern look and feel
    Returns CSS as a string to be displayed as markdown
    """
    return """
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #1E88E5;
        --primary-light: #64B5F6;
        --primary-dark: #0D47A1;
        --background-color: #f4f7fa;
        --card-background: #ffffff;
        --secondary-color: #ff9800;
        --secondary-light: #FFB74D;
        --text-color: #212121;
        --text-light: #757575;
        --success-color: #4CAF50;
        --error-color: #F44336;
        --warning-color: #FFC107;
        --info-color: #2196F3;
        --border-radius: 10px;
        --box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        --transition-speed: 0.3s;
    }

    /* Page background */
    .main {
        background-color: var(--background-color);
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Typography */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--text-color);
        line-height: 1.6;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-dark);
        font-weight: 600;
        margin-bottom: 1rem;
    }

    h1 {
        font-size: 2.5rem;
        position: relative;
        padding-bottom: 10px;
    }

    h1:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 50px;
        height: 4px;
        background-color: var(--primary-color);
        border-radius: 2px;
    }

    h2 {
        font-size: 2rem;
    }

    h3 {
        font-size: 1.5rem;
        color: var(--primary-color);
    }

    /* Cards styling */
    .quiz-card {
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        background-color: var(--card-background);
        border-top: 4px solid var(--primary-color);
        transition: transform var(--transition-speed), box-shadow var(--transition-speed);
    }

    .quiz-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    /* Question card specific styling */
    .question-card {
        border-top: 4px solid var(--info-color);
    }

    /* Result card specific styling */
    .result-card {
        border-top: 4px solid var(--success-color);
    }

    /* Buttons */
    .stButton button {
        border-radius: 25px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all var(--transition-speed) ease;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    /* Primary button */
    .primary-btn button {
        background-color: var(--primary-color) !important;
        color: white !important;
    }

    .primary-btn button:hover {
        background-color: var(--primary-dark) !important;
    }

    /* Secondary button */
    .secondary-btn button {
        background-color: var(--secondary-color) !important;
        color: white !important;
    }

    /* Success button */
    .success-btn button {
        background-color: var(--success-color) !important;
        color: white !important;
    }

    /* Warning button */
    .warning-btn button {
        background-color: var(--warning-color) !important;
        color: var(--text-color) !important;
    }

    /* Danger button */
    .danger-btn button {
        background-color: var(--error-color) !important;
        color: white !important;
    }

    /* Ghost button */
    .ghost-btn button {
        background-color: transparent !important;
        color: var(--primary-color) !important;
        border: 1px solid var(--primary-color) !important;
        box-shadow: none !important;
    }

    .ghost-btn button:hover {
        background-color: rgba(30, 136, 229, 0.1) !important;
    }

    /* Logo container */
    .logo-container {
        text-align: center;
        padding: 1.5rem 1rem;
        transition: all var(--transition-speed) ease;
    }

    .logo-container img {
        max-height: 80px;
        transition: all var(--transition-speed) ease;
    }

    .logo-container:hover img {
        transform: scale(1.05);
    }

    /* Certificate styling */
    .certificate-container {
        background-color: white;
        border-radius: var(--border-radius);
        padding: 30px;
        box-shadow: var(--box-shadow);
        margin: 30px 0;
        text-align: center;
        border: 1px solid #e0e0e0;
        position: relative;
        overflow: hidden;
    }

    .certificate-container:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
    }

    /* Certificate download button */
    .certificate-button {
        display: inline-block;
        background: linear-gradient(to right, var(--primary-color), var(--primary-dark));
        color: white !important; /* Force white text color */
        padding: 12px 30px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 20px;
        transition: all var(--transition-speed) ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.4);
    }

    .certificate-button:hover {
        background: linear-gradient(to right, var(--primary-dark), var(--primary-color));
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.6);
        color: white !important; /* Ensure text stays white on hover too */
        text-decoration: none; /* Remove default underline on hover */
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        
        .quiz-card {
            padding: 1.25rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        h3 {
            font-size: 1.25rem;
        }
    }

    /* Sidebar - improved and more compact */
    [data-testid="stSidebar"] {
        background-color: white;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
    }

    /* User info card at the top */
    .sidebar-user-info {
        background-color: #f0f7ff;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
    }

    .sidebar-user-info p {
        margin: 0 !important;
    }

    .sidebar-user-name {
        font-weight: 600;
        font-size: 1rem;
    }

    .sidebar-user-role {
        font-size: 0.8rem;
        color: #555;
        margin-top: 3px !important;
    }

    /* Section headers */
    .sidebar-section-header {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #666;
        margin: 15px 0 8px 0;
        letter-spacing: 0.5px;
    }

    /* Navigation buttons */
    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        text-align: left;
        padding: 8px 12px;
        margin-bottom: 4px;
        border-radius: 6px;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateX(3px);
    }

    /* Button icons */
    .sidebar-button-icon {
        display: inline-block;
        width: 20px;
        text-align: center;
        margin-right: 8px;
    }

    /* Divider */
    .sidebar-divider {
        height: 1px;
        background-color: #eaeaea;
        margin: 12px 0;
    }

    /* Expander */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        border: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] > div[role="button"] {
        border-radius: 6px;
        padding: 8px 12px !important;
        font-size: 0.9rem;
    }

    /* Footer */
    .sidebar-footer {
        font-size: 0.7rem;
        color: #999;
        text-align: center;
        padding: 12px 0;
        margin-top: 20px;
        border-top: 1px solid #eaeaea;
    }
    </style>
    """



# Helper function to encode images to base64
def get_base64_encoded_image(image_path):
    """
    Convert an image file to base64 encoded string
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Base64 encoded string of the image
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

# Display company logo
def display_logo():
    """Display the company logo or a placeholder if no logo is available"""
    settings = load_settings()
    company_name = settings.get("company_name", "Your Company")
    
    # Check if logo file exists
    if os.path.exists(LOGO_PATH):
        # Use actual logo file
        logo_base64 = get_base64_encoded_image(LOGO_PATH)
        if logo_base64:
            logo_html = f"""
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_base64}" alt="{company_name} Logo">
            </div>
            """
        else:
            # Fallback to placeholder if encoding fails
            logo_html = f"""
            <div class="logo-container">
                <img src="https://via.placeholder.com/200x80?text={company_name.replace(' ', '+')}" alt="{company_name} Logo">
            </div>
            """
    else:
        # Use placeholder logo with company name
        logo_html = f"""
        <div class="logo-container">
            <img src="https://via.placeholder.com/200x80?text={company_name.replace(' ', '+')}" alt="{company_name} Logo">
        </div>
        """
    st.markdown(logo_html, unsafe_allow_html=True)

# Apply custom CSS class to a component
def apply_custom_css_class(component, css_class):
    """
    Wrap a component with a div of a specific CSS class
    
    Args:
        component: Streamlit component to wrap
        css_class (str): CSS class name to apply
    """
    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
    component
    st.markdown('</div>', unsafe_allow_html=True)

# Session State and Navigation
def initialize_session_state():
    """Initialize session state variables for tracking user and navigation"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.name = None
        st.session_state.current_page = "login"
        st.session_state.theme = "light"  # Added theme support

def navigate_to(page):
    """
    Navigate to a different page and reset any page-specific state
    
    Args:
        page (str): Page name to navigate to
    """
    st.session_state.current_page = page
    
    # Reset quiz state when navigating away from quiz
    if page != "quiz":
        # Clear quiz-related session state
        for key in list(st.session_state.keys()):
            if key.startswith("quiz_") or key in [
                "current_question", "score", "answered", 
                "quiz_complete", "quiz_in_progress",
                "correct_answers", "incorrect_answers", "selected_answers"
            ]:
                del st.session_state[key]

def show_sidebar():
    """Display a more compact and modern navigation sidebar"""
    with st.sidebar:
        # Apply custom CSS
        st.markdown(load_css(), unsafe_allow_html=True)
        
        # Display logo
        display_logo()
        
        # User info card
        st.markdown(f"""
            <div style="background-color: #f0f7ff; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                <p style="margin: 0; font-weight: 600; font-size: 1rem;">Welcome, {st.session_state.name}</p>
                <p style="margin: 3px 0 0 0; font-size: 0.8rem; color: #555;">Role: {st.session_state.role.title()}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation header
        st.markdown('<p style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: #666; margin: 15px 0 8px 0; letter-spacing: 0.5px;">NAVIGATION</p>', unsafe_allow_html=True)
        
        # Dashboard button - Plain buttons without HTML in the label
        current_page = st.session_state.current_page
        if current_page == "dashboard":
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("📊 Dashboard", use_container_width=True):
            navigate_to("dashboard")
            st.rerun()
        if current_page == "dashboard":
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Quiz button
        if current_page == "quiz":
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("📝 Take Quiz", use_container_width=True):
            navigate_to("quiz")
            st.rerun()
        if current_page == "quiz":
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Scores button
        if current_page == "scores":
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("📈 View Scores", use_container_width=True):
            navigate_to("scores")
            st.rerun()
        if current_page == "scores":
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Admin-only sections
        if st.session_state.role == "admin":
            st.markdown('<hr style="height: 1px; background-color: #eaeaea; margin: 12px 0;">', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: #666; margin: 15px 0 8px 0; letter-spacing: 0.5px;">ADMIN CONTROLS</p>', unsafe_allow_html=True)
            
            # Admin panel button
            if current_page == "admin":
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("⚙️ Admin Panel", use_container_width=True):
                navigate_to("admin")
                st.rerun()
            if current_page == "admin":
                st.markdown('</div>', unsafe_allow_html=True)
                
            # Documentation button
            if current_page == "documentation":
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("📚 Documentation", use_container_width=True):
                navigate_to("documentation")
                st.rerun()
            if current_page == "documentation":
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Settings expander - more compact
        with st.expander("Display Settings"):
            # Theme selection
            current_theme = st.session_state.get("theme", "light")
            theme_options = {"light": "Light Mode", "dark": "Dark Mode"}
            selected_theme = st.radio("Theme", options=list(theme_options.keys()), 
                                     format_func=lambda x: theme_options[x],
                                     index=0 if current_theme == "light" else 1,
                                     horizontal=True)
            
            if selected_theme != current_theme:
                st.session_state.theme = selected_theme
                st.rerun()
            
            # Font size selection
            font_size = st.select_slider(
                "Font Size",
                options=["Small", "Medium", "Large"],
                value=st.session_state.get("font_size", "Medium")
            )
            
            if font_size != st.session_state.get("font_size", "Medium"):
                st.session_state.font_size = font_size
                st.rerun()
        
        # Logout button
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Reset basic state
            initialize_session_state()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # App info footer - properly positioned
        st.markdown("""
            <div style="font-size: 0.7rem; color: #999; text-align: center; padding: 12px 0; margin-top: 20px; border-top: 1px solid #eaeaea;">
                XLC Forklift Operator Training <br>
                © 2025 Forklift Safety Systems
            </div>
        """, unsafe_allow_html=True)

# Show a notification or alert
def show_notification(message, type="info"):
    """
    Display a notification message with appropriate styling
    
    Args:
        message (str): Message to display
        type (str): Type of notification - "info", "success", "warning", or "error"
    """
    if type == "success":
        st.markdown(f"""
            <div style="padding: 15px; background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4CAF50; 
                    border-radius: 4px; margin-bottom: 15px;">
                <p style="margin: 0; color: #2E7D32;"><strong>Success:</strong> {message}</p>
            </div>
        """, unsafe_allow_html=True)
    elif type == "warning":
        st.markdown(f"""
            <div style="padding: 15px; background-color: rgba(255, 152, 0, 0.1); border-left: 4px solid #FF9800; 
                    border-radius: 4px; margin-bottom: 15px;">
                <p style="margin: 0; color: #E65100;"><strong>Warning:</strong> {message}</p>
            </div>
        """, unsafe_allow_html=True)
    elif type == "error":
        st.markdown(f"""
            <div style="padding: 15px; background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #F44336; 
                    border-radius: 4px; margin-bottom: 15px;">
                <p style="margin: 0; color: #C62828;"><strong>Error:</strong> {message}</p>
            </div>
        """, unsafe_allow_html=True)
    else:  # info
        st.markdown(f"""
            <div style="padding: 15px; background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196F3; 
                    border-radius: 4px; margin-bottom: 15px;">
                <p style="margin: 0; color: #0D47A1;"><strong>Info:</strong> {message}</p>
            </div>
        """, unsafe_allow_html=True)

# Display a confirmation dialog
def confirm_dialog(title, message, confirm_button="Confirm", cancel_button="Cancel"):
    """
    Display a confirmation dialog and return the result
    
    Args:
        title (str): Dialog title
        message (str): Message to display
        confirm_button (str): Text for confirm button
        cancel_button (str): Text for cancel button
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    st.markdown(f"""
        <div style="padding: 20px; background-color: white; border-radius: 10px; 
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); margin-bottom: 20px;">
            <h3 style="margin-top: 0;">{title}</h3>
            <p>{message}</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        cancel = st.button(cancel_button, key="cancel_btn")
    
    with col2:
        confirm = st.button(confirm_button, key="confirm_btn")
    
    return confirm

# Display a modal with content
def show_modal(title, content, close_button="Close"):
    """
    Display a modal dialog with custom content
    
    Args:
        title (str): Modal title
        content (str): HTML content to display
        close_button (str): Text for close button
    """
    modal_id = f"modal_{hash(title)}"
    
    # Modal CSS
    st.markdown(f"""
        <style>
        #{modal_id} {{
            display: block;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            overflow: auto;
        }}
        
        #{modal_id} .modal-content {{
            background-color: white;
            margin: 10% auto;
            padding: 20px;
            border-radius: 10px;
            width: 70%;
            max-width: 700px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            position: relative;
        }}
        
        #{modal_id} .close {{
            position: absolute;
            top: 10px;
            right: 20px;
            font-size: 28px;
            font-weight: bold;
            color: #aaa;
            cursor: pointer;
        }}
        
        #{modal_id} .close:hover {{
            color: #555;
        }}
        </style>
        
        <div id="{modal_id}">
            <div class="modal-content">
                <span class="close" onclick="document.getElementById('{modal_id}').style.display='none';">&times;</span>
                <h2>{title}</h2>
                <div class="modal-body">
                    {content}
                </div>
                <div style="text-align: right; margin-top: 20px;">
                    <button onclick="document.getElementById('{modal_id}').style.display='none';" 
                            style="background-color: #1E88E5; color: white; border: none; padding: 8px 16px; 
                                   border-radius: 4px; cursor: pointer;">
                        {close_button}
                    </button>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Display a loading spinner with message
def show_loading(message="Loading..."):
    """
    Display a custom loading spinner with message
    
    Args:
        message (str): Message to display while loading
    """
    loading_html = f"""
        <div style="display: flex; align-items: center; justify-content: center; padding: 20px;">
            <div style="border: 5px solid #f3f3f3; border-top: 5px solid #1E88E5; 
                      border-radius: 50%; width: 30px; height: 30px; 
                      animation: spin 1s linear infinite; margin-right: 15px;"></div>
            <p style="margin: 0; color: #555;">{message}</p>
        </div>
        
        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    """
    st.markdown(loading_html, unsafe_allow_html=True)

# Create a custom tab interface
def custom_tabs(tabs_dict):
    """
    Create a custom styled tab interface
    
    Args:
        tabs_dict (dict): Dictionary of tab names and their content functions
                         e.g. {"Tab 1": tab1_function, "Tab 2": tab2_function}
    """
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = list(tabs_dict.keys())[0]
    
    # Render the tabs
    cols = st.columns(len(tabs_dict))
    
    for i, (tab_name, _) in enumerate(tabs_dict.items()):
        with cols[i]:
            if tab_name == st.session_state.active_tab:
                st.markdown(f"""
                    <div style="text-align: center; padding: 10px; 
                             background-color: #1E88E5; color: white; 
                             border-radius: 10px 10px 0 0; cursor: pointer; 
                             font-weight: 600;">
                        {tab_name}
                    </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(tab_name, key=f"tab_{tab_name}", use_container_width=True):
                    st.session_state.active_tab = tab_name
                    st.rerun()
    
    # Display the content of the active tab
    st.markdown("""
        <div style="border: 1px solid #ddd; border-top: none; 
                 border-radius: 0 0 10px 10px; padding: 20px;">
    """, unsafe_allow_html=True)
    
    tabs_dict[st.session_state.active_tab]()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Create a custom card component
def create_card(title, content, icon=None, footer=None, color=None):
    """
    Create a custom styled card component
    
    Args:
        title (str): Card title
        content (str): Card content (HTML)
        icon (str, optional): Icon for the card (emoji or HTML)
        footer (str, optional): Footer content (HTML)
        color (str, optional): Accent color for the card
    """
    if not color:
        color = "#1E88E5"  # Default to primary color
    
    icon_html = f"""
        <div style="font-size: 24px; margin-right: 10px;">
            {icon}
        </div>
    """ if icon else ""
    
    footer_html = f"""
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #f0f0f0; font-size: 0.9rem; color: #777;">
            {footer}
        </div>
    """ if footer else ""
    
    card_html = f"""
        <div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 20px;
                  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); border-top: 4px solid {color};">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                {icon_html}
                <h3 style="margin: 0; color: {color};">{title}</h3>
            </div>
            <div>
                {content}
            </div>
            {footer_html}
        </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# Create a progress indicator
def progress_indicator(steps, current_step, labels=None):
    """
    Display a horizontal progress indicator for multi-step processes
    
    Args:
        steps (int): Total number of steps
        current_step (int): Current step (1-indexed)
        labels (list, optional): List of step labels
    """
    if not labels:
        labels = [f"Step {i+1}" for i in range(steps)]
    
    progress_html = """
        <div style="display: flex; justify-content: space-between; align-items: center; 
                  margin: 30px 0; position: relative;">
    """
    
    # Add a line connecting all steps
    progress_html += f"""
        <div style="position: absolute; height: 2px; background-color: #e0e0e0; 
                  top: 15px; left: 15px; right: 15px; z-index: 1;"></div>
        <div style="position: absolute; height: 2px; background-color: #1E88E5; 
                  top: 15px; left: 15px; width: {((current_step - 1) / (steps - 1)) * 100}%; z-index: 2;"></div>
    """
    
    # Add individual steps
    for i in range(steps):
        step_num = i + 1
        
        if step_num < current_step:
            # Completed step
            progress_html += f"""
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: #1E88E5; 
                          color: white; display: flex; justify-content: center; align-items: center;
                          font-weight: 600; position: relative; z-index: 3;">
                    <span>✓</span>
                    <div style="position: absolute; top: 35px; left: 50%; transform: translateX(-50%); 
                              white-space: nowrap; font-size: 0.8rem; font-weight: 500; color: #1E88E5;">
                        {labels[i]}
                    </div>
                </div>
            """
        elif step_num == current_step:
            # Current step
            progress_html += f"""
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: white; 
                          border: 2px solid #1E88E5; color: #1E88E5; display: flex; justify-content: center; 
                          align-items: center; font-weight: 600; position: relative; z-index: 3;">
                    <span>{step_num}</span>
                    <div style="position: absolute; top: 35px; left: 50%; transform: translateX(-50%); 
                              white-space: nowrap; font-size: 0.8rem; font-weight: 600; color: #1E88E5;">
                        {labels[i]}
                    </div>
                </div>
            """
        else:
            # Upcoming step
            progress_html += f"""
                <div style="width: 30px; height: 30px; border-radius: 50%; background-color: white; 
                          border: 2px solid #e0e0e0; color: #888; display: flex; justify-content: center; 
                          align-items: center; font-weight: 600; position: relative; z-index: 3;">
                    <span>{step_num}</span>
                    <div style="position: absolute; top: 35px; left: 50%; transform: translateX(-50%); 
                              white-space: nowrap; font-size: 0.8rem; font-weight: 500; color: #888;">
                        {labels[i]}
                    </div>
                </div>
            """
    
    progress_html += "</div>"
    
    st.markdown(progress_html, unsafe_allow_html=True)