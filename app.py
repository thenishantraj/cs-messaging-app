import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import plotly.express as px
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

# Custom CSS for styling
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Chat bubbles */
    .customer-message {
        background-color: #f0f2f6;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    
    .agent-message {
        background-color: #0d6efd;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    /* Priority badges */
    .priority-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    
    /* Message list items */
    .message-item {
        padding: 12px;
        border-radius: 8px;
        margin: 4px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .message-item:hover {
        background-color: #f8f9fa;
    }
    
    .message-item.selected {
        background-color: #e3f2fd;
        border-left: 4px solid #0d6efd;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* Scrollable containers */
    .scrollable {
        overflow-y: auto;
        max-height: 70vh;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
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
        responses = session.query(CannedResponse).order_by(CannedResponse.use_count.desc()).all()
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

def add_new_canned_response(title, response_text, category):
    """Add new canned response"""
    session = get_session()
    try:
        response = CannedResponse(
            title=title,
            response_text=response_text,
            category=category
        )
        session.add(response)
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
    
    # Header
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.markdown("<h1 class='custom-header'>💬 Branch CS Messaging</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align: center; padding-top: 20px;'><h3>Welcome, {st.session_state.agent_name}</h3></div>", unsafe_allow_html=True)
    with col3:
        auto_refresh = st.checkbox("Auto-refresh", value=st.session_state.auto_refresh)
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh
            st.rerun()
    
    # Get statistics
    stats = get_message_stats()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='color: #666; margin: 0;'>Total Messages</h4>
            <h2 style='color: #0d6efd; margin: 10px 0;'>{stats['total']}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='color: #666; margin: 0;'>Pending</h4>
            <h2 style='color: #FF9800; margin: 10px 0;'>{stats['pending']}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='color: #666; margin: 0;'>High Priority</h4>
            <h2 style='color: #FF4B4B; margin: 10px 0;'>{stats['high_priority']}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='color: #666; margin: 0;'>Today</h4>
            <h2 style='color: #4CAF50; margin: 10px 0;'>{stats['today']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Main three-column layout
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    # Left column: Message queue
    with col_left:
        st.subheader("📨 Message Queue")
        
        # Filters
        with st.expander("Filters", expanded=True):
            search_query = st.text_input("Search messages", key="search_filter")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                priority_filter = st.selectbox(
                    "Priority",
                    ["all", "high", "medium", "low", "normal"],
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
                        CustomerMessage.user_id.cast(String).contains(search_query)
                    )
                )
            
            messages = query.limit(50).all()
        finally:
            session.close()
        
        # Display message list
        st.markdown("<div class='scrollable'>", unsafe_allow_html=True)
        for msg in messages:
            priority_color = utils.get_priority_color(msg.priority)
            status_color = utils.get_status_color(msg.status)
            time_ago = utils.format_timestamp(msg.timestamp)
            
            is_selected = st.session_state.selected_message and st.session_state.selected_message.id == msg.id
            
            st.markdown(f"""
            <div class='message-item {'selected' if is_selected else ''}' onclick='selectMessage({msg.id})'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <strong>Customer {msg.user_id}</strong>
                    <small style='color: #666;'>{time_ago}</small>
                </div>
                <div style='margin: 8px 0; font-size: 0.9em; color: #444;'>
                    {msg.message_body[:60]}...
                </div>
                <div style='display: flex; gap: 4px;'>
                    <span class='priority-badge' style='background-color: {priority_color}; color: white;'>
                        {msg.priority.upper()}
                    </span>
                    <span class='status-badge' style='background-color: {status_color}; color: white;'>
                        {msg.status.replace('_', ' ').upper()}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add selection functionality
            if st.button(f"Select", key=f"select_{msg.id}", use_container_width=True):
                st.session_state.selected_message = msg
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Center column: Chat interface
    with col_center:
        st.subheader("💬 Chat")
        
        if st.session_state.selected_message:
            msg = st.session_state.selected_message
            
            # Customer info header
            col_c1, col_c2 = st.columns([3, 1])
            with col_c1:
                st.markdown(f"### Customer {msg.user_id}")
            with col_c2:
                # Status update
                current_status = st.selectbox(
                    "Update Status",
                    ["pending", "in_progress", "resolved"],
                    index=["pending", "in_progress", "resolved"].index(msg.status),
                    key=f"status_update_{msg.id}"
                )
                if current_status != msg.status:
                    if update_message_status(msg.id, current_status, st.session_state.agent_name):
                        msg.status = current_status
                        st.success(f"Status updated to {current_status}")
                        time.sleep(0.5)
                        st.rerun()
            
            # Chat history
            chat_container = st.container()
            with chat_container:
                # Customer message
                st.markdown(f"""
                <div class='customer-message'>
                    <div style='font-weight: bold; margin-bottom: 4px;'>Customer {msg.user_id}</div>
                    <div>{msg.message_body}</div>
                    <div style='font-size: 0.8em; color: #666; margin-top: 8px;'>
                        {utils.format_timestamp(msg.timestamp)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Agent response if exists
                if msg.response:
                    st.markdown(f"""
                    <div class='agent-message'>
                        <div style='font-weight: bold; margin-bottom: 4px;'>{msg.agent_id or 'Agent'}</div>
                        <div>{msg.response}</div>
                        <div style='font-size: 0.8em; color: rgba(255,255,255,0.8); margin-top: 8px;'>
                            {utils.format_timestamp(msg.response_timestamp)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Response input
            st.markdown("---")
            
            # Canned responses
            canned_responses = get_canned_responses()
            canned_titles = [cr.title for cr in canned_responses]
            selected_canned = st.selectbox("Quick Responses", [""] + canned_titles)
            
            if selected_canned:
                selected_response = next((cr for cr in canned_responses if cr.title == selected_canned), None)
                if selected_response:
                    response_text = st.text_area("Response", value=selected_response.response_text, height=100)
                else:
                    response_text = st.text_area("Response", height=100)
            else:
                response_text = st.text_area("Response", height=100)
            
            col_r1, col_r2 = st.columns([4, 1])
            with col_r1:
                if st.button("Send Response", type="primary", use_container_width=True):
                    if response_text.strip():
                        if update_message_status(msg.id, "resolved", st.session_state.agent_name, response_text):
                            # Update canned response use count
                            if selected_canned:
                                session = get_session()
                                try:
                                    cr = session.query(CannedResponse).filter(CannedResponse.title == selected_canned).first()
                                    if cr:
                                        cr.use_count += 1
                                        session.commit()
                                finally:
                                    session.close()
                            
                            st.success("Response sent!")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.warning("Please enter a response")
            
            with col_r2:
                if st.button("Mark as Pending", use_container_width=True):
                    update_message_status(msg.id, "pending", st.session_state.agent_name)
                    st.success("Marked as pending")
                    time.sleep(0.5)
                    st.rerun()
        else:
            st.info("Select a message from the queue to start chatting")
    
    # Right column: Customer profile and tools
    with col_right:
        st.subheader("👤 Customer Profile")
        
        if st.session_state.selected_message:
            msg = st.session_state.selected_message
            profile = get_customer_profile(msg.user_id)
            
            if profile:
                # Customer info
                st.markdown(f"""
                <div class='metric-card'>
                    <h4 style='margin: 0 0 10px 0;'>Customer Information</h4>
                    <p><strong>Name:</strong> {profile.name}</p>
                    <p><strong>Phone:</strong> {profile.phone}</p>
                    <p><strong>Email:</strong> {profile.email or 'N/A'}</p>
                    <p><strong>Credit Score:</strong> <span style='color: {'#4CAF50' if profile.credit_score >= 700 else '#FF9800' if profile.credit_score >= 600 else '#FF4B4B'}'>
                        {profile.credit_score}
                    </span></p>
                    <p><strong>Repayment History:</strong> <span style='color: {'#4CAF50' if profile.repayment_history == 'good' else '#FF9800' if profile.repayment_history == 'fair' else '#FF4B4B'}'>
                        {profile.repayment_history.upper()}
                    </span></p>
                    <p><strong>Total Loans:</strong> {profile.total_loans}</p>
                    <p><strong>Total Repaid:</strong> Ksh {profile.total_repaid:,}</p>
                    <p><strong>Last Loan:</strong> Ksh {profile.last_loan_amount:,}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("No profile found for this customer")
            
            # Message analysis
            st.markdown("### 📊 Message Analysis")
            info = utils.extract_customer_info(msg.message_body)
            
            if info:
                st.markdown("**Extracted Information:**")
                if 'phone_numbers' in info:
                    st.write(f"📱 Phone: {', '.join(info['phone_numbers'])}")
                if 'amounts' in info:
                    st.write(f"💰 Amounts: {', '.join(info['amounts'])}")
                if 'dates' in info:
                    st.write(f"📅 Dates: {', '.join(info['dates'])}")
            
            # Urgency score visualization
            score, priority = utils.calculate_urgency_score(msg.message_body)
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = min(score, 20),
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Urgency Score"},
                gauge = {
                    'axis': {'range': [0, 20]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 7], 'color': "lightgreen"},
                        {'range': [7, 14], 'color': "yellow"},
                        {'range': [14, 20], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 10
                    }
                }
            ))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
            
            # Message category
            category = utils.categorize_message(msg.message_body)
            st.markdown(f"**Category:** {category.replace('_', ' ').title()}")
            
        # Canned response management
        st.markdown("---")
        with st.expander("➕ Add New Canned Response"):
            new_title = st.text_input("Title")
            new_response = st.text_area("Response Text")
            new_category = st.selectbox(
                "Category",
                ["loan_application", "payment", "technical", "account", 
                 "urgent", "fraud", "general", "other"]
            )
            
            if st.button("Add Response", type="primary"):
                if new_title and new_response:
                    if add_new_canned_response(new_title, new_response, new_category):
                        st.success("Canned response added!")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.warning("Please fill in all fields")
        
        # Agent selector
        st.markdown("---")
        st.subheader("👥 Agent Settings")
        agent_name = st.selectbox(
            "Select Agent",
            ["Agent_01", "Agent_02", "Agent_03", "Agent_04", "Agent_05"],
            index=0 if st.session_state.agent_name == "Agent_01" else 
                  1 if st.session_state.agent_name == "Agent_02" else
                  2 if st.session_state.agent_name == "Agent_03" else
                  3 if st.session_state.agent_name == "Agent_04" else 4
        )
        if agent_name != st.session_state.agent_name:
            st.session_state.agent_name = agent_name
            st.rerun()
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time_diff = (datetime.now() - st.session_state.last_refresh).seconds
        if time_diff > 30:  # Refresh every 30 seconds
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    
    # Hidden JavaScript for message selection
    st.markdown("""
    <script>
    function selectMessage(messageId) {
        // This would be handled by Streamlit buttons in the actual implementation
        console.log("Selected message:", messageId);
    }
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
