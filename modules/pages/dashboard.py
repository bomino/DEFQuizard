import streamlit as st
import pandas as pd
import datetime
from modules.ui import load_css, display_logo, apply_custom_css_class, navigate_to
from modules.data_manager import get_user_scores, get_score_statistics, load_questions, load_settings

def dashboard_page():
    """
    Modern dashboard interface for users showing their performance metrics,
    upcoming certifications, and quick access to key functions
    """
    # Apply custom CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Display logo
    display_logo()
    
    # Welcome header with user name
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h1 style="margin: 0;">Welcome, {st.session_state.name}</h1>
            <span style="background-color: #e3f2fd; color: #1E88E5; padding: 5px 15px; 
                   border-radius: 20px; font-size: 0.9rem; font-weight: 500;">
                {st.session_state.role.title()}
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Get user data
    username = st.session_state.username
    user_scores = get_user_scores(username)
    user_stats = get_score_statistics(username)
    questions = load_questions()
    settings = load_settings()
    
    # Quick actions buttons in a grid
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("🚀 Start New Quiz", key="start_quiz_btn", use_container_width=True):
            navigate_to("quiz")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("📊 View All Scores", key="view_scores_btn", use_container_width=True):
            navigate_to("scores")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.role == "admin":
        with col3:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("⚙️ Admin Panel", key="admin_panel_btn", use_container_width=True):
                navigate_to("admin")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main dashboard content in two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Performance overview card
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### Your Performance")
        
        # Check if the user has taken any quizzes
        if not user_scores:
            st.info("You haven't taken any quizzes yet. Start a quiz to see your performance.")
        else:
            # Key metrics in a row
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                avg_score = user_stats["avg_score"]
                st.metric(
                    "Average Score", 
                    f"{avg_score:.1f}%",
                    delta=None if user_stats["total_attempts"] < 2 else f"{user_scores[0]['percentage'] - avg_score:.1f}%",
                    delta_color="normal"
                )
            
            with metric_col2:
                highest_score = user_stats["highest_score"]
                st.metric("Best Score", f"{highest_score:.1f}%")
            
            with metric_col3:
                total_quizzes = user_stats["total_attempts"]
                st.metric("Quizzes Taken", f"{total_quizzes}")
            
            # Score progression chart
            if len(user_scores) > 1:
                st.markdown("#### Score Progression")
                
                # Create DataFrame for chart
                df = pd.DataFrame(user_scores)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.sort_values("timestamp")
                
                # Add passing score reference line
                passing_score = settings.get("passing_score", 80)
                chart_data = pd.DataFrame({
                    "timestamp": df["timestamp"],
                    "Your Score": df["percentage"],
                    "Passing Score": [passing_score] * len(df)
                })
                
                st.line_chart(chart_data.set_index("timestamp"))
            
            # Latest quiz info
            latest = user_scores[0]
            st.markdown("#### Latest Quiz Results")
            
            # Format date
            latest_date = datetime.datetime.strptime(latest["timestamp"], "%Y-%m-%d %H:%M:%S")
            formatted_date = latest_date.strftime("%B %d, %Y at %I:%M %p")
            
            # Calculate pass/fail status
            passing_score = settings.get("passing_score", 80)
            passed = latest["percentage"] >= passing_score
            
            # Display with appropriate colors based on pass/fail
            if passed:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4CAF50; border-radius: 4px; margin-bottom: 15px;">
                        <p style="margin: 0; color: #2E7D32; font-weight: 500;">You scored {latest["percentage"]:.1f}% on {formatted_date}</p>
                        <p style="margin: 5px 0 0 0; color: #388E3C;">Result: <span style="font-weight: 500;">PASSED</span> (minimum {passing_score}%)</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: rgba(244, 67, 54, 0.1); border-left: 4px solid #F44336; border-radius: 4px; margin-bottom: 15px;">
                        <p style="margin: 0; color: #C62828; font-weight: 500;">You scored {latest["percentage"]:.1f}% on {formatted_date}</p>
                        <p style="margin: 5px 0 0 0; color: #D32F2F;">Result: <span style="font-weight: 500;">FAILED</span> (minimum {passing_score}%)</p>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Category performance (if available)
        if user_scores and any("categories" in score for score in user_scores):
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            st.markdown("### Performance by Category")
            
            # Aggregate category data from all attempts
            categories = {}
            
            for score in user_scores:
                if "categories" in score:
                    for category, data in score["categories"].items():
                        if category not in categories:
                            categories[category] = {
                                "total_questions": 0,
                                "correct_answers": 0
                            }
                        
                        categories[category]["total_questions"] += data["total"]
                        categories[category]["correct_answers"] += data["correct"]
            
            if categories:
                # Calculate percentages and create visual bar chart
                for category in categories:
                    total = categories[category]["total_questions"]
                    correct = categories[category]["correct_answers"]
                    percentage = (correct / total) * 100 if total > 0 else 0
                    categories[category]["percentage"] = percentage
                    
                    # Color based on percentage
                    if percentage >= 80:
                        color = "#4CAF50"  # Green
                    elif percentage >= 70:
                        color = "#FF9800"  # Orange
                    else:
                        color = "#F44336"  # Red
                    
                    st.markdown(f"""
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-weight: 500;">{category}</span>
                                <span>{correct}/{total} ({percentage:.1f}%)</span>
                            </div>
                            <div style="width: 100%; background-color: #f0f0f0; border-radius: 10px; height: 10px;">
                                <div style="width: {percentage}%; background-color: {color}; height: 10px; border-radius: 10px;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Category performance data is not available for your quizzes.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Certification status card
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### Certification Status")
        
        # Check for valid passing score
        has_valid_cert = False
        if user_scores:
            passing_score = settings.get("passing_score", 80)
            validity_days = settings.get("certificate_validity_days", 365)
            
            # Find the most recent passing score
            passing_scores = [s for s in user_scores if s["percentage"] >= passing_score]
            if passing_scores:
                last_pass = passing_scores[0]  # Already sorted by date
                cert_date = datetime.datetime.strptime(last_pass["timestamp"], "%Y-%m-%d %H:%M:%S")
                expiry_date = cert_date + datetime.timedelta(days=validity_days)
                
                # Check if certificate is still valid
                now = datetime.datetime.now()
                if now < expiry_date:
                    has_valid_cert = True
                    
                    # Calculate days remaining
                    days_remaining = (expiry_date - now).days
                    
                    # Display certificate status with nice styling
                    st.markdown(f"""
                        <div style="text-align: center; margin-bottom: 15px;">
                            <div style="font-size: 64px; color: #4CAF50; margin-bottom: 10px;">
                                <i>✓</i>
                            </div>
                            <p style="font-weight: 600; font-size: 18px; color: #4CAF50; margin-bottom: 5px;">
                                Certified Operator
                            </p>
                            <p style="color: #666; margin-bottom: 15px;">
                                Valid until {expiry_date.strftime("%B %d, %Y")}
                            </p>
                            <div style="background-color: #e8f5e9; padding: 8px; border-radius: 10px;">
                                <p style="margin: 0; color: #388E3C;">
                                    {days_remaining} days remaining
                                </p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Download certificate button
                    from modules.certificate import create_certificate
                    
                    cert_html = create_certificate(
                        st.session_state.name, 
                        f"{last_pass['percentage']:.1f}", 
                        cert_date.strftime("%B %d, %Y"),
                        last_pass.get("id", "")
                    )
                    
                    import base64
                    b64 = base64.b64encode(cert_html.encode()).decode()
                    download_button = f'<a href="data:text/html;base64,{b64}" download="forklift_certificate.html" class="certificate-button">Download Certificate</a>'
                    st.markdown(download_button, unsafe_allow_html=True)
                else:
                    # Expired certificate
                    st.markdown(f"""
                        <div style="text-align: center; margin-bottom: 15px;">
                            <div style="font-size: 64px; color: #FF9800; margin-bottom: 10px;">
                                <i>!</i>
                            </div>
                            <p style="font-weight: 600; font-size: 18px; color: #FF9800; margin-bottom: 5px;">
                                Certification Expired
                            </p>
                            <p style="color: #666; margin-bottom: 15px;">
                                Your certificate expired on {expiry_date.strftime("%B %d, %Y")}
                            </p>
                            <div style="background-color: #fff3e0; padding: 8px; border-radius: 10px;">
                                <p style="margin: 0; color: #E65100;">
                                    Please take a new quiz to renew
                                </p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                # No passing scores yet
                st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 15px;">
                        <div style="font-size: 64px; color: #F44336; margin-bottom: 10px;">
                            <i>✗</i>
                        </div>
                        <p style="font-weight: 600; font-size: 18px; color: #F44336; margin-bottom: 5px;">
                            Not Certified
                        </p>
                        <p style="color: #666; margin-bottom: 15px;">
                            You need to pass a quiz with at least {passing_score}% to become certified
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            # No quizzes taken
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 15px;">
                    <div style="font-size: 64px; color: #9E9E9E; margin-bottom: 10px;">
                        <i>?</i>
                    </div>
                    <p style="font-weight: 600; font-size: 18px; color: #9E9E9E; margin-bottom: 5px;">
                        No Quizzes Taken
                    </p>
                    <p style="color: #666; margin-bottom: 15px;">
                        Take a quiz to earn your certification
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick stats card
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### Quick Stats")
        
        # Total questions available
        total_questions = len(questions)
        
        # Categories available
        categories = sorted(set(q.get("category", "General") for q in questions))
        
        # Total users (if admin)
        if st.session_state.role == "admin":
            from modules.data_manager import load_users
            total_users = len(load_users())
            
            st.markdown(f"""
                <p><strong>Total Questions:</strong> {total_questions}</p>
                <p><strong>Categories:</strong> {len(categories)}</p>
                <p><strong>Total Users:</strong> {total_users}</p>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <p><strong>Total Questions:</strong> {total_questions}</p>
                <p><strong>Categories:</strong> {len(categories)}</p>
            """, unsafe_allow_html=True)
        
        # List categories
        with st.expander("View All Categories"):
            for category in categories:
                cat_count = sum(1 for q in questions if q.get("category", "General") == category)
                st.markdown(f"- **{category}**: {cat_count} questions")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Upcoming features card (for visual balance)
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### Quick Tips")
        
        st.markdown("""
            <div style="padding: 10px; border-left: 3px solid #2196F3; margin-bottom: 10px; background-color: #f1f8fe;">
                <p style="margin: 0; font-weight: 500;">Pre-shift Safety Check</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Always perform a complete pre-shift inspection of your forklift before operating.</p>
            </div>
            
            <div style="padding: 10px; border-left: 3px solid #4CAF50; margin-bottom: 10px; background-color: #f1f9f1;">
                <p style="margin: 0; font-weight: 500;">Load Stability</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem;">Center the load on the forks and tilt backward to stabilize.</p>
            </div>
            
            <div style="padding: 10px; border-left: 3px solid #FF9800; margin-bottom: 10px; background-color: #fffaf0;">
                <p style="margin: 0; font-weight: 500;">Visibility</p>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem;">When carrying a load that blocks forward vision, drive in reverse.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Bottom card with upcoming trainings
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown("### OSHA Compliance Calendar")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="text-align: center; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; height: 100%;">
                <p style="font-weight: 600; color: #1E88E5;">Annual Refresher Training</p>
                <p style="color: #666;">Required once per year for all operators</p>
                <p style="font-size: 0.9rem; margin-top: 10px;">
                    <span style="background-color: #e3f2fd; color: #1565C0; padding: 3px 8px; border-radius: 12px;">OSHA Required</span>
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="text-align: center; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; height: 100%;">
                <p style="font-weight: 600; color: #4CAF50;">Load Handling Workshop</p>
                <p style="color: #666;">Specialized training on safe load management</p>
                <p style="font-size: 0.9rem; margin-top: 10px;">
                    <span style="background-color: #e8f5e9; color: #2E7D32; padding: 3px 8px; border-radius: 12px;">Recommended</span>
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="text-align: center; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; height: 100%;">
                <p style="font-weight: 600; color: #FF9800;">Hazard Recognition</p>
                <p style="color: #666;">Training on identifying workplace hazards</p>
                <p style="font-size: 0.9rem; margin-top: 10px;">
                    <span style="background-color: #fff3e0; color: #E65100; padding: 3px 8px; border-radius: 12px;">Optional</span>
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)