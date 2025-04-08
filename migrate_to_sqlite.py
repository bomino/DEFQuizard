#!/usr/bin/env python3
"""
Migration script to move data from JSON files to SQLite database
"""
import os
import sys
import argparse
import json
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our database modules
try:
    from modules.database.connection import init_db
    from modules.database.migrate import migrate_data, verify_migration
    
    # Import the data manager to have access to file paths
    from modules.data_manager import (
        USER_DB_FILE, QUESTIONS_FILE, SCORES_FILE, SETTINGS_FILE,
        BACKUP_DIR
    )
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def create_backup(files):
    """
    Create backups of all JSON data files
    
    Args:
        files (list): List of file paths to back up
    
    Returns:
        str: Path to backup directory
    """
    # Create timestamp for backup directory
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = os.path.join(BACKUP_DIR, f"migration_backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy files to backup directory
    for file_path in files:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, file_name)
            
            # Copy the file
            with open(file_path, "r") as src, open(backup_path, "w") as dst:
                dst.write(src.read())
            
            print(f"Backed up {file_path} to {backup_path}")
    
    return backup_dir

def migrate():
    """
    Run the migration process
    """
    # Check if data files exist
    data_files = [USER_DB_FILE, QUESTIONS_FILE, SCORES_FILE, SETTINGS_FILE]
    existing_files = [f for f in data_files if os.path.exists(f)]
    
    if not existing_files:
        print("No JSON data files found. Nothing to migrate.")
        return False
    
    # Create backups first
    backup_dir = create_backup(existing_files)
    print(f"Created backup of all data files in {backup_dir}")
    
    # Initialize the database
    print("Initializing database...")
    init_db()
    
    # Run the migration
    print("Migrating data...")
    try:
        stats = migrate_data()
        print(f"Migration complete!")
        print(f"Migrated {stats['users']} users, {stats['questions']} questions, "
              f"{stats['scores']} scores, and {stats['settings']} settings.")
        
        # Verify the migration
        print("Verifying migration...")
        verification = verify_migration()
        
        if verification["success"]:
            print("Migration verified successfully!")
        else:
            print("Migration verification failed. Please check the data.")
        
        print("Verification results:")
        for entity in ["users", "questions", "scores", "settings"]:
            print(f"  {entity.capitalize()}: JSON={verification[entity]['json']}, DB={verification[entity]['db']}")
        
        return verification["success"]
    
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Migrate data from JSON files to SQLite database")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backups of JSON files")
    parser.add_argument("--force", action="store_true", help="Force migration even if database already exists")
    
    args = parser.parse_args()
    
    # Check if database file already exists
    db_path = os.path.join("data", "forklift_training.db")
    if os.path.exists(db_path) and not args.force:
        print(f"Database file already exists at {db_path}")
        print("Use --force to run migration anyway (this may overwrite existing database data)")
        return
    
    # Run migration
    if migrate():
        print("\nMigration completed successfully!")
        print("\nYou can now use the application with SQLite database.")
        print("The JSON files have been backed up and can be safely removed if desired.")
    else:
        print("\nMigration failed or was incomplete.")
        print("Please check the logs above for more information.")
        print("Your original JSON files are still intact and backups were created.")

if __name__ == "__main__":
    main()