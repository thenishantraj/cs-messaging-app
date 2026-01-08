# setup_app.py
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

print("🚀 Setting up Branch CS Messaging App...")
print("="*50)

# 1. Check CSV file
csv_path = 'data/GeneralistRails_Project_MessageData.csv'
if os.path.exists(csv_path):
    print(f"✅ CSV file found: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"   Total rows: {len(df)}")
else:
    print("❌ CSV file not found. Please ensure it's in 'data/' folder")
    print("   Creating sample data instead...")
    # Create sample dataframe
    data = {
        'User ID': [208, 218, 444, 676, 779, 1092, 1155, 1241, 1245, 1354],
        'Timestamp (UTC)': ['2017-02-01 19:29:05'] * 10,
        'Message Body': [
            "Why was my loan application rejected?",
            "I will pay on 5th, please wait",
            "I will clear my loan before 15th",
            "Hi can i get the batch number?",
            "I have cleared my loan but still denied",
            "My number is 0790898526 help me",
            "Salaries delayed but will pay today",
            "Thanks for being understanding",
            "Please send me batch number",
            "Expunge my details from system"
        ]
    }
    df = pd.DataFrame(data)

# 2. Delete old database if exists
if os.path.exists("cs_messages.db"):
    os.remove("cs_messages.db")
    print("✅ Old database deleted")

# 3. Create new database
conn = sqlite3.connect('cs_messages.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE customer_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    message_body TEXT NOT NULL,
    agent_id TEXT,
    response TEXT,
    response_timestamp DATETIME,
    status TEXT DEFAULT 'pending',
    urgency_score INTEGER DEFAULT 0,
    priority TEXT DEFAULT 'normal',
    category TEXT
)
''')

cursor.execute('''
CREATE TABLE canned_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    response_text TEXT NOT NULL,
    category TEXT,
    use_count INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE customer_profiles (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT,
    email TEXT,
    last_loan_amount INTEGER,
    last_loan_date DATETIME,
    repayment_history TEXT DEFAULT 'good',
    total_loans INTEGER DEFAULT 0,
    total_repaid INTEGER DEFAULT 0,
    credit_score INTEGER DEFAULT 700
)
''')

print("✅ Database tables created")

# 4. Insert messages
print("📨 Inserting messages...")
for _, row in df.iterrows():
    user_id = int(row['User ID']) if pd.notna(row['User ID']) else random.randint(1000, 9999)
    message = str(row['Message Body'])
    
    # Calculate urgency
    urgency = 0
    if any(word in message.lower() for word in ['urgent', 'emergency', 'asap']):
        urgency += 10
    if any(word in message.lower() for word in ['loan', 'reject', 'denied']):
        urgency += 8
    if any(word in message.lower() for word in ['batch', 'number', 'crb']):
        urgency += 7
    if any(word in message.lower() for word in ['pay', 'payment', 'clear']):
        urgency += 5
    
    # Priority
    priority = 'normal'
    if urgency > 15:
        priority = 'high'
    elif urgency > 8:
        priority = 'normal'
    else:
        priority = 'low'
    
    # Category
    category = 'other'
    if 'loan' in message.lower():
        category = 'loan_application'
    elif 'pay' in message.lower():
        category = 'payment'
    elif 'batch' in message.lower():
        category = 'clearance'
    
    cursor.execute('''
    INSERT INTO customer_messages 
    (user_id, timestamp, message_body, status, urgency_score, priority, category)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        datetime.now() - timedelta(hours=random.randint(1, 100)),
        message,
        'pending',
        urgency,
        priority,
        category
    ))

print(f"✅ {len(df)} messages inserted")

# 5. Insert canned responses
canned = [
    ("Loan Application Received", "Thank you for your loan application. We are reviewing it.", "loan_application"),
    ("Payment Confirmation", "We have received your payment. Thank you.", "payment"),
    ("Batch Number", "Your batch number is [BATCH_NUMBER].", "clearance"),
    ("Application Rejected", "Your application was rejected. Reapply after 7 days.", "loan_application"),
    ("Payment Extension", "We can extend payment deadline by 3 days.", "payment")
]

for title, response, category in canned:
    cursor.execute('INSERT INTO canned_responses (title, response_text, category) VALUES (?, ?, ?)', 
                   (title, response, category))
print(f"✅ {len(canned)} canned responses inserted")

# 6. Insert customer profiles
unique_users = df['User ID'].dropna().unique()[:20]
for user_id in unique_users:
    cursor.execute('''
    INSERT INTO customer_profiles 
    (user_id, name, phone, email, last_loan_amount, last_loan_date, 
     repayment_history, total_loans, total_repaid, credit_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        int(user_id),
        f"Customer {user_id}",
        f"07{str(int(user_id)).zfill(8)}",
        f"customer{user_id}@example.com",
        random.choice([5000, 10000, 15000]),
        datetime.now() - timedelta(days=random.randint(10, 90)),
        random.choice(['good', 'fair', 'poor']),
        random.randint(1, 10),
        random.randint(10000, 50000),
        random.randint(600, 800)
    ))
print(f"✅ {len(unique_users)} customer profiles inserted")

conn.commit()
conn.close()

print("\n" + "="*50)
print("✅ Setup complete!")
print("\n📱 Now run the app:")
print("streamlit run app.py")
print("\n🌐 Open: http://localhost:8501")
