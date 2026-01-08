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
        try:
            # Try different paths for CSV file
            possible_paths = [
                'data/GeneralistRails_Project_MessageData.csv',
                './data/GeneralistRails_Project_MessageData.csv',
                'GeneralistRails_Project_MessageData.csv',
                './GeneralistRails_Project_MessageData.csv'
            ]
            
            df = None
            csv_path = None
            
            for path in possible_paths:
                if os.path.exists(path):
                    csv_path = path
                    df = pd.read_csv(path)
                    print(f"✅ Loaded CSV from: {path}")
                    break
            
            if df is None:
                print("⚠️ CSV file not found in any location. Creating sample data instead.")
                # Create sample messages if CSV not found
                messages = []
                for i in range(50):
                    msg = CustomerMessage(
                        user_id=1000 + i,
                        timestamp=datetime.now() - timedelta(hours=i),
                        message_body=f"Sample message {i+1}: Need help with loan application",
                        urgency_score=random.randint(1, 15),
                        priority=random.choice(['low', 'normal', 'high']),
                        category=random.choice(['loan_application', 'payment', 'technical']),
                        status=random.choice(['pending', 'in_progress', 'resolved'])
                    )
                    messages.append(msg)
                
                session.add_all(messages)
                print("✅ Created 50 sample messages")
            else:
                # Clean and process data
                print("📊 Processing CSV data...")
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
                        category=category,
                        status='pending'  # YEH LINE ADD KARNA HAI
                    )
                    messages.append(msg)
                
                session.add_all(messages)
                print(f"✅ Loaded {len(messages)} messages from CSV")
            
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
            ]
            
            session.add_all(canned_responses)
            
            # Create sample customer profiles
            profiles = []
            for i in range(1, 31):
                profile = CustomerProfile(
                    user_id=1000 + i,
                    name=f"Customer {1000 + i}",
                    email=f"customer{1000 + i}@example.com",
                    phone=f"07{str(1000 + i).zfill(8)}",
                    last_loan_amount=random.choice([5000, 10000, 15000, 20000]),
                    last_loan_date=datetime.now() - timedelta(days=random.randint(10, 90)),
                    repayment_history=random.choice(['good', 'fair', 'poor']),
                    total_loans=random.randint(1, 10),
                    total_repaid=random.randint(10000, 100000),
                    credit_score=random.randint(550, 800)
                )
                profiles.append(profile)
            
            session.add_all(profiles)
            
            session.commit()
            print("✅ Database initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            session.rollback()
    
    session.close()
    return engine

def get_session():
    """Get database session"""
    engine = create_engine('sqlite:///cs_messages.db')
    Session = sessionmaker(bind=engine)
    return Session()
