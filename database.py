import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
from datetime import datetime
import os

Base = declarative_base()

class CustomerMessage(Base):
    """Database model for customer messages"""
    __tablename__ = 'customer_messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    message_body = Column(Text, nullable=False)
    agent_id = Column(String(50), nullable=True)
    response = Column(Text, nullable=True)
    response_timestamp = Column(DateTime, nullable=True)
    status = Column(String(20), default='pending')  # pending, in_progress, resolved
    urgency_score = Column(Integer, default=0)
    priority = Column(String(20), default='normal')  # low, normal, high
    category = Column(String(50), nullable=True)

class CannedResponse(Base):
    """Database model for canned responses"""
    __tablename__ = 'canned_responses'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    response_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    use_count = Column(Integer, default=0)

class CustomerProfile(Base):
    """Database model for customer profiles"""
    __tablename__ = 'customer_profiles'
    
    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    last_loan_amount = Column(Integer, nullable=True)
    last_loan_date = Column(DateTime, nullable=True)
    repayment_history = Column(String(20), default='good')  # good, fair, poor
    total_loans = Column(Integer, default=0)
    total_repaid = Column(Integer, default=0)
    credit_score = Column(Integer, default=700)

def init_database():
    """Initialize the database and load CSV data"""
    # Create SQLite database
    engine = create_engine('sqlite:///cs_messages.db')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if data already exists
    existing_messages = session.query(CustomerMessage).first()
    
    if not existing_messages:
        # Load CSV data
        csv_path = os.path.join('data', 'GeneralistRails_Project_MessageData.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            
            # Clean and process data
            df['timestamp'] = pd.to_datetime(df['Timestamp (UTC)'])
            df['message_body'] = df['Message Body'].astype(str)
            df['user_id'] = pd.to_numeric(df['User ID'], errors='coerce')
            
            # Calculate urgency scores
            urgency_keywords = {
                'urgent': 5, 'emergency': 5, 'immediately': 4, 'asap': 4,
                'loan': 3, 'disburse': 4, 'approval': 3, 'rejected': 4,
                'batch number': 3, 'CRB': 3, 'clearance': 3,
                'payment': 2, 'pay': 2, 'money': 2, 'balance': 2
            }
            
            messages = []
            for _, row in df.iterrows():
                if pd.isna(row['user_id']) or pd.isna(row['message_body']):
                    continue
                    
                # Calculate urgency score
                urgency_score = 0
                message_lower = row['message_body'].lower()
                for keyword, score in urgency_keywords.items():
                    if keyword in message_lower:
                        urgency_score += score
                
                # Determine priority
                priority = 'low'
                if urgency_score >= 10:
                    priority = 'high'
                elif urgency_score >= 5:
                    priority = 'normal'
                
                # Determine category
                category = 'other'
                if any(word in message_lower for word in ['loan', 'apply', 'approved', 'rejected']):
                    category = 'loan_application'
                elif any(word in message_lower for word in ['pay', 'payment', 'clear', 'balance']):
                    category = 'payment'
                elif any(word in message_lower for word in ['batch', 'number', 'CRB', 'clearance']):
                    category = 'clearance'
                elif any(word in message_lower for word in ['urgent', 'emergency', 'asap', 'immediately']):
                    category = 'urgent_inquiry'
                elif any(word in message_lower for word in ['update', 'change', 'number', 'phone']):
                    category = 'account_update'
                
                message = CustomerMessage(
                    user_id=int(row['user_id']),
                    timestamp=row['timestamp'],
                    message_body=row['message_body'],
                    urgency_score=urgency_score,
                    priority=priority,
                    category=category
                )
                messages.append(message)
            
            session.add_all(messages)
            
            # Create sample canned responses
            canned_responses = [
                CannedResponse(
                    title="Loan Application Received",
                    response_text="Thank you for your loan application. We are reviewing it and will get back to you within 24 hours.",
                    category="loan_application"
                ),
                CannedResponse(
                    title="Payment Confirmation",
                    response_text="We have received your payment. Thank you for settling your loan.",
                    category="payment"
                ),
                CannedResponse(
                    title="Batch Number Request",
                    response_text="Your batch number is [BATCH_NUMBER]. Please use this for CRB clearance.",
                    category="clearance"
                ),
                CannedResponse(
                    title="Account Verification",
                    response_text="We need to verify your account details. Please provide your ID number for verification.",
                    category="account_update"
                ),
                CannedResponse(
                    title="Application Rejected - 7 Days",
                    response_text="Your application has been rejected. You can reapply after 7 days.",
                    category="loan_application"
                ),
                CannedResponse(
                    title="Payment Extension",
                    response_text="We understand your situation. We can extend your payment deadline by 3 days.",
                    category="payment"
                ),
                CannedResponse(
                    title="Urgent Inquiry",
                    response_text="We are looking into your urgent inquiry and will respond shortly.",
                    category="urgent_inquiry"
                )
            ]
            
            session.add_all(canned_responses)
            
            # Create sample customer profiles
            profiles = []
            unique_user_ids = df['User ID'].unique()[:20]  # First 20 users for sample
            
            for user_id in unique_user_ids:
                profile = CustomerProfile(
                    user_id=int(user_id),
                    name=f"Customer {user_id}",
                    email=f"customer{user_id}@example.com",
                    phone=f"07{str(user_id).zfill(8)}",
                    last_loan_amount=5000 if user_id % 3 == 0 else 10000 if user_id % 3 == 1 else 15000,
                    last_loan_date=datetime(2023, 12, 1),
                    repayment_history='good' if user_id % 4 == 0 else 'fair' if user_id % 4 == 1 else 'poor',
                    total_loans=user_id % 10 + 1,
                    total_repaid=(user_id % 10 + 1) * 8000,
                    credit_score=650 + (user_id % 10) * 10
                )
                profiles.append(profile)
            
            session.add_all(profiles)
            
            session.commit()
            print(f"Loaded {len(messages)} messages, {len(canned_responses)} canned responses, and {len(profiles)} customer profiles.")
        else:
            print(f"CSV file not found at {csv_path}")
    
    session.close()
    return engine

def get_session():
    """Get database session"""
    engine = create_engine('sqlite:///cs_messages.db')
    Session = sessionmaker(bind=engine)
    return Session()
