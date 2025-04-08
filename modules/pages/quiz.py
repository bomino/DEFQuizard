import streamlit as st
import random
import base64
import datetime
import time
from modules.ui import load_css, display_logo, navigate_to, apply_custom_css_class
from modules.data_manager import load_questions, save_quiz_score, load_user_settings, save_user_settings
from modules.certificate import create_certificate

def quiz_page():
    """Main function for the quiz page with enhanced features"""
    # Apply custom CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Display logo
    display_logo()
    
    # Quiz title with badge
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <h1 style="margin: 0; margin-right: 15px;">Forklift Operator Safety Quiz</h1>
            <span style="background-color: #e3f2fd; color: #1E88E5; padding: 5px 10px; 
                   border-radius: 20px; font-size: 0.8rem; font-weight: 500;">
                OSHA Compliant
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Define helper functions first before using them
    def get_category_scores(questions):
        """Calculate scores by category"""
        category_scores = {}
        for idx, question in enumerate(questions):
            category = question.get("category", "General")
            if category not in category_scores:
                category_scores[category] = {"correct": 0, "total": 0}
            
            category_scores[category]["total"] += 1
            if idx in st.session_state.correct_answers:
                category_scores[category]["correct"] += 1
        
        return category_scores

    def check_answer(selected_option, question_idx):
        """Handle answer submission"""
        question = st.session_state.quiz_questions[question_idx]
        correct_answer = question["answer"]
        
        # Store the user's selection
        st.session_state.selected_answers[question_idx] = selected_option
        
        if selected_option == correct_answer:
            st.session_state.score += 1
            st.session_state.correct_answers.append(question_idx)
            return True
        else:
            st.session_state.incorrect_answers.append(question_idx)
            return False

    def next_question():
        """Go to next question or complete quiz"""
        if st.session_state.current_question < len(st.session_state.quiz_questions) - 1:
            st.session_state.current_question += 1
            st.session_state.answered = False
        else:
            st.session_state.quiz_complete = True
            st.session_state.quiz_in_progress = False
            
            # Save the score when quiz is complete
            score = st.session_state.score
            max_score = len(st.session_state.quiz_questions)
            save_quiz_score(
                st.session_state.username, 
                score, 
                max_score,
                categories=get_category_scores(st.session_state.quiz_questions)
            )

    def prev_question():
        """Go to previous question"""
        if st.session_state.current_question > 0:
            st.session_state.current_question -= 1
            st.session_state.answered = True  # Allow reviewing previous answers

    def restart_quiz():
        """Reset quiz state to start over"""
        # Clear all quiz-related session state
        if 'quiz_questions' in st.session_state:
            del st.session_state.quiz_questions
        if 'current_question' in st.session_state:
            del st.session_state.current_question
        if 'score' in st.session_state:
            del st.session_state.score
        if 'answered' in st.session_state:
            del st.session_state.answered
        if 'quiz_complete' in st.session_state:
            del st.session_state.quiz_complete
        if 'quiz_in_progress' in st.session_state:
            del st.session_state.quiz_in_progress
        if 'correct_answers' in st.session_state:
            del st.session_state.correct_answers
        if 'incorrect_answers' in st.session_state:
            del st.session_state.incorrect_answers
        if 'selected_answers' in st.session_state:
            del st.session_state.selected_answers
        if 'quiz_timer_start' in st.session_state:
            del st.session_state.quiz_timer_start
        if 'quiz_timer_remaining' in st.session_state:
            del st.session_state.quiz_timer_remaining
    
    # Initialize all quiz-related session state variables if they don't exist
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    
    if 'score' not in st.session_state:
        st.session_state.score = 0
    
    if 'answered' not in st.session_state:
        st.session_state.answered = False
    
    if 'quiz_complete' not in st.session_state:
        st.session_state.quiz_complete = False
    
    if 'quiz_in_progress' not in st.session_state:
        st.session_state.quiz_in_progress = False
    
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = []
    
    if 'incorrect_answers' not in st.session_state:
        st.session_state.incorrect_answers = []
    
    if 'selected_answers' not in st.session_state:
        st.session_state.selected_answers = {}
    
    # Initialize timer if it's enabled
    if 'quiz_timer_enabled' not in st.session_state:
        # Default to no timer
        st.session_state.quiz_timer_enabled = False
        st.session_state.quiz_timer_duration = 0
    
    if 'quiz_timer_start' not in st.session_state and st.session_state.quiz_timer_enabled:
        st.session_state.quiz_timer_start = time.time()
        st.session_state.quiz_timer_remaining = st.session_state.quiz_timer_duration * 60
    
    # Load all questions
    all_questions = load_questions()
    
    # Check if there are any questions to show
    if not all_questions:
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.warning("No questions are available. Please contact your administrator.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # MAIN FLOW: Handle different quiz states
    # 1. Quiz completed state
    if st.session_state.quiz_complete and len(st.session_state.quiz_questions) > 0:
        score = st.session_state.score
        max_score = len(st.session_state.quiz_questions)
        percentage = (score / max_score) * 100
        
        # Calculate category-wise performance
        category_performance = get_category_scores(st.session_state.quiz_questions)
        
        st.markdown('<div class="quiz-card result-card">', unsafe_allow_html=True)
        
        # Display confetti for good scores
        if percentage >= 80:
            st.balloons()
        
        # Show different messages based on score
        if percentage >= 90:
            st.success("🏆 Excellent! You've demonstrated exceptional knowledge of forklift safety!")
        elif percentage >= 80:
            st.success("✅ Great job! You have a solid understanding of forklift safety.")
        elif percentage >= 70:
            st.warning("📝 Good effort! Review the areas where you made mistakes before operating equipment.")
        else:
            st.error("❌ Please review the forklift safety manual and try again. Additional training is recommended.")
        
        # Display score with progress bar
        st.markdown(f"### Your Score: {score}/{max_score} ({percentage:.1f}%)")
        st.progress(percentage/100)
        
        # Show completion time if timer was enabled
        if st.session_state.quiz_timer_enabled:
            elapsed_time = time.time() - st.session_state.quiz_timer_start
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            st.info(f"⏱️ Completion Time: {minutes} minutes, {seconds} seconds")
        
        # Display category-wise performance
        st.markdown("### Performance by Category")
        
        for category, data in category_performance.items():
            correct = data["correct"]
            total = data["total"]
            cat_percentage = (correct / total) * 100 if total > 0 else 0
            
            # Choose color based on performance
            if cat_percentage >= 80:
                color = "#4CAF50"  # Green
            elif cat_percentage >= 70:
                color = "#FF9800"  # Orange
            else:
                color = "#F44336"  # Red
            
            st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span><strong>{category}</strong></span>
                        <span>{correct}/{total} ({cat_percentage:.1f}%)</span>
                    </div>
                    <div style="width: 100%; background-color: #f0f0f0; border-radius: 10px; height: 10px;">
                        <div style="width: {cat_percentage}%; background-color: {color}; height: 10px; border-radius: 10px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Generate certificate for passing score
        if percentage >= 80:
            st.markdown("### Certificate of Completion")
            st.markdown('<div class="certificate-container">', unsafe_allow_html=True)
            
            # Generate a unique certificate ID
            import hashlib
            cert_id = hashlib.md5(f"{st.session_state.name}_{percentage}_{datetime.datetime.now()}".encode()).hexdigest()[:8].upper()
            
            cert_html = create_certificate(
                st.session_state.name, 
                f"{percentage:.1f}", 
                datetime.datetime.now().strftime("%B %d, %Y"),
                cert_id
            )
            
            b64 = base64.b64encode(cert_html.encode()).decode()
            download_button = f'<a href="data:text/html;base64,{b64}" download="forklift_safety_certificate.html" class="certificate-button">Download Certificate</a>'
            st.markdown(download_button, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Review incorrect answers
        if st.session_state.incorrect_answers:
            with st.expander("Review Incorrect Answers"):
                for q_idx in st.session_state.incorrect_answers:
                    question = st.session_state.quiz_questions[q_idx]
                    selected = st.session_state.selected_answers.get(q_idx)
                    
                    st.markdown(f"""
                        <div style="margin-bottom: 20px; padding: 15px; border-left: 3px solid #F44336; background-color: rgba(244, 67, 54, 0.05);">
                            <p style="font-weight: 600; margin-bottom: 10px;">{question["question"]}</p>
                            <p style="color: #F44336; margin-bottom: 5px;">
                                <span style="font-weight: 600;">Your answer:</span> {question["options"][selected]}
                            </p>
                            <p style="color: #4CAF50; margin-bottom: 10px;">
                                <span style="font-weight: 600;">Correct answer:</span> {question["options"][question["answer"]]}
                            </p>
                            <p style="font-style: italic; color: #555;">
                                <span style="font-weight: 600;">Explanation:</span> {question["explanation"]}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("View My Scores", key="view_scores_btn", use_container_width=True):
                navigate_to("scores")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Take Quiz Again", key="restart_quiz_btn", use_container_width=True):
                restart_quiz()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. Quiz in progress state
    elif st.session_state.quiz_in_progress and len(st.session_state.quiz_questions) > 0:
        current_q = st.session_state.quiz_questions[st.session_state.current_question]
        
        # Calculate progress percentage
        progress_pct = (st.session_state.current_question) / len(st.session_state.quiz_questions)
        
        # Display timer if enabled
        if st.session_state.quiz_timer_enabled:
            elapsed = time.time() - st.session_state.quiz_timer_start
            remaining = max(0, st.session_state.quiz_timer_duration * 60 - elapsed)
            
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            
            # Display timer with different colors based on remaining time
            if remaining <= 60:  # Last minute
                st.markdown(f"""
                    <div style="text-align: right; color: #F44336; font-weight: 600; margin-bottom: 10px;">
                        ⏱️ Time Remaining: {minutes}:{seconds:02d}
                    </div>
                """, unsafe_allow_html=True)
            elif remaining <= 300:  # Last 5 minutes
                st.markdown(f"""
                    <div style="text-align: right; color: #FF9800; font-weight: 600; margin-bottom: 10px;">
                        ⏱️ Time Remaining: {minutes}:{seconds:02d}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="text-align: right; color: #1E88E5; font-weight: 600; margin-bottom: 10px;">
                        ⏱️ Time Remaining: {minutes}:{seconds:02d}
                    </div>
                """, unsafe_allow_html=True)
            
            # Auto-submit quiz if time runs out
            if remaining <= 0 and not st.session_state.quiz_complete:
                st.session_state.quiz_complete = True
                st.session_state.quiz_in_progress = False
                
                # Save the score when quiz is complete
                score = st.session_state.score
                max_score = len(st.session_state.quiz_questions)
                save_quiz_score(st.session_state.username, score, max_score)
                st.rerun()
        
        # Show progress
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-weight: 500;">Question {st.session_state.current_question + 1} of {len(st.session_state.quiz_questions)}</span>
                <span style="color: #1E88E5; font-weight: 600;">Score: {st.session_state.score}/{st.session_state.current_question if st.session_state.answered else st.session_state.current_question+1}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.progress(progress_pct)
        
        # Display category badge
        category = current_q.get("category", "General")
        st.markdown(f"""
            <div style="margin-bottom: 15px;">
                <span style="background-color: #e3f2fd; color: #1E88E5; padding: 3px 10px; 
                      border-radius: 15px; font-size: 0.8rem; font-weight: 500;">
                    {category}
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        # Question card
        st.markdown('<div class="quiz-card question-card">', unsafe_allow_html=True)
        
        # Display the question
        st.subheader(current_q["question"])
        
        # Use radio buttons for options
        selected_option = st.radio(
            "Select your answer:",
            options=range(len(current_q["options"])),
            format_func=lambda x: current_q["options"][x],
            key=f"q{st.session_state.current_question}"
        )
        
        # Submit button
        if not st.session_state.answered:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Submit Answer", key=f"submit_btn_{st.session_state.current_question}", use_container_width=True):
                is_correct = check_answer(selected_option, st.session_state.current_question)
                st.session_state.answered = True
                
                if is_correct:
                    st.success("✅ Correct!")
                else:
                    correct_answer_text = current_q["options"][current_q["answer"]]
                    st.error(f"❌ Incorrect! The correct answer is: {correct_answer_text}")
                
                # Show explanation
                st.info(f"Explanation: {current_q['explanation']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation buttons (only show after answering)
        if st.session_state.answered:
            col1, col2, col3 = st.columns([1, 1, 2])
            
            # Previous button (if not on first question)
            with col1:
                if st.session_state.current_question > 0:
                    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
                    if st.button("← Previous", key=f"prev_btn_{st.session_state.current_question}", use_container_width=True):
                        prev_question()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Next button
            with col3:
                # Different text if it's the last question
                button_text = "Finish Quiz" if st.session_state.current_question == len(st.session_state.quiz_questions) - 1 else "Next Question →"
                
                st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                if st.button(button_text, key=f"next_btn_{st.session_state.current_question}", use_container_width=True):
                    next_question()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)

        # Display quiz progress at the bottom
        st.markdown("""
            <div style="margin-top: 20px; text-align: center; color: #757575; font-size: 0.9rem;">
                Answer all questions to complete the quiz. A score of 80% or higher is required to pass.
            </div>
        """, unsafe_allow_html=True)

    # 3. Quiz setup/start state
    else:
        # Quiz Settings
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        
        st.markdown("""
            <h3 style="margin-bottom: 20px;">Quiz Settings</h3>
            <p style="margin-bottom: 20px;">Configure your quiz preferences before starting.</p>
        """, unsafe_allow_html=True)
        
        # Quiz options in columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Number of questions option
            max_questions = len(all_questions)
            min_questions = min(5, max_questions)  # Ensure min value is not greater than max

            if max_questions > min_questions:
                num_questions = st.slider(
                    "Number of Questions", 
                    min_value=min_questions, 
                    max_value=max_questions,
                    value=min(max_questions, 10),
                    step=1 if max_questions < 10 else 5  # Smaller step if few questions
                )
            else:
                # If we have very few questions, just use all of them
                num_questions = max_questions
                st.info(f"Using all available questions ({num_questions}).")
            
            # Filter by category
            categories = sorted(set(q.get("category", "General") for q in all_questions))
            selected_categories = st.multiselect(
                "Filter by Categories", 
                options=categories,
                default=categories
            )
        
        with col2:
            # Time limit option
            timer_enabled = st.checkbox("Enable Time Limit", value=False)
            timer_minutes = st.slider(
                "Time Limit (minutes)", 
                min_value=5, 
                max_value=60, 
                value=20,
                step=5,
                disabled=not timer_enabled
            )
            
            # Randomize questions
            randomize = st.checkbox("Randomize Questions", value=True)
        
        # Filter questions based on user selections
        filtered_questions = [
            q for q in all_questions 
            if q.get("category", "General") in selected_categories
        ]
        
        # Make sure we have questions after filtering
        if not filtered_questions:
            st.warning("No questions match your selected categories. Please select different categories.")
        else:
            # Limit to selected number of questions
            if len(filtered_questions) > num_questions:
                if randomize:
                    # Random selection
                    selected_questions = random.sample(filtered_questions, num_questions)
                else:
                    # Take first N questions
                    selected_questions = filtered_questions[:num_questions]
            else:
                selected_questions = filtered_questions
            
            # Start quiz button
            start_col1, start_col2, start_col3 = st.columns([1, 2, 1])
            with start_col2:
                if st.button("Start Quiz", key="start_quiz_btn", use_container_width=True):
                    st.session_state.quiz_questions = selected_questions
                    st.session_state.current_question = 0
                    st.session_state.score = 0
                    st.session_state.answered = False
                    st.session_state.quiz_complete = False
                    st.session_state.quiz_in_progress = True
                    st.session_state.correct_answers = []
                    st.session_state.incorrect_answers = []
                    st.session_state.selected_answers = {}
                    
                    # Set timer if enabled
                    st.session_state.quiz_timer_enabled = timer_enabled
                    st.session_state.quiz_timer_duration = timer_minutes
                    if timer_enabled:
                        st.session_state.quiz_timer_start = time.time()
                        st.session_state.quiz_timer_remaining = timer_minutes * 60
                    
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)