# modules/pages/admin.py

import streamlit as st
import pandas as pd
import os
import datetime
import base64
from ..ui import load_css, display_logo, apply_custom_css_class, show_notification
from ..data_manager import (
    load_questions, load_scores, load_users, load_settings,
    save_questions, save_users, save_settings, LOGO_PATH,
    get_category_statistics, get_score_statistics,
    clear_all_scores, clear_user_scores
)
from ..auth import hash_password
from ..certificate import create_certificate  # Add this import

# Import database management tab if available
try:
    from .admin_db import database_management
    HAS_DB_MANAGEMENT = True
except ImportError:
    HAS_DB_MANAGEMENT = False

def admin_page():
    """Main admin panel interface with tabs for different management functions"""
    # Apply custom CSS
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # Display logo
    display_logo()
    
    # Admin header with badge
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <h1 style="margin: 0; margin-right: 15px;">Admin Panel</h1>
            <span style="background-color: #ffebee; color: #e53935; padding: 5px 10px; 
                   border-radius: 20px; font-size: 0.8rem; font-weight: 500;">
                Administrator Access
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Create tabs with enhanced styling
    tabs = [
        "📊 Dashboard", 
        "❓ Manage Questions", 
        "👤 User Management", 
        "🔧 System Settings",
        "🎨 Branding"
    ]
    
    # Add database tab if available
    if HAS_DB_MANAGEMENT:
        tabs.append("💾 Database")
    
    # Create tabs
    all_tabs = st.tabs(tabs)
    
    with all_tabs[0]:
        admin_dashboard()
    
    with all_tabs[1]:
        manage_questions()
    
    with all_tabs[2]:
        manage_users()
    
    with all_tabs[3]:
        system_settings()
        
    with all_tabs[4]:
        branding_settings()
    
    # Database management tab if available
    if HAS_DB_MANAGEMENT and len(all_tabs) > 5:
        with all_tabs[5]:
            database_management()

# The rest of the file remains the same
# Keep all existing functions: admin_dashboard, manage_questions, manage_users, system_settings, branding_settings
# ...

