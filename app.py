import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from sqlalchemy import desc, asc, or_

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

# Simple and Clean CSS
st.markdown("""
<style>
    /* Simple header */
    .main-header {
        background: #0d6efd;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    
    /* Simple metric cards */
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    
    /* Message items */
    .message-item {
        padding: 10px;
        border-radius: 6px;
        margin: 5px 0;
        background: white;
        border: 1px solid #e0e0e0;
    }
    
    .message-item:hover {
        background: #f8f9fa;
    }
    
    .message-item.selected {
        background: #e3f2fd;
        border-left: 3px solid #0d6efd;
    }
    
    /* Simple badges */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin: 2px;
    }
    
    /* Chat bubbles */
    .customer-bubble {
        background: #f0f2f6;
        padding: 12px 15px;
        border-radius: 15px 15px 15px 3px;
        margin: 8px 0;
        max-width: 85%;
    }
    
    .agent-bubble {
        background: #0d6efd;
        color: white;
        padding: 12px 15px;
        border-radius: 15px 15px 3px 15px;
        margin: 8px 0 8px auto;
        max-width: 85%;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_message_id' not in st.session_state:
    st.session_state.selected_message_id = None
if 'agent_name' not in st.session_state:
    st.session_state.agent_name = "Agent_01"
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

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

def main():
    """Main application function"""
    init_session()
    
    # Simple Header
    st.markdown("""
    <div class='main-header'>
        <h1 style='margin: 0;'>💬 Branch Customer Service</h1>
        <p style='margin: 5px 0 0 0; opacity: 0.9;'>Messaging Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent info and refresh
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        st.markdown(f"**Agent:** {st.session_state.agent_name}")
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=st.session_state.auto_refresh)
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh
            st.rerun()
    
    # Get statistics
    stats = get_message_stats()
    
    # Simple Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='color: #666; font-size: 14px;'>Total Messages</div>
            <div style='font-size: 24px; font-weight: bold; color: #0d6efd;'>{stats['total']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='color: #666; font-size: 14px;'>Pending</div>
            <div style='font-size: 24px; font-weight: bold; color: #FF9800;'>{stats['pending']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='color: #666; font-size: 14px;'>High Priority</div>
            <div style='font-size: 24px; font-weight: bold; color: #FF4B4B;'>{stats['high_priority']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='color: #666; font-size: 14px;'>Today</div>
            <div style='font-size: 24px; font-weight: bold; color: #4CAF50;'>{stats['today']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main three-column layout
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    # LEFT COLUMN: Message Queue
    with col_left:
        st.subheader("📨 Message Queue")
        
        # Simple Filters
        with st.expander("Filters", expanded=True):
            search_query = st.text_input("Search messages")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                priority_filter = st.selectbox("Priority", ["all", "high", "normal", "low"])
            with col_f2:
                status_filter = st.selectbox("Status", ["all", "pending", "in_progress", "resolved"])
            
            category_filter = st.selectbox("Category", ["all", "loan_application", "payment", "technical", "account", "other"])
        
        # Get filtered messages
        session = get_session()
        try:
            query = session.query(CustomerMessage).order_by(desc(CustomerMessage.urgency_score), desc(CustomerMessage.timestamp))
            
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
                        CustomerMessage.user_id.cast(str).contains(search_query)
                    )
                )
            
            messages = query.limit(50).all()
        finally:
            session.close()
        
        # Display message list
        for msg in messages:
            priority_color = utils.get_priority_color(msg.priority)
            status_color = utils.get_status_color(msg.status)
            time_ago = utils.format_timestamp(msg.timestamp)
            
            is_selected = st.session_state.selected_message_id == msg.id
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class='message-item {'selected' if is_selected else ''}'>
                    <div style='display: flex; justify-content: space-between;'>
                        <strong>Customer {msg.user_id}</strong>
                        <small style='color: #666;'>{time_ago}</small>
                    </div>
                    <div style='margin: 5px 0; font-size: 0.9em; color: #444;'>
                        {msg.message_body[:50]}...
                    </div>
                    <div style='display: flex; gap: 4px;'>
                        <span class='badge' style='background-color: {priority_color}; color: white;'>
                            {msg.priority}
                        </span>
                        <span class='badge' style='background-color: {status_color}; color: white;'>
                            {msg.status}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Select", key=f"select_{msg.id}", use_container_width=True):
                    st.session_state.selected_message_id = msg.id
                    st.rerun()
    
    # CENTER COLUMN: Chat Interface
    with col_center:
        st.subheader("💬 Chat")
        
        if st.session_state.selected_message_id:
            # Get selected message
            session = get_session()
            try:
                msg = session.query(CustomerMessage).filter(CustomerMessage.id == st.session_state.selected_message_id).first()
            finally:
                session.close()
            
            if msg:
                # Customer info and status
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    st.markdown(f"**Customer {msg.user_id}**")
                with col_c2:
                    current_status = st.selectbox(
                        "Status",
                        ["pending", "in_progress", "resolved"],
                        index=["pending", "in_progress", "resolved"].index(msg.status),
                        key=f"status_{msg.id}"
                    )
                    if current_status != msg.status:
                        update_message_status(msg.id, current_status, st.session_state.agent_name)
                        st.success(f"Status updated to {current_status}")
                        time.sleep(0.5)
                        st.rerun()
                
                st.markdown("---")
                
                # Chat history
                # Customer message
                st.markdown(f"""
                <div class='customer-bubble'>
                    <div style='font-weight: bold; margin-bottom: 5px;'>Customer {msg.user_id}</div>
                    <div>{msg.message_body}</div>
                    <div style='font-size: 0.8em; color: #666; margin-top: 5px;'>
                        {msg.timestamp.strftime('%b %d, %I:%M %p') if msg.timestamp else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Agent response if exists
                if msg.response:
                    st.markdown(f"""
                    <div class='agent-bubble'>
                        <div style='font-weight: bold; margin-bottom: 5px;'>{msg.agent_id or 'Agent'}</div>
                        <div>{msg.response}</div>
                        <div style='font-size: 0.8em; color: rgba(255,255,255,0.8); margin-top: 5px;'>
                            {msg.response_timestamp.strftime('%b %d, %I:%M %p') if msg.response_timestamp else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Response section
                # Canned responses
                canned_responses = get_canned_responses()
                canned_titles = [cr.title for cr in canned_responses]
                selected_canned = st.selectbox("Quick Responses", [""] + canned_titles)
                
                if selected_canned:
                    selected_response = next((cr for cr in canned_responses if cr.title == selected_canned), None)
                    if selected_response:
                        response_text = st.text_area("Your Response", value=selected_response.response_text, height=100)
                    else:
                        response_text = st.text_area("Your Response", height=100)
                else:
                    response_text = st.text_area("Your Response", height=100)
                
                col_r1, col_r2 = st.columns([4, 1])
                with col_r1:
                    if st.button("Send Response", type="primary", use_container_width=True):
                        if response_text.strip():
                            if update_message_status(msg.id, "resolved", st.session_state.agent_name, response_text.strip()):
                                st.success("Response sent!")
                                time.sleep(0.5)
                                st.rerun()
                        else:
                            st.warning("Please enter a response")
                with col_r2:
                    if st.button("Mark Pending", use_container_width=True):
                        update_message_status(msg.id, "pending", st.session_state.agent_name)
                        st.success("Marked as pending")
                        time.sleep(0.5)
                        st.rerun()
        else:
            # No message selected
            st.info("Select a message from the queue to start chatting")
    
    # RIGHT COLUMN: Customer Profile
    with col_right:
        st.subheader("👤 Customer Profile")
        
        if st.session_state.selected_message_id:
            # Get message to get user_id
            session = get_session()
            try:
                msg = session.query(CustomerMessage).filter(CustomerMessage.id == st.session_state.selected_message_id).first()
                if msg:
                    profile = get_customer_profile(msg.user_id)
            finally:
                session.close()
            
            if msg and profile:
                st.markdown(f"""
                <div class='metric-card'>
                    <p><strong>Name:</strong> {profile.name}</p>
                    <p><strong>Phone:</strong> {profile.phone}</p>
                    <p><strong>Credit Score:</strong> {profile.credit_score}</p>
                    <p><strong>Repayment:</strong> {profile.repayment_history.title()}</p>
                    <p><strong>Total Loans:</strong> {profile.total_loans}</p>
                    <p><strong>Total Repaid:</strong> Ksh {profile.total_repaid:,}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No profile found for this customer")
        
        # Agent selector
        st.markdown("---")
        st.subheader("Agent")
        agent_name = st.selectbox(
            "Select Agent",
            ["Agent_01", "Agent_02", "Agent_03", "Agent_04", "Agent_05"],
            index=0 if st.session_state.agent_name == "Agent_01" else 
                  1 if st.session_state.agent_name == "Agent_02" else
                  2 if st.session_state.agent_name == "Agent_03" else
                  3 if st.session_state.agent_name == "Agent_04" else 4,
            label_visibility="collapsed"
        )
        if agent_name != st.session_state.agent_name:
            st.session_state.agent_name = agent_name
            st.rerun()
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time_diff = (datetime.now() - st.session_state.last_refresh).seconds
        if time_diff > 30:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

if __name__ == "__main__":
    main()
