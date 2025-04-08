# Utility functions can be added here
def format_timestamp(timestamp_str):
    """Format timestamp for better display"""
    from datetime import datetime
    
    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%b %d, %Y at %I:%M %p")

# Add more utility functions as needed