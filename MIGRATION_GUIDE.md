# Migration Guide: JSON to SQLite

This guide will help you migrate your Forklift Operator Training application from JSON file storage to SQLite database storage.

## Benefits of SQLite

Moving to SQLite provides several advantages:

- **Improved Data Integrity**: SQLite enforces constraints and relationships between data
- **Better Performance**: Faster data operations, especially with larger datasets
- **Concurrent Access**: Multiple operations can be performed simultaneously
- **Transaction Support**: All-or-nothing operations that prevent data corruption
- **Advanced Querying**: Complex queries and data filtering capabilities
- **Reduced Memory Usage**: Only loads needed data rather than entire files
- **Robust Backup System**: Easier to back up and restore your data

## Migration Options

There are two ways to migrate your data:

### Option 1: Automatic Migration (Recommended)

The application includes a built-in migration script that will handle the entire process for you:

1. **Install Required Dependencies**:
   ```bash
   pip install sqlalchemy alembic
   ```

2. **Run the Migration Script**:
   ```bash
   python migrate_to_sqlite.py
   ```
   
3. **Verify Migration**:
   The script will output verification information showing how many records were migrated.

4. **Restart the Application**:
   ```bash
   streamlit run app.py
   ```

The migration script will:
- Create a backup of all your JSON files
- Initialize the SQLite database
- Transfer all users, questions, scores, and settings
- Verify the migration was successful

### Option 2: Admin Panel Migration

You can also migrate directly through the Admin Panel:

1. **Login as Administrator**
2. **Navigate to the Admin Panel**
3. **Go to the "Database" tab**
4. **Click "Migrate to SQLite"**
5. **Follow the on-screen prompts**

## Verifying Migration

After migration, you can verify everything worked correctly:

1. **Login to the Admin Panel**
2. **Go to the "Database" tab**
3. **Review the database statistics**
4. **Click "Verify Database Integrity" to run a thorough check**

## Backup and Safety

The migration process automatically creates backups of all your JSON files in the `data/backups` directory with a timestamp. These backups are preserved even after successful migration.

## Troubleshooting

### Common Issues:

1. **Missing Dependencies**:
   ```
   Error: No module named 'sqlalchemy'
   ```
   
   Solution: Install required packages:
   ```bash
   pip install sqlalchemy alembic
   ```

2. **Permission Errors**:
   ```
   Error: Permission denied: 'data/forklift_training.db'
   ```
   
   Solution: Ensure your user has write access to the data directory.
   
3. **Data Integrity Issues**:
   
   Solution: Restore from backups and try again:
   ```bash
   cp data/backups/migration_backup_[TIMESTAMP]/users.json data/
   ```

4. **Migrated Data Discrepancies**:
   
   Solution: Check verification output and manually fix any issues, or restore from backups and retry migration with the `--force` flag:
   ```bash
   python migrate_to_sqlite.py --force
   ```

## Rollback Procedure

If you need to revert to JSON files:

1. **Restore JSON Files from Backup**:
   ```bash
   cp data/backups/migration_backup_[TIMESTAMP]/*.json data/
   ```

2. **Rename or Remove the SQLite Database**:
   ```bash
   mv data/forklift_training.db data/forklift_training.db.bak
   ```

3. **Edit modules/data_manager.py**:
   Set `USE_DATABASE = False` at the top of the file (if needed)

4. **Restart the Application**:
   ```bash
   streamlit run app.py
   ```

## Best Practices After Migration

1. **Regular Backups**: Use the Database tab in the Admin Panel to create regular backups
2. **Optimize Performance**: Run the database optimization tool periodically
3. **Update Dependencies**: Keep SQLAlchemy and other dependencies up to date
4. **Monitor Database Size**: Very large databases (>1GB) may need more advanced management

## Support

If you encounter issues during migration, please:

1. Check the application logs
2. Review the troubleshooting steps above
3. Contact support with details of your issue and the migration log output