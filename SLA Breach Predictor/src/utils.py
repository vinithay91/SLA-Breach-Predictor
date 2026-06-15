"""
Utility functions for SLA Breach Predictor
"""

from datetime import datetime
import pandas as pd


def calculate_risk_score(ticket):
    """
    Calculate risk score for a ticket based on priority and time remaining
    
    Args:
        ticket: Dictionary containing ticket information
        
    Returns:
        Risk score between 0 and 1
    """
    priority_weights = {
        "critical": 1.0,
        "high": 0.8,
        "medium": 0.5,
        "low": 0.2
    }
    
    priority = ticket.get("priority", "medium").lower()
    base_score = priority_weights.get(priority, 0.5)
    
    # Adjust based on time remaining if available
    if "time_remaining" in ticket:
        time_remaining = ticket["time_remaining"]
        if time_remaining < 4:  # Less than 4 hours
            base_score = min(1.0, base_score + 0.3)
        elif time_remaining < 24:  # Less than 24 hours
            base_score = min(1.0, base_score + 0.1)
    
    return round(base_score, 2)


def parse_datetime(date_string):
    """
    Parse datetime string to datetime object
    
    Args:
        date_string: String in ISO format
        
    Returns:
        datetime object
    """
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except:
        return None


def load_csv_data(file_path):
    """
    Load data from CSV file
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        DataFrame with loaded data
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None


def save_csv_data(data, file_path):
    """
    Save data to CSV file
    
    Args:
        data: DataFrame to save
        file_path: Path to save CSV file
    """
    try:
        data.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving CSV: {e}")


def format_report_summary(stats):
    """
    Format statistics into a readable summary
    
    Args:
        stats: Dictionary with statistics
        
    Returns:
        Formatted string
    """
    summary = f"""
    Total Tickets: {stats.get('total', 0)}
    High Risk: {stats.get('high_risk', 0)}
    Medium Risk: {stats.get('medium_risk', 0)}
    Low Risk: {stats.get('low_risk', 0)}
    """
    return summary
