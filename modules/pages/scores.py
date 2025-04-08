import streamlit as st
import pandas as pd
from ..ui import load_css, display_logo, navigate_to
from ..data_manager import get_user_scores, SCORES_FILE
import json

def scores_page():
    # Apply custom CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Display logo
    display_logo()
    
    st.title("My Quiz Scores")
    
    # Load the scores directly from the file to ensure we have the latest data
    with open(SCORES_FILE, "r") as f:
        all_scores = json.load(f)
    
    user_scores = [s for s in all_scores if s["username"] == st.session_state.username]
    
    if not user_scores:
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.info("You haven't taken any quizzes yet. Take a quiz to see your scores here!")
        
        if st.button("Take a Quiz", key="take_quiz_from_scores"):
            navigate_to("quiz")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Convert to DataFrame for easy display
        df = pd.DataFrame(user_scores)
        
        # Make sure we're sorting correctly by timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values("timestamp", ascending=False)
        
        # Show latest score
        latest = df.iloc[0]
        
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Latest Quiz Score", f"{latest['percentage']:.1f}%")
        with col2:
            st.metric("Taken on", latest['timestamp'].strftime("%b %d, %Y"))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show score progression over time (properly sorted)
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### Score Progression")
        chart_df = df.sort_values("timestamp")[["timestamp", "percentage"]]
        if len(chart_df) > 1:  # Only show chart if more than one attempt
            st.line_chart(chart_df.set_index("timestamp"))
        else:
            st.info("Complete more quizzes to see your score progression over time.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show stats
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            # Show best score
            best_score = df.loc[df["percentage"].idxmax()]
            st.metric("Your Best Score", f"{best_score['percentage']:.1f}%")
        with col2:
            # Show average score
            avg_score = df["percentage"].mean()
            st.metric("Your Average Score", f"{avg_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show all attempts
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### All Your Attempts")
        st.dataframe(
            df[["timestamp", "score", "max_score", "percentage"]].reset_index(drop=True),
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Take quiz again button
        if st.button("Take Quiz Again", key="take_quiz_again_from_scores"):
            navigate_to("quiz")
            st.rerun()