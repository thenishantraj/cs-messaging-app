import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import desc, asc, or_, and_

# Import custom modules
from database import init_database, get_session, CustomerMessage, CannedResponse, CustomerProfile
import utils

# Page configuration
st.set_page_config(
    page_title="Branch CS Messaging Platform",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Custom header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #0d6efd;
        height: 100%;
    }
    
    .metric-card-pending {
        border-left-color: #FF9800;
    }
    
    .metric-card-high {
        border-left-color: #FF4B4B;
    }
    
    .metric-card-today {
        border-left-color: #4CAF50;
    }
    
    /* Message list items */
    .message-item {
        padding: 15px;
        margin: 8px 0;
        background: white;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .message-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #0d6efd;
    }
    
    .message-item.selected {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border: 2px solid #0d6efd;
        box-shadow: 0 4px 12px rgba(13, 110, 253, 0.2);
    }
    
    /* Priority badges */
    .priority-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Chat bubbles */
    .customer-bubble {
        background: #f0f2f6;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0 10px 0;
        max-width: 85%;
        position: relative;
    }
    
    .agent-bubble {
        background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0 10px auto;
        max-width: 85%;
        position: relative;
    }
    
    /* Customer profile card */
    .profile-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Scrollable containers */
    .scrollable-container {
        height: calc(100vh - 250px);
        overflow-y: auto;
        padding-right: 10px;
    }
    
    .scrollable-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .scrollable-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    .scrollable-container::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Filter section */
    .filter-section {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_message' not in st.session_state:
    st.session_state.selected_message = None
if 'agent_name' not in st.session_state:
    st.session_state.agent_name = "Agent_01"
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'selected_message_id' not in st.session_state:
    st.session_state.selected_message_id = None

def init_session():
    """Initialize database and session"""
    if 'db_initialized' not in st.session_state:
        init_database()
        st.session_state.db_initialized = True

def get_customer_profile(user_id):
    """Get customer profile information"""
    session = get_session()
    try:
        profile = session.query(CustomerProfile).filter(CustomerProfile.user_id == user_id).first()
        return profile
    finally:
        session.close()

def get_canned_responses():
    """Get all canned responses"""
    session = get_session()
    try:
        responses = session.query(CannedResponse).order_by(desc(CannedResponse.use_count)).all()
        return responses
    finally:
        session.close()

def update_message_status(message_id, status, agent_name=None, response_text=None):
    """Update message status and add response"""
    session = get_session()
    try:
        message = session.query(CustomerMessage).filter(CustomerMessage.id == message_id).first()
        if message:
            message.status = status
            if agent_name:
                message.agent_id = agent_name
            if response_text:
                message.response = response_text
                message.response_timestamp = datetime.now()
            session.commit()
            return True
    finally:
        session.close()
    return False

def increment_canned_response_use(response_id):
    """Increment canned response use count"""
    session = get_session()
    try:
        response = session.query(CannedResponse).filter(CannedResponse.id == response_id).first()
        if response:
            response.use_count += 1
            session.commit()
            return True
    finally:
        session.close()
    return False

def get_message_stats():
    """Get message statistics"""
    session = get_session()
    try:
        total = session.query(CustomerMessage).count()
        pending = session.query(CustomerMessage).filter(CustomerMessage.status == 'pending').count()
        high_priority = session.query(CustomerMessage).filter(CustomerMessage.priority == 'high').count()
        today = datetime.now().date()
        today_messages = session.query(CustomerMessage).filter(
            CustomerMessage.timestamp >= datetime.combine(today, datetime.min.time())
        ).count()
        
        return {
            'total': total,
            'pending': pending,
            'high_priority': high_priority,
            'today': today_messages
        }
    finally:
        session.close()

def truncate_text(text, max_length=80):
    """Truncate text for display"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def main():
    """Main application function"""
    init_session()
    
    # Header with gradient
    st.markdown("""
    <div class='main-header'>
        <h1 style='margin: 0;'>💬 Branch Customer Service</h1>
        <p style='margin: 5px 0 0 0; opacity: 0.9;'>Multi-Agent Messaging Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent selector at the top
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        st.markdown(f"<h4 style='color: #666;'>👤 Agent: <b>{st.session_state.agent_name}</b></h4>", unsafe_allow_html=True)
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=st.session_state.auto_refresh)
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh
            st.rerun()
    
    # Get statistics
    stats = get_message_stats()
    
    # Metrics row - Improved spacing
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <div style='background: #e3f2fd; padding: 8px; border-radius: 8px; margin-right: 10px;'>
                    📨
                </div>
                <div>
                    <div style='font-size: 14px; color: #666;'>Total Messages</div>
                    <div style='font-size: 28px; font-weight: bold; color: #0d6efd;'>{stats['total']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card metric-card-pending'>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <div style='background: #fff3e0; padding: 8px; border-radius: 8px; margin-right: 10px;'>
                    ⏳
                </div>
                <div>
                    <div style='font-size: 14px; color: #666;'>Pending</div>
                    <div style='font-size: 28px; font-weight: bold; color: #FF9800;'>{stats['pending']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card metric-card-high'>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <div style='background: #ffebee; padding: 8px; border-radius: 8px; margin-right: 10px;'>
                    🔥
                </div>
                <div>
                    <div style='font-size: 14px; color: #666;'>High Priority</div>
                    <div style='font-size: 28px; font-weight: bold; color: #FF4B4B;'>{stats['high_priority']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card metric-card-today'>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <div style='background: #e8f5e8; padding: 8px; border-radius: 8px; margin-right: 10px;'>
                    📅
                </div>
                <div>
                    <div style='font-size: 14px; color: #666;'>Today</div>
                    <div style='font-size: 28px; font-weight: bold; color: #4CAF50;'>{stats['today']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main three-column layout with better spacing
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1.2, 1.8, 1])
    
    # Left column: Message queue
    with col_left:
        st.markdown("### 📨 Message Queue")
        
        # Compact filter section
        with st.container():
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                priority_filter = st.selectbox(
                    "Priority",
                    ["all", "high", "medium", "low"],
                    key="priority_filter"
                )
            with col_f2:
                status_filter = st.selectbox(
                    "Status",
                    ["all", "pending", "in_progress", "resolved"],
                    key="status_filter"
                )
            
            category_filter = st.selectbox(
                "Category",
                ["all", "loan_application", "payment", "technical", 
                 "account", "urgent", "fraud", "general", "other"],
                key="category_filter"
            )
            
            search_query = st.text_input("🔍 Search messages", key="search_filter")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Get filtered messages
        session = get_session()
        try:
            query = session.query(CustomerMessage).order_by(
                desc(CustomerMessage.priority == 'high'),
                desc(CustomerMessage.urgency_score),
                desc(CustomerMessage.timestamp)
            )
            
            if priority_filter != "all":
                query = query.filter(CustomerMessage.priority == priority_filter)
            if status_filter != "all":
                query = query.filter(CustomerMessage.status == status_filter)
            if category_filter != "all":
                query = query.filter(CustomerMessage.category == category_filter)
            
            if search_query:
                query = query.filter(
                    or_(
                        CustomerMessage.message_body.contains(search_query),
                        CustomerMessage.user_id.cast(String).contains(search_query)
                    )
                )
            
            messages = query.limit(30).all()
        finally:
            session.close()
        
        # Display message list in scrollable container
        st.markdown("<div class='scrollable-container'>", unsafe_allow_html=True)
        
        if not messages:
            st.info("No messages match your filters.")
        else:
            for msg in messages:
                priority_color = utils.get_priority_color(msg.priority)
                status_color = utils.get_status_color(msg.status)
                time_ago = utils.format_timestamp(msg.timestamp)
                
                is_selected = st.session_state.selected_message_id == msg.id
                
                # Create a compact message card
                st.markdown(f"""
                <div class='message-item {'selected' if is_selected else ''}' 
                     onclick='selectMessage({msg.id})' 
                     style='cursor: pointer;'>
                    <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;'>
                        <div>
                            <strong style='color: #333;'>👤 Customer {msg.user_id}</strong>
                            <div style='font-size: 12px; color: #666; margin-top: 2px;'>{time_ago}</div>
                        </div>
                        <div style='display: flex; gap: 4px;'>
                            <span class='priority-badge' style='background-color: {priority_color}; color: white;'>
                                {msg.priority}
                            </span>
                        </div>
                    </div>
                    <div style='color: #444; font-size: 14px; line-height: 1.4; margin: 8px 0 12px 0;'>
                        {truncate_text(msg.message_body, 70)}
                    </div>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span class='status-badge' style='background-color: {status_color}; color: white;'>
                            {msg.status.replace('_', ' ')}
                        </span>
                        <button onclick='event.stopPropagation(); selectMessage({msg.id})' 
                                style='background: #0d6efd; color: white; border: none; padding: 4px 12px; 
                                       border-radius: 6px; font-size: 12px; cursor: pointer;'>
                            Select
                        </button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add actual Streamlit button for functionality
                if st.button(f"Select Message #{msg.id}", key=f"select_{msg.id}", 
                           help=f"Select message from Customer {msg.user_id}",
                           use_container_width=True):
                    st.session_state.selected_message_id = msg.id
                    st.session_state.selected_message = msg
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Center column: Chat interface
    with col_center:
        st.markdown("### 💬 Active Chat")
        
        if st.session_state.selected_message:
            msg = st.session_state.selected_message
            
            # Customer info header with status
            col_header1, col_header2 = st.columns([3, 2])
            with col_header1:
                st.markdown(f"**Customer ID:** `{msg.user_id}`")
                st.markdown(f"**Category:** `{msg.category.replace('_', ' ').title() if msg.category else 'N/A'}`")
            
            with col_header2:
                # Status update dropdown
                current_status = st.selectbox(
                    "Update Status",
                    ["pending", "in_progress", "resolved"],
                    index=["pending", "in_progress", "resolved"].index(msg.status),
                    key=f"status_update_{msg.id}",
                    label_visibility="collapsed"
                )
                if current_status != msg.status:
                    if update_message_status(msg.id, current_status, st.session_state.agent_name):
                        msg.status = current_status
                        st.success(f"✓ Status updated to {current_status}")
                        time.sleep(0.5)
                        st.rerun()
            
            st.markdown("---")
            
            # Chat history in a nice container
            chat_container = st.container()
            with chat_container:
                # Customer message bubble
                st.markdown(f"""
                <div class='customer-bubble'>
                    <div style='font-weight: 600; color: #333; margin-bottom: 5px;'>
                        👤 Customer {msg.user_id}
                    </div>
                    <div style='color: #444; line-height: 1.5;'>{msg.message_body}</div>
                    <div style='font-size: 11px; color: #888; margin-top: 8px;'>
                        {msg.timestamp.strftime('%b %d, %Y %I:%M %p') if msg.timestamp else 'N/A'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Agent response if exists
                if msg.response:
                    st.markdown(f"""
                    <div class='agent-bubble'>
                        <div style='font-weight: 600; margin-bottom: 5px;'>
                            👨‍💼 {msg.agent_id or st.session_state.agent_name}
                        </div>
                        <div style='line-height: 1.5;'>{msg.response}</div>
                        <div style='font-size: 11px; color: rgba(255,255,255,0.8); margin-top: 8px;'>
                            {msg.response_timestamp.strftime('%b %d, %Y %I:%M %p') if msg.response_timestamp else 'N/A'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Response section
            st.markdown("#### ✏️ Send Response")
            
            # Canned responses in expander
            with st.expander("💾 Quick Responses", expanded=True):
                canned_responses = get_canned_responses()
                if canned_responses:
                    canned_titles = [cr.title for cr in canned_responses]
                    selected_canned = st.selectbox(
                        "Choose a template",
                        [""] + canned_titles,
                        key="canned_select"
                    )
                    
                    if selected_canned:
                        selected_response = next((cr for cr in canned_responses if cr.title == selected_canned), None)
                        if selected_response:
                            response_text = st.text_area(
                                "Response Text",
                                value=selected_response.response_text,
                                height=120,
                                key=f"response_{msg.id}"
                            )
                            canned_id = selected_response.id
                        else:
                            response_text = st.text_area(
                                "Response Text",
                                height=120,
                                key=f"response_{msg.id}"
                            )
                            canned_id = None
                    else:
                        response_text = st.text_area(
                            "Response Text",
                            height=120,
                            key=f"response_{msg.id}"
                        )
                        canned_id = None
                else:
                    response_text = st.text_area(
                        "Response Text",
                        height=120,
                        key=f"response_{msg.id}"
                    )
                    canned_id = None
            
            # Send buttons
            col_btn1, col_btn2 = st.columns([3, 1])
            with col_btn1:
                if st.button("📤 Send Response", type="primary", use_container_width=True):
                    if response_text and response_text.strip():
                        if update_message_status(msg.id, "resolved", st.session_state.agent_name, response_text.strip()):
                            # Update canned response use count
                            if canned_id:
                                increment_canned_response_use(canned_id)
                            
                            st.success("✅ Response sent successfully!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.warning("⚠️ Please enter a response")
            with col_btn2:
                if st.button("⏸️ Mark as Pending", use_container_width=True):
                    update_message_status(msg.id, "pending", st.session_state.agent_name)
                    st.success("✓ Marked as pending")
                    time.sleep(0.5)
                    st.rerun()
        else:
            # Welcome screen when no message is selected
            st.markdown("""
            <div style='text-align: center; padding: 40px 20px; background: white; border-radius: 12px; margin-top: 20px;'>
                <div style='font-size: 48px; margin-bottom: 20px;'>💬</div>
                <h3 style='color: #666;'>Select a Conversation</h3>
                <p style='color: #888;'>Choose a message from the queue to start chatting</p>
                <div style='margin-top: 30px; color: #999; font-size: 14px;'>
                    <div>📨 <b>100+</b> messages in queue</div>
                    <div>🔥 <b>{}</b> high priority messages</div>
                    <div>⏳ <b>{}</b> pending responses</div>
                </div>
            </div>
            """.format(stats['high_priority'], stats['pending']), unsafe_allow_html=True)
    
    # Right column: Customer profile and tools
    with col_right:
        st.markdown("### 👤 Customer Profile")
        
        if st.session_state.selected_message:
            msg = st.session_state.selected_message
            
            # Customer profile card
            profile = get_customer_profile(msg.user_id)
            if profile:
                st.markdown(f"""
                <div class='profile-card'>
                    <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                        <div style='background: #e3f2fd; width: 50px; height: 50px; border-radius: 25px; 
                                    display: flex; align-items: center; justify-content: center; margin-right: 15px;'>
                            <span style='font-size: 20px;'>👤</span>
                        </div>
                        <div>
                            <h4 style='margin: 0;'>{profile.name}</h4>
                            <p style='color: #666; margin: 5px 0;'>{profile.phone}</p>
                        </div>
                    </div>
                    
                    <div style='margin-top: 15px;'>
                        <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                            <span style='color: #666;'>Credit Score:</span>
                            <span style='font-weight: bold; color: {'#4CAF50' if profile.credit_score >= 700 else '#FF9800' if profile.credit_score >= 600 else '#FF4B4B'};'>
                                {profile.credit_score}
                            </span>
                        </div>
                        <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                            <span style='color: #666;'>Repayment:</span>
                            <span style='font-weight: bold; color: {'#4CAF50' if profile.repayment_history == 'good' else '#FF9800' if profile.repayment_history == 'fair' else '#FF4B4B'};'>
                                {profile.repayment_history.title()}
                            </span>
                        </div>
                        <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                            <span style='color: #666;'>Total Loans:</span>
                            <span style='font-weight: bold;'>{profile.total_loans}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                            <span style='color: #666;'>Total Repaid:</span>
                            <span style='font-weight: bold;'>Ksh {profile.total_repaid:,}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info(f"No detailed profile found for Customer {msg.user_id}")
                st.markdown("""
                <div class='profile-card'>
                    <p style='color: #666; text-align: center;'>
                        Basic customer information is available.<br>
                        Detailed profile data can be added through admin panel.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Message analysis
            st.markdown("### 📊 Message Analysis")
            
            with st.container():
                # Calculate urgency score
                score, priority = utils.calculate_urgency_score(msg.message_body)
                
                # Simple gauge
                progress_value = min(score, 20) / 20
                color = "#FF4B4B" if score >= 12 else "#FFA500" if score >= 7 else "#4CAF50"
                
                st.markdown(f"""
                <div style='margin: 15px 0;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                        <span style='color: #666;'>Urgency Score:</span>
                        <span style='font-weight: bold; color: {color};'>{score}/20</span>
                    </div>
                    <div style='background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;'>
                        <div style='background: {color}; width: {progress_value * 100}%; height: 100%;'></div>
                    </div>
                    <div style='text-align: center; margin-top: 5px;'>
                        <span style='font-size: 12px; color: #666;'>{priority.upper()} PRIORITY</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Extracted information
                info = utils.extract_customer_info(msg.message_body)
                if info:
                    st.markdown("**📋 Extracted Details:**")
                    if 'phone_numbers' in info:
                        st.write(f"📱 **Phone:** {', '.join(info['phone_numbers'][:2])}")
                    if 'amounts' in info:
                        st.write(f"💰 **Amounts:** {', '.join(info['amounts'][:2])}")
                    if 'dates' in info:
                        st.write(f"📅 **Dates:** {', '.join(info['dates'][:2])}")
            
            # Add new canned response
            st.markdown("---")
            with st.expander("➕ Add New Quick Response"):
                with st.form("add_canned_response"):
                    new_title = st.text_input("Title")
                    new_response = st.text_area("Response Text")
                    new_category = st.selectbox(
                        "Category",
                        ["loan_application", "payment", "technical", "account", 
                         "urgent", "fraud", "general", "other"]
                    )
                    
                    submitted = st.form_submit_button("Add to Templates", type="primary")
                    if submitted:
                        if new_title and new_response:
                            # Add to database (you'll need to implement this function)
                            from database import add_new_canned_response
                            if add_new_canned_response(new_title, new_response, new_category):
                                st.success("✓ Template added successfully!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("Please fill in all fields")
        
        # Agent selector at bottom
        st.markdown("---")
        st.markdown("### 👥 Agent Settings")
        agent_options = ["Agent_01", "Agent_02", "Agent_03", "Agent_04", "Agent_05"]
        current_index = agent_options.index(st.session_state.agent_name) if st.session_state.agent_name in agent_options else 0
        
        new_agent = st.selectbox(
            "Select your agent profile",
            agent_options,
            index=current_index,
            label_visibility="collapsed"
        )
        
        if new_agent != st.session_state.agent_name:
            st.session_state.agent_name = new_agent
            st.success(f"✓ Switched to {new_agent}")
            time.sleep(0.5)
            st.rerun()
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time_diff = (datetime.now() - st.session_state.last_refresh).seconds
        if time_diff > 30:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

if __name__ == "__main__":
    main()
