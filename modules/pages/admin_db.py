# modules/pages/admin_db.py

import streamlit as st
import os
import pandas as pd
import datetime
import sqlite3
import subprocess
import sys

# Try to import database-specific modules
try:
    from ..database.connection import get_db_session, close_db_session
    from ..database.migrate import migrate_data, verify_migration
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False

def database_management():
    """
    Database management tab for the admin panel
    """
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown("### Database Management")
    
    # Check if we're using SQLite
    if not USE_DATABASE:
        st.warning("The application is not configured to use SQLite. You are currently using JSON file storage.")
        
        # Provide migration option
        st.markdown("#### Migrate to SQLite")
        st.markdown("""
            You can migrate your data from JSON files to SQLite for better performance, reliability, and data integrity.
            
            Benefits of SQLite:
            - Better performance with larger datasets
            - Improved data integrity and consistency
            - Support for complex queries and reports
            - Easier backups and data management
        """)
        
        if st.button("Migrate to SQLite", key="migrate_to_sqlite"):
            try:
                # Run the migration script
                script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "migrate_to_sqlite.py")
                
                if os.path.exists(script_path):
                    st.info("Starting migration... This may take a moment.")
                    
                    # Get python executable path
                    python_executable = sys.executable
                    
                    # Run the script as a subprocess
                    result = subprocess.run(
                        [python_executable, script_path, "--force"],
                        capture_output=True,
                        text=True
                    )
                    
                    # Display the output
                    if result.returncode == 0:
                        st.success("Migration completed successfully! Please restart the application to use SQLite.")
                        st.code(result.stdout, language="text")
                    else:
                        st.error("Migration failed. See error output below:")
                        st.code(result.stderr, language="text")
                else:
                    st.error(f"Migration script not found at {script_path}")
                    st.info("Please make sure the migrate_to_sqlite.py file is in the project root directory.")
            except Exception as e:
                st.error(f"Error running migration: {e}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # If using SQLite, show database info and management options
    db_path = os.path.join("data", "forklift_training.db")
    
    # Show database file info
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path) / (1024 * 1024)  # Convert to MB
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(db_path))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Database Size", f"{file_size:.2f} MB")
        
        with col2:
            st.metric("Last Modified", file_modified.strftime("%Y-%m-%d %H:%M"))
        
        with col3:
            # Connect to the database and get table counts
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get the count of all tables
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            st.metric("Tables", f"{table_count}")
            
            conn.close()
    else:
        st.warning("Database file not found. The application may be using in-memory database or file-based storage.")
    
    # Database operations
    st.markdown("#### Database Operations")
    
    # Put operations in columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Backup database
        st.markdown("##### Create Database Backup")
        
        if st.button("Create Backup", key="backup_db"):
            try:
                # Create backup directory if it doesn't exist
                backup_dir = os.path.join("data", "backups")
                os.makedirs(backup_dir, exist_ok=True)
                
                # Generate backup filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                backup_file = os.path.join(backup_dir, f"database_backup_{timestamp}.db")
                
                # Copy the database file
                import shutil
                shutil.copy2(db_path, backup_file)
                
                st.success(f"Backup created successfully at {backup_file}")
            except Exception as e:
                st.error(f"Error creating backup: {e}")
    
    with col2:
        # Optimize database
        st.markdown("##### Optimize Database")
        
        if st.button("Optimize Database", key="optimize_db"):
            try:
                # Connect to the database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Run VACUUM to rebuild the database file, reclaiming free space
                cursor.execute("VACUUM")
                
                # Run ANALYZE to update statistics used by the query planner
                cursor.execute("ANALYZE")
                
                conn.close()
                
                st.success("Database optimized successfully!")
            except Exception as e:
                st.error(f"Error optimizing database: {e}")
    
    # Database statistics
    st.markdown("#### Database Statistics")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    # Table statistics
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
    
    if not tables.empty:
        table_stats = []
        
        for table_name in tables['name']:
            # Skip internal sqlite tables
            if table_name.startswith('sqlite_'):
                continue
            
            # Get row count
            row_count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table_name}", conn).iloc[0]['count']
            
            # Get column count
            column_count = len(pd.read_sql_query(f"PRAGMA table_info({table_name})", conn))
            
            table_stats.append({
                "Table": table_name,
                "Rows": row_count,
                "Columns": column_count
            })
        
        if table_stats:
            st.dataframe(pd.DataFrame(table_stats), use_container_width=True)
        else:
            st.info("No user tables found in the database.")
    else:
        st.info("No tables found in the database.")
    
    conn.close()
    
    # Migration verification for users who have migrated
    st.markdown("#### Verify Data Integrity")
    
    if st.button("Verify Database Integrity", key="verify_db"):
        try:
            # Run pragma integrity_check
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            
            if result == "ok":
                st.success("Database integrity check passed successfully!")
            else:
                st.error(f"Database integrity check failed: {result}")
        except Exception as e:
            st.error(f"Error checking database integrity: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)