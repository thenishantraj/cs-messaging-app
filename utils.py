import pandas as pd
from datetime import datetime, timedelta
import re
from typing import List, Dict, Tuple, Optional

def calculate_urgency_score(message: str) -> Tuple[int, str]:
    """Calculate urgency score and priority for a message"""
    urgency_keywords = {
        'urgent': 5, 'emergency': 5, 'immediately': 4, 'asap': 4, 'now': 3,
        'loan': 3, 'disburse': 4, 'approval': 3, 'approved': 2, 'rejected': 4,
        'batch number': 3, 'CRB': 3, 'clearance': 3, 'credit': 3,
        'payment': 2, 'pay': 2, 'money': 2, 'balance': 2, 'due': 2,
        'help': 3, 'problem': 3, 'issue': 3, 'error': 3,
        'fraud': 5, 'stolen': 5, 'hacked': 5
    }
    
    message_lower = message.lower()
    score = 0
    
    for keyword, points in urgency_keywords.items():
        if keyword in message_lower:
            score += points
    
    # Boost score for certain patterns
    if any(pattern in message_lower for pattern in ["can't access", "can't login", "blocked"]):
        score += 3
    
    # Determine priority
    if score >= 12:
        priority = "high"
    elif score >= 7:
        priority = "medium"
    else:
        priority = "low"
    
    return score, priority

def categorize_message(message: str) -> str:
    """Categorize message based on content"""
    message_lower = message.lower()
    
    categories = {
        'loan_application': ['loan', 'apply', 'application', 'approved', 'rejected', 'qualif', 'eligible'],
        'payment': ['pay', 'payment', 'clear', 'balance', 'due', 'overdue', 'settle'],
        'technical': ['app', 'login', 'access', 'error', 'bug', 'system', 'technical'],
        'account': ['account', 'update', 'change', 'number', 'phone', 'email', 'profile'],
        'urgent': ['urgent', 'emergency', 'asap', 'immediately', 'now', 'critical'],
        'fraud': ['fraud', 'stolen', 'hacked', 'unauthorized', 'scam'],
        'general': ['hi', 'hello', 'thanks', 'thank', 'help', 'question']
    }
    
    for category, keywords in categories.items():
        if any(keyword in message_lower for keyword in keywords):
            return category
    
    return 'other'

def extract_customer_info(message: str) -> Dict:
    """Extract potential customer information from message"""
    info = {}
    
    # Extract phone numbers
    phone_patterns = [
        r'07\d{8}',  # Kenyan mobile numbers
        r'\+2547\d{8}',
        r'0\d{9}'
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, message)
        if phones:
            info['phone_numbers'] = phones
            break
    
    # Extract amounts
    amount_patterns = [
        r'Ksh\s*(\d+(?:,\d+)*)',
        r'ksh\s*(\d+(?:,\d+)*)',
        r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'(\d+(?:,\d+)*)\s*(?:ksh|shillings)'
    ]
    
    amounts = []
    for pattern in amount_patterns:
        amounts.extend(re.findall(pattern, message.lower()))
    if amounts:
        info['amounts'] = amounts
    
    # Extract dates
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{1,2}-\d{1,2}-\d{4}',
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'
    ]
    
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, message))
    if dates:
        info['dates'] = dates
    
    return info

def filter_messages(messages_df: pd.DataFrame, 
                    search_query: str = "",
                    priority_filter: str = "all",
                    category_filter: str = "all",
                    status_filter: str = "all") -> pd.DataFrame:
    """Filter messages based on various criteria"""
    filtered_df = messages_df.copy()
    
    # Apply search filter
    if search_query:
        mask = (
            filtered_df['message_body'].str.contains(search_query, case=False, na=False) |
            filtered_df['user_id'].astype(str).str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Apply priority filter
    if priority_filter != "all":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
    
    # Apply category filter
    if category_filter != "all":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    
    # Apply status filter
    if status_filter != "all":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    return filtered_df

def format_timestamp(timestamp) -> str:
    """Format timestamp for display"""
    if pd.isna(timestamp):
        return "N/A"
    
    if isinstance(timestamp, str):
        timestamp = pd.to_datetime(timestamp)
    
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60}m ago"
        else:
            return f"{diff.seconds // 3600}h ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days}d ago"
    else:
        return timestamp.strftime("%b %d, %Y")

def get_priority_color(priority: str) -> str:
    """Get color for priority badge"""
    colors = {
        'high': '#FF4B4B',
        'medium': '#FFA500',
        'low': '#4CAF50',
        'normal': '#2196F3'
    }
    return colors.get(priority.lower(), '#757575')

def get_status_color(status: str) -> str:
    """Get color for status badge"""
    colors = {
        'pending': '#FF9800',
        'in_progress': '#2196F3',
        'resolved': '#4CAF50'
    }
    return colors.get(status, '#757575')