def admin_dashboard():
    """Dashboard with key metrics and charts"""
    st.subheader("Performance Dashboard")
    
    # Load data
    scores = load_scores()
    users = load_users()
    questions = load_questions()
    
    if not scores:
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.info("No quiz scores recorded yet. Data will appear here once users start taking quizzes.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(scores)
    
    # Key metrics in cards
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    
    # First row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_quizzes = len(scores)
        st.metric("Total Quizzes Taken", f"{total_quizzes}")
    
    with col2:
        avg_score = df["percentage"].mean()
        st.metric("Average Score", f"{avg_score:.1f}%")
    
    with col3:
        passing_score = 80  # Could be from settings
        passing_rate = (df["percentage"] >= passing_score).mean() * 100
        st.metric("Pass Rate", f"{passing_rate:.1f}%")
    
    with col4:
        active_users = df["username"].nunique()
        total_users = len(users)
        user_activity = (active_users / total_users) * 100 if total_users > 0 else 0
        st.metric("User Activity", f"{user_activity:.1f}%", help=f"{active_users} out of {total_users} users have taken quizzes")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Second row - Recent activity & trending
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Recent Quiz Activity")
        # Sort by timestamp to get recent attempts
        recent_df = df.sort_values("timestamp", ascending=False).head(5)
        
        # Add name column from users
        recent_df["name"] = recent_df["username"].apply(lambda u: users.get(u, {}).get("name", "Unknown"))
        
        # Format timestamp
        recent_df["date"] = pd.to_datetime(recent_df["timestamp"]).dt.strftime("%b %d, %Y")
        
        # Show recent activity table
        st.dataframe(
            recent_df[["name", "date", "percentage"]].rename(columns={
                "name": "User",
                "date": "Date",
                "percentage": "Score (%)"
            }),
            use_container_width=True
        )
    
    with col2:
        st.markdown("### Score Trends")
        # Group by date and calculate average score
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        trend_df = df.groupby("date")["percentage"].mean().reset_index()
        trend_df["date"] = pd.to_datetime(trend_df["date"])
        
        # Plot trend
        st.line_chart(trend_df.set_index("date"))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Third row - Category performance & User performance
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Performance by Category")
        
        # Get category statistics
        category_stats = get_category_statistics()
        
        if category_stats:
            # Convert to DataFrame for visualization
            cat_df = pd.DataFrame([
                {
                    "Category": cat,
                    "Correct (%)": data["percentage"],
                    "Total Questions": data["total_questions"]
                }
                for cat, data in category_stats.items()
            ])
            
            # Sort by percentage
            cat_df = cat_df.sort_values("Correct (%)", ascending=False)
            
            # Show as bar chart
            st.bar_chart(cat_df.set_index("Category")["Correct (%)"])
            
            # Show as table too
            st.dataframe(cat_df, use_container_width=True)
        else:
            st.info("No category data available yet.")
    
    with col2:
        st.markdown("### Top Performers")
        
        # Group by username and calculate stats
        user_stats = df.groupby("username").agg({
            "percentage": ["mean", "count"],
        }).reset_index()
        
        user_stats.columns = ["username", "avg_score", "attempts"]
        
        # Add name
        user_stats["name"] = user_stats["username"].apply(lambda u: users.get(u, {}).get("name", "Unknown"))
        
        # Sort by average score
        top_users = user_stats.sort_values("avg_score", ascending=False).head(5)
        
        # Format for display
        top_users["avg_score"] = top_users["avg_score"].round(1).astype(str) + "%"
        
        # Show top performers
        st.dataframe(
            top_users[["name", "avg_score", "attempts"]].rename(columns={
                "name": "User",
                "avg_score": "Average Score",
                "attempts": "Quizzes Taken"
            }),
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fourth row - Question difficulty analysis
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown("### Question Analysis")
    
    # Modify the question difficulty analysis section
    if "categories" in df.columns:
        # Calculate most challenging questions
        question_difficulty = {}
        
        for _, row in df.iterrows():
            if "question_performance" in row:
                for q_id, result in row["question_performance"].items():
                    if q_id not in question_difficulty:
                        question_difficulty[q_id] = {"attempts": 0, "correct": 0}
                    
                    question_difficulty[q_id]["attempts"] += 1
                    if result.get("correct", False):
                        question_difficulty[q_id]["correct"] += 1
        
        # Calculate difficulty percentage
        for q_id in question_difficulty:
            attempts = question_difficulty[q_id]["attempts"]
            correct = question_difficulty[q_id]["correct"]
            question_difficulty[q_id]["difficulty"] = 100 - ((correct / attempts) * 100 if attempts > 0 else 0)
        
        # Only proceed if we have question difficulty data
        if question_difficulty:
            # Convert to DataFrame
            q_diff_df = pd.DataFrame([
                {
                    "question_id": q_id,  # Using "question_id" instead of "id" to be more explicit
                    "difficulty": data["difficulty"],
                    "attempts": data["attempts"]
                }
                for q_id, data in question_difficulty.items()
            ])
            
            # Get question text
            questions_dict = {q["id"]: q for q in questions}
            
            # Add question text column - make sure we're using the correct column name
            if "question_id" in q_diff_df.columns:
                q_diff_df["question"] = q_diff_df["question_id"].apply(
                    lambda qid: questions_dict.get(qid, {}).get("question", "Unknown Question")
                )
                
                # Limit question text length
                q_diff_df["question"] = q_diff_df["question"].apply(lambda q: q[:50] + "..." if len(q) > 50 else q)
                
                # Sort by difficulty (hardest first)
                q_diff_df = q_diff_df.sort_values("difficulty", ascending=False).head(10)
                
                # Show most difficult questions
                st.subheader("Most Challenging Questions")
                st.dataframe(
                    q_diff_df[["question", "difficulty", "attempts"]].rename(columns={
                        "question": "Question",
                        "difficulty": "Difficulty Score",
                        "attempts": "Times Attempted"
                    }),
                    use_container_width=True
                )
            else:
                st.info("Detailed question analysis requires more quiz data.")
        else:
            st.info("Question difficulty analysis will be available after more quizzes are taken.")
    else:
        st.info("Detailed question analysis will be available after more quizzes are taken.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export data section
    with st.expander("Export Data"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Export all scores
            export_scores_csv = df.to_csv(index=False)
            st.download_button(
                label="Download All Scores (CSV)",
                data=export_scores_csv,
                file_name=f"forklift_quiz_scores_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Export user performance summary
            user_perf_df = df.groupby("username").agg({
                "percentage": ["mean", "min", "max", "count"]
            }).reset_index()
            
            user_perf_df.columns = ["username", "avg_score", "min_score", "max_score", "attempts"]
            user_perf_df["name"] = user_perf_df["username"].apply(lambda u: users.get(u, {}).get("name", "Unknown"))
            
            export_users_csv = user_perf_df.to_csv(index=False)
            st.download_button(
                label="Download User Summary (CSV)",
                data=export_users_csv,
                file_name=f"forklift_quiz_user_summary_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def manage_questions():
    """Question management interface"""
    st.subheader("Question Management")
    
    # Load questions
    questions = load_questions()
    
    # Question import/export section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### Import Questions")
        
        st.write("Upload a CSV file with quiz questions.")
        
        # Sample data for template
        sample_data = [
            {"id": 1, "question": "What should you do before operating a forklift?",
             "option1": "Check fuel only",
             "option2": "Full pre-shift inspection",
             "option3": "Test horn",
             "option4": "Load immediately",
             "answer": 1,
             "explanation": "OSHA requires a pre-shift inspection for safety.",
             "category": "Safety",
             "difficulty": "Basic"}
        ]
        sample_df = pd.DataFrame(sample_data)
        sample_csv = sample_df.to_csv(index=False)
        
        st.download_button(
            label="Download Template",
            data=sample_csv,
            file_name="question_template.csv",
            mime="text/csv",
            help="Download a CSV template for importing questions"
        )
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                
                # Validate the CSV structure
                required_columns = ["question", "option1", "option2", "option3", "option4", "answer", "explanation"]
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"CSV is missing these required columns: {', '.join(missing_columns)}")
                else:
                    # Preview the uploaded data
                    st.write("Preview of uploaded questions:")
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    # Confirm import
                    import_col1, import_col2 = st.columns([1, 1])
                    with import_col1:
                        replace_existing = st.checkbox("Replace all existing questions", value=False)
                    
                    with import_col2:
                        if st.button("Import Questions", key="import_questions_btn"):
                            # Load existing questions
                            if replace_existing:
                                questions = []
                            
                            # Get highest existing ID
                            next_id = max([q["id"] for q in questions], default=0) + 1
                            
                            # Convert DataFrame rows to question dictionaries
                            new_questions_count = 0
                            for _, row in df.iterrows():
                                new_q = {
                                    "id": next_id,
                                    "question": row["question"],
                                    "options": [row["option1"], row["option2"], row["option3"], row["option4"]],
                                    "answer": int(row["answer"]),
                                    "explanation": row["explanation"],
                                    "category": row.get("category", "General"),
                                    "difficulty": row.get("difficulty", "Intermediate")
                                }
                                questions.append(new_q)
                                next_id += 1
                                new_questions_count += 1
                            
                            # Save updated questions
                            save_questions(questions)
                            st.success(f"Successfully imported {new_questions_count} questions!")
                            
            except Exception as e:
                st.error(f"Error processing CSV file: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### Export Questions")
        
        if questions:
            # Convert questions to DataFrame format
            export_data = []
            for q in questions:
                q_data = {
                    "id": q["id"],
                    "question": q["question"],
                    "option1": q["options"][0] if len(q["options"]) > 0 else "",
                    "option2": q["options"][1] if len(q["options"]) > 1 else "",
                    "option3": q["options"][2] if len(q["options"]) > 2 else "",
                    "option4": q["options"][3] if len(q["options"]) > 3 else "",
                    "answer": q["answer"],
                    "explanation": q["explanation"],
                    "category": q.get("category", "General"),
                    "difficulty": q.get("difficulty", "Intermediate")
                }
                export_data.append(q_data)
            
            export_df = pd.DataFrame(export_data)
            
            # Statistics about questions
            total_questions = len(questions)
            categories_count = export_df["category"].value_counts().to_dict()
            difficulty_count = export_df["difficulty"].value_counts().to_dict()
            
            st.metric("Total Questions", total_questions)
            
            # Show statistics in expandable section
            with st.expander("Question Statistics"):
                st.markdown("#### Questions by Category")
                for category, count in categories_count.items():
                    st.markdown(f"- **{category}**: {count} questions")
                
                st.markdown("#### Questions by Difficulty")
                for difficulty, count in difficulty_count.items():
                    st.markdown(f"- **{difficulty}**: {count} questions")
            
            # Export options
            st.markdown("#### Export Options")
            
            # Filter by category option
            categories = sorted(set(q.get("category", "General") for q in questions))
            selected_categories = st.multiselect(
                "Filter by Categories", 
                options=categories,
                default=categories
            )
            
            # Generate CSV based on filters
            filtered_df = export_df[export_df["category"].isin(selected_categories)]
            csv = filtered_df.to_csv(index=False)
            
            st.download_button(
                label=f"Download Questions ({len(filtered_df)} questions)",
                data=csv,
                file_name=f"forklift_quiz_questions_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No questions to export.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Question management interface
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    
    # Tabs for different question management functions
    q_tab1, q_tab2, q_tab3 = st.tabs(["Add New Question", "Edit Questions", "Delete Questions"])
    
    with q_tab1:
        st.markdown("### Add New Question")
        
        with st.form(key="new_question_form"):
            new_question = st.text_area("Question", key="new_q", help="Enter the full question text")
            
            # Category selection (existing or new)
            categories = sorted(set(q.get("category", "General") for q in questions))
            category_type = st.radio("Category", ["Select Existing", "Create New"], horizontal=True)
            
            if category_type == "Select Existing":
                new_category = st.selectbox("Select Category", ["General"] + categories)
            else:
                new_category = st.text_input("New Category Name")
            
            # Difficulty selection
            difficulties = ["Basic", "Intermediate", "Advanced"]
            new_difficulty = st.select_slider("Difficulty Level", options=difficulties, value="Intermediate")
            
            # Options
            st.markdown("#### Answer Options")
            new_options = []
            cols = st.columns(2)
            for i in range(4):  # Assuming we always want 4 options
                col_idx = i % 2
                with cols[col_idx]:
                    new_opt = st.text_input(f"Option {i+1}", key=f"new_option_{i}")
                    new_options.append(new_opt)
            
            # Correct answer
            new_answer = st.selectbox(
                "Correct Answer",
                range(len(new_options)),
                format_func=lambda i: new_options[i] if new_options[i] else f"Option {i+1}"
            )
            
            # Explanation
            new_explanation = st.text_area("Explanation", key="new_explanation", 
                                          help="Provide explanation why the answer is correct")
            
            submit_new = st.form_submit_button("Add Question")
            
            if submit_new:
                if not new_question or "" in new_options or not new_explanation:
                    st.error("All fields are required")
                else:
                    # Load questions again in case they were updated
                    questions = load_questions()
                    
                    # Generate new ID
                    new_id = max([q["id"] for q in questions], default=0) + 1
                    
                    new_q = {
                        "id": new_id,
                        "question": new_question,
                        "options": new_options,
                        "answer": new_answer,
                        "explanation": new_explanation,
                        "category": new_category,
                        "difficulty": new_difficulty
                    }
                    
                    questions.append(new_q)
                    save_questions(questions)
                    st.success("New question added successfully!")
    
    with q_tab2:
        if questions:
            st.markdown("### Edit Existing Question")
            
            # Filter options
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                filter_category = st.selectbox(
                    "Filter by Category",
                    ["All"] + sorted(set(q.get("category", "General") for q in questions))
                )
            
            with filter_col2:
                filter_difficulty = st.selectbox(
                    "Filter by Difficulty",
                    ["All"] + sorted(set(q.get("difficulty", "Intermediate") for q in questions))
                )
            
            # Apply filters
            filtered_questions = questions
            if filter_category != "All":
                filtered_questions = [q for q in filtered_questions if q.get("category", "General") == filter_category]
            if filter_difficulty != "All":
                filtered_questions = [q for q in filtered_questions if q.get("difficulty", "Intermediate") == filter_difficulty]
            
            # Question selection
            question_titles = [f"Q{q['id']}: {q['question'][:50]}..." for q in filtered_questions]
            if not question_titles:
                st.warning("No questions match the selected filters.")
            else:
                selected_q_idx = st.selectbox(
                    "Select Question to Edit", 
                    range(len(filtered_questions)), 
                    format_func=lambda i: question_titles[i]
                )
                
                q_to_edit = filtered_questions[selected_q_idx]
                
                with st.form(key="edit_question_form"):
                    edited_question = st.text_area("Question", value=q_to_edit["question"])
                    
                    # Category selection
                    categories = sorted(set(q.get("category", "General") for q in questions))
                    edited_category = st.selectbox(
                        "Category", 
                        categories, 
                        index=categories.index(q_to_edit.get("category", "General")) if q_to_edit.get("category", "General") in categories else 0
                    )
                    
                    # Difficulty selection
                    difficulties = ["Basic", "Intermediate", "Advanced"]
                    edited_difficulty = st.select_slider(
                        "Difficulty Level", 
                        options=difficulties, 
                        value=q_to_edit.get("difficulty", "Intermediate")
                    )
                    
                    # Options
                    st.markdown("#### Answer Options")
                    edited_options = []
                    cols = st.columns(2)
                    for i, opt in enumerate(q_to_edit["options"]):
                        col_idx = i % 2
                        with cols[col_idx]:
                            edited_opt = st.text_input(f"Option {i+1}", value=opt, key=f"edit_option_{i}")
                            edited_options.append(edited_opt)
                    
                    edited_answer = st.selectbox(
                        "Correct Answer",
                        range(len(edited_options)),
                        format_func=lambda i: edited_options[i],
                        index=q_to_edit["answer"]
                    )
                    
                    edited_explanation = st.text_area("Explanation", value=q_to_edit["explanation"])
                    
                    submit_edit = st.form_submit_button("Save Changes")
                    
                    if submit_edit:
                        # Update the question in the original questions list
                        for i, q in enumerate(questions):
                            if q["id"] == q_to_edit["id"]:
                                questions[i]["question"] = edited_question
                                questions[i]["options"] = edited_options
                                questions[i]["answer"] = edited_answer
                                questions[i]["explanation"] = edited_explanation
                                questions[i]["category"] = edited_category
                                questions[i]["difficulty"] = edited_difficulty
                                break
                        
                        save_questions(questions)
                        st.success("Question updated successfully!")
        else:
            st.info("No questions available to edit. Add questions manually or import from CSV.")
    
    with q_tab3:
        if questions:
            st.markdown("### Delete Questions")
            
            # Filter options
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                delete_filter_category = st.selectbox(
                    "Filter by Category",
                    ["All"] + sorted(set(q.get("category", "General") for q in questions)),
                    key="delete_category_filter"
                )
            
            with filter_col2:
                delete_filter_difficulty = st.selectbox(
                    "Filter by Difficulty",
                    ["All"] + sorted(set(q.get("difficulty", "Intermediate") for q in questions)),
                    key="delete_difficulty_filter"
                )
            
            # Apply filters
            filtered_delete_questions = questions
            if delete_filter_category != "All":
                filtered_delete_questions = [q for q in filtered_delete_questions if q.get("category", "General") == delete_filter_category]
            if delete_filter_difficulty != "All":
                filtered_delete_questions = [q for q in filtered_delete_questions if q.get("difficulty", "Intermediate") == delete_filter_difficulty]
            
            # Question selection for deletion
            if not filtered_delete_questions:
                st.warning("No questions match the selected filters.")
            else:
                delete_question_titles = [f"Q{q['id']}: {q['question'][:50]}..." for q in filtered_delete_questions]
                
                delete_options = st.multiselect(
                    "Select Questions to Delete",
                    options=range(len(filtered_delete_questions)),
                    format_func=lambda i: delete_question_titles[i]
                )
                
                if delete_options:
                    st.warning(f"You are about to delete {len(delete_options)} questions. This action cannot be undone.")
                    
                    if st.button("Confirm Deletion"):
                        # Get IDs of questions to delete
                        ids_to_delete = [filtered_delete_questions[i]["id"] for i in delete_options]
                        
                        # Remove questions with those IDs
                        questions = [q for q in questions if q["id"] not in ids_to_delete]
                        
                        save_questions(questions)
                        st.success(f"Successfully deleted {len(delete_options)} questions!")
                        st.rerun()  # Refresh the page
        else:
            st.info("No questions available to delete.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# modules/pages/admin/manage_users.py

def manage_users():
    """User management interface with enhanced features"""
    st.subheader("User Management")
    # Load users and scores
    users = load_users()
    scores = load_scores()

    # Convert users to DataFrame for easier handling
    if users:
        users_df = pd.DataFrame([
            {
                "username": username,
                "name": info["name"],
                "role": info["role"],
                "last_login": info.get("last_login", "Never"),
                "created_at": info.get("created_at", "Unknown")
            }
            for username, info in users.items()
        ])

        # Add quiz stats
        if not scores:
            users_df["quizzes_taken"] = 0
            users_df["avg_score"] = 0
        else:
            scores_df = pd.DataFrame(scores)

            # Debugging: Print columns in scores_df to verify structure
            print("Columns in scores_df:", scores_df.columns)

            # Check if 'id' column exists; if not, use another column or count rows
            if "id" in scores_df.columns:
                count_column = "id"
            elif "timestamp" in scores_df.columns:  # Fallback to timestamp if available
                count_column = "timestamp"
            else:
                count_column = None  # Use row count as fallback

            # Group by username and calculate stats
            if count_column:
                user_stats = scores_df.groupby("username").agg({
                    count_column: "count",  # Count the specified column
                    "percentage": "mean"    # Calculate average score
                }).reset_index().rename(columns={count_column: "quizzes_taken", "percentage": "avg_score"})
            else:
                # If no specific column exists, count rows directly
                user_stats = scores_df.groupby("username").agg({
                    "percentage": "mean"
                }).reset_index()
                user_stats["quizzes_taken"] = scores_df["username"].map(scores_df["username"].value_counts())

            # Merge with users_df
            users_df = users_df.merge(user_stats, on="username", how="left")
            users_df["quizzes_taken"] = users_df["quizzes_taken"].fillna(0).astype(int)
            users_df["avg_score"] = users_df["avg_score"].fillna(0).round(1)

    # User overview
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)

    # User stats summary
    col1, col2, col3 = st.columns(3)
    with col1:
        total_users = len(users) if users else 0
        st.metric("Total Users", total_users)
    with col2:
        admin_count = sum(1 for u, info in users.items() if info["role"] == "admin")
        st.metric("Administrators", admin_count)
    with col3:
        operator_count = sum(1 for u, info in users.items() if info["role"] == "operator")
        st.metric("Operators", operator_count)

    # User table with filtering and sorting
    if users:
        # Search and filter
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input("Search Users", placeholder="Enter name or username")
        with search_col2:
            role_filter = st.selectbox("Role", ["All", "admin", "operator"])

        # Apply filters
        filtered_df = users_df
        if search_query:
            filtered_df = filtered_df[
                filtered_df["username"].str.contains(search_query, case=False) | 
                filtered_df["name"].str.contains(search_query, case=False)
            ]
        if role_filter != "All":
            filtered_df = filtered_df[filtered_df["role"] == role_filter]

        # Display user table
        st.dataframe(
            filtered_df.sort_values("username"),
            use_container_width=True,
            column_config={
                "username": "Username",
                "name": "Full Name",
                "role": "Role",
                "quizzes_taken": "Quizzes Taken",
                "avg_score": "Avg. Score (%)",
                "last_login": "Last Login",
                "created_at": "Created At"
            }
        )
    else:
        st.info("No users found. Add users using the form below.")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # User management tabs
    user_tab1, user_tab2, user_tab3, user_tab4 = st.tabs(["Add User", "Reset Password", "Remove User", "Manage User Data"])
    
    with user_tab1:
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### Add New User")
        
        with st.form(key="new_user_form"):
            new_username = st.text_input("Username", help="Username for login (no spaces)")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            new_name = st.text_input("Full Name")
            new_role = st.selectbox("Role", ["operator", "admin"])
            
            submit_user = st.form_submit_button("Add User")
            
            if submit_user:
                if not new_username or not new_password or not new_name:
                    st.error("All fields are required")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif new_username in users:
                    st.error("Username already exists")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long")
                else:
                    users[new_username] = {
                        "password": hash_password(new_password),
                        "name": new_name,
                        "role": new_role,
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "last_login": None
                    }
                    save_users(users)
                    st.success(f"User {new_username} added successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with user_tab2:
        if users:
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            st.markdown("### Reset User Password")
            
            # User selection
            reset_username = st.selectbox(
                "Select User", 
                sorted(list(users.keys())), 
                format_func=lambda u: f"{u} ({users[u]['name']})",
                key="reset_password_select"
            )
            
            with st.form(key="reset_password_form"):
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                # Password requirements helper
                if new_password:
                    col1, col2 = st.columns(2)
                    with col1:
                        if len(new_password) >= 8:
                            st.success("✓ At least 8 characters")
                        else:
                            st.error("✗ At least 8 characters")
                    
                    with col2:
                        if any(c.isupper() for c in new_password) and any(c.islower() for c in new_password):
                            st.success("✓ Mix of upper and lower case")
                        else:
                            st.warning("✗ Mix of upper and lower case (recommended)")
                
                generate_password = st.checkbox("Generate a secure password instead")
                
                if generate_password:
                    import random, string
                    # Generate a secure random password
                    chars = string.ascii_letters + string.digits + "!@#$%^&*"
                    generated_password = ''.join(random.choice(chars) for _ in range(12))
                    st.info(f"Generated password: {generated_password}")
                    st.warning("Make sure to save this password! It won't be shown again.")
                
                reset_submit = st.form_submit_button("Reset Password")
                
                if reset_submit:
                    if generate_password:
                        # Use the generated password
                        users[reset_username]["password"] = hash_password(generated_password)
                        save_users(users)
                        st.success(f"Password for {reset_username} has been reset to the generated password.")
                    else:
                        if not new_password:
                            st.error("Password cannot be empty")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match")
                        elif len(new_password) < 8:
                            st.error("Password must be at least 8 characters long")
                        else:
                            users[reset_username]["password"] = hash_password(new_password)
                            save_users(users)
                            st.success(f"Password for {reset_username} has been reset")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with user_tab3:
        if users:
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            st.markdown("### Remove User")
            
            # User selection
            delete_users = st.multiselect(
                "Select Users to Remove",
                sorted(list(users.keys())),
                format_func=lambda u: f"{u} ({users[u]['name']} - {users[u]['role']})"
            )
            
            if delete_users:
                # Count admins to prevent removing the last one
                admin_count = sum(1 for u, info in users.items() if info["role"] == "admin")
                
                # Check if we're trying to remove the last admin
                removing_last_admin = admin_count <= sum(1 for u in delete_users if users[u]["role"] == "admin")
                
                if removing_last_admin:
                    st.error("Cannot remove the last administrator account. At least one admin must remain.")
                else:
                    st.warning(f"You are about to remove {len(delete_users)} user(s). This action cannot be undone.")
                    st.info("Quiz scores for these users will remain in the system.")
                    
                    if st.button("Confirm Removal"):
                        # Remove the selected users
                        for username in delete_users:
                            del users[username]
                        
                        save_users(users)
                        st.success(f"Successfully removed {len(delete_users)} user(s).")
                        st.rerun()  # Refresh the page
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Then add this code for the fourth tab
    with user_tab4:
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown("### Manage Quiz Results")
        
        if not scores:
            st.info("No quiz scores found in the system.")
        else:
            # Option to clear all scores
            st.markdown("#### Clear All Quiz Results")
            st.warning("This will permanently delete ALL quiz results for ALL users.")
            
            if st.button("Clear All Results", key="clear_all_results"):
                confirm = st.checkbox("I understand this will delete all quiz history and cannot be undone")
                
                if confirm and st.button("Confirm Clear All Results", key="confirm_clear_all"):
                    # Call function to clear all scores
                    clear_all_scores()  # This function needs to be added to data_manager.py
                    st.success("All quiz results have been cleared successfully.")
                    st.rerun()
            
            # Option to clear scores for a specific user
            st.markdown("#### Clear Results for Specific User")
            
            # Get unique usernames from scores
            usernames = sorted(list(set(score["username"] for score in scores)))
            
            if usernames:
                selected_user = st.selectbox(
                    "Select User", 
                    usernames,
                    format_func=lambda u: f"{u} ({users.get(u, {}).get('name', 'Unknown')})"
                )
                
                # Count scores for selected user
                user_scores_count = sum(1 for score in scores if score["username"] == selected_user)
                
                if user_scores_count > 0:
                    st.info(f"Found {user_scores_count} quiz result(s) for {selected_user}")
                    
                    if st.button("Clear Results for this User", key="clear_user_results"):
                        # Call function to clear scores for specific user
                        clear_user_scores(selected_user)  # This function needs to be added to data_manager.py
                        st.success(f"All quiz results for {selected_user} have been cleared.")
                        st.rerun()
                else:
                    st.info(f"No quiz results found for {selected_user}")
                    
        st.markdown('</div>', unsafe_allow_html=True)            


# modules/pages/admin/system_settings.py

def system_settings():
    """System settings interface"""
    st.subheader("System Settings")
    
    # Load current settings
    settings = load_settings()
    
    # Initialize with defaults if missing
    if not settings:
        settings = {
            "company_name": "Your Company",
            "passing_score": 80,
            "certificate_validity_days": 365,
            "enable_self_registration": True,
            "default_quiz_time_limit": 0,
            "default_quiz_questions": 10,
            "track_categories": True,
            "require_reset_password": True,
            "password_expiry_days": 90,
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    # Settings form
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    
    with st.form("settings_form"):
        st.markdown("### Application Settings")
        
        # Company info
        company_name = st.text_input("Company Name", value=settings.get("company_name", "Your Company"))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            passing_score = st.slider(
                "Passing Score (%)", 
                min_value=50, 
                max_value=100, 
                value=settings.get("passing_score", 80),
                step=5
            )
        
        with col2:
            certificate_validity = st.number_input(
                "Certificate Validity (days)",
                min_value=30,
                max_value=1825,  # 5 years
                value=settings.get("certificate_validity_days", 365),
                step=30
            )
        
        with col3:
            enable_registration = st.checkbox(
                "Allow Self-Registration",
                value=settings.get("enable_self_registration", True)
            )
        
        # Quiz default settings
        st.markdown("### Quiz Default Settings")
        
        quiz_col1, quiz_col2 = st.columns(2)
        
        with quiz_col1:
            default_time_limit = st.number_input(
                "Default Time Limit (minutes, 0 for no limit)",
                min_value=0,
                max_value=120,
                value=settings.get("default_quiz_time_limit", 0),
                step=5
            )
        
        with quiz_col2:
            default_questions = st.number_input(
                "Default Number of Questions",
                min_value=5,
                max_value=50,
                value=settings.get("default_quiz_questions", 10),
                step=5
            )
        
        track_categories = st.checkbox(
            "Track Category Performance",
            value=settings.get("track_categories", True),
            help="Collect detailed statistics on performance by category"
        )
        
        # Security settings
        st.markdown("### Security Settings")
        
        security_col1, security_col2 = st.columns(2)
        
        with security_col1:
            require_password_reset = st.checkbox(
                "Require Password Reset for New Users",
                value=settings.get("require_reset_password", True)
            )
        
        with security_col2:
            password_expiry = st.number_input(
                "Password Expiry (days, 0 for never)",
                min_value=0,
                max_value=365,
                value=settings.get("password_expiry_days", 90),
                step=30
            )
        
        # Database settings section
        try:
            from ..database.connection import get_db_session, close_db_session
            HAS_DATABASE = True
        except ImportError:
            HAS_DATABASE = False
        
        if HAS_DATABASE:
            st.markdown("### Database Settings")
            
            # Backup frequency
            backup_frequency = st.selectbox(
                "Automatic Backup Frequency",
                options=["Daily", "Weekly", "Monthly", "Never"],
                index=["Daily", "Weekly", "Monthly", "Never"].index(settings.get("backup_frequency", "Weekly"))
            )
            settings["backup_frequency"] = backup_frequency
        
        # Submit button
        submit_settings = st.form_submit_button("Save Settings")
        
        if submit_settings:
            # Update settings
            settings = {
                "company_name": company_name,
                "passing_score": passing_score,
                "certificate_validity_days": certificate_validity,
                "enable_self_registration": enable_registration,
                "default_quiz_time_limit": default_time_limit,
                "default_quiz_questions": default_questions,
                "track_categories": track_categories,
                "require_reset_password": require_password_reset,
                "password_expiry_days": password_expiry,
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add database settings if available
            if HAS_DATABASE:
                settings["backup_frequency"] = backup_frequency
            
            save_settings(settings)
            st.success("Settings updated successfully!")
    
    st.markdown('</div>', unsafe_allow_html=True)


 # modules/pages/admin/branding_settings.py


def branding_settings():
    """Branding customization interface"""
    st.subheader("Company Branding")
    
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown("### Company Logo")
    
    # Show current logo if it exists
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=200, caption="Current logo")
    else:
        st.info("No custom logo uploaded. A default placeholder will be shown.")
    
    st.write("Upload your company logo to display throughout the app and on certificates.")
    st.write("Recommended size: 400x200 pixels, PNG or JPG format with transparent background.")
    
    # Logo upload
    uploaded_logo = st.file_uploader("Upload Logo (PNG or JPG)", type=["png", "jpg", "jpeg"])
    if uploaded_logo is not None:
        # Display preview
        st.image(uploaded_logo, width=200, caption="Logo Preview")
        
        # Save button
        if st.button("Save Logo", key="save_logo_btn"):
            # Ensure the assets directory exists
            os.makedirs(os.path.dirname(LOGO_PATH), exist_ok=True)
            
            # Save the uploaded logo
            with open(LOGO_PATH, "wb") as f:
                f.write(uploaded_logo.getbuffer())
            st.success("Logo uploaded successfully! It will appear throughout the app.")
    
    # Remove logo option
    if os.path.exists(LOGO_PATH):
        if st.button("Remove Logo", key="remove_logo_btn"):
            os.remove(LOGO_PATH)
            st.success("Logo removed successfully.")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Custom certificate settings
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown("### Certificate Customization")
    
    # Load settings
    settings = load_settings()
    
    # Certificate preview
    st.write("Preview how certificates will appear when issued to users:")
    
    # Generate sample certificate
    sample_cert = create_certificate(
        "Sample User",
        "92.5",
        datetime.datetime.now().strftime("%B %d, %Y"),
        "SAMPLE123"
    )
    
    # Display certificate preview using base64 encoding
    b64_cert = base64.b64encode(sample_cert.encode()).decode()
    iframe_html = f'<iframe src="data:text/html;base64,{b64_cert}" width="100%" height="500" style="border: 1px solid #ddd; border-radius: 5px;"></iframe>'
    st.markdown(iframe_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)