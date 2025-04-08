# modules/navigation.py
import streamlit as st

def navigate_to(page):
    st.session_state.current_page = page
    # Reset quiz state when navigating away from quiz
    if page != "quiz":
        if "current_question" in st.session_state:
            del st.session_state.current_question
        if "score" in st.session_state:
            del st.session_state.score
        if "answered" in st.session_state:
            del st.session_state.answered
        if "quiz_complete" in st.session_state:
            del st.session_state.quiz_complete