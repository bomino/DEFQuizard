import streamlit as st
from ..ui import load_css, display_logo, navigate_to
from ..auth import authenticate, add_user

def login_page():
    # Apply custom CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Display logo
    display_logo()
    
    st.title("Forklift Operator Training Portal")
    
    # Using a container for the login card
    login_container = st.container()
    
    with login_container:
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", key="login_button"):
                is_authenticated, role, name = authenticate(username, password)
                if is_authenticated:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.session_state.name = name
                    navigate_to("quiz")
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            new_username = st.text_input("Username", key="register_username")
            new_password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            full_name = st.text_input("Full Name")
            
            if st.button("Register", key="register_button"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not new_username or not new_password or not full_name:
                    st.error("All fields are required")
                else:
                    success, message = add_user(new_username, new_password, full_name)
                    if success:
                        st.success(message)
                        st.info("You can now login with your credentials")
                    else:
                        st.error(message)
        
        st.markdown('</div>', unsafe_allow_html=True)