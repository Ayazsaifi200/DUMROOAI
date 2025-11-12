"""
Dumroo AI Admin Panel - Streamlit Web Interface
Natural Language Querying System with Role-Based Access Control
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.rbac import rbac
    from src.data_manager import data_manager
    from src.query_processor import query_processor
except ImportError:
    # Fallback for running from different directory
    import sys
    sys.path.append('.')
    from src.rbac import rbac
    from src.data_manager import data_manager  
    from src.query_processor import query_processor

# Page configuration
st.set_page_config(
    page_title="Dumroo AI Admin Panel",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .user-info {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .query-suggestion {
        background: #f0f2f6;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        cursor: pointer;
        border-left: 3px solid #1f77b4;
    }
    .query-suggestion:hover {
        background: #e1e6f0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background: #dcf8c6;
        margin-left: 2rem;
    }
    .ai-message {
        background: #f1f1f1;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'query_suggestions' not in st.session_state:
    st.session_state.query_suggestions = []

def login_page():
    """Display login page"""
    st.markdown('<h1 class="main-header">🎓 Dumroo AI Admin Panel</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3>Natural Language Querying System with Role-Based Access Control</h3>
        <p>Ask questions in simple English or Hindi and get instant insights from your student data!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login to Continue")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if username and password:
                    user = rbac.authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_info = user
                        st.success(f"Welcome, {user.full_name}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username or password!")
                else:
                    st.warning("Please enter both username and password!")
    
    # Display demo accounts
    st.markdown("---")
    st.markdown("### 🎯 Demo Accounts")
    
    demo_accounts = [
        {"username": "super_admin", "password": "admin123", "access": "Full access to all data"},
        {"username": "north_admin", "password": "north123", "access": "North region students only"},
        {"username": "grade89_admin", "password": "grade123", "access": "Grade 8 & 9 students only"},
        {"username": "classab_admin", "password": "class123", "access": "Class A & B students only"},
    ]
    
    cols = st.columns(2)
    for i, account in enumerate(demo_accounts):
        with cols[i % 2]:
            st.info(f"**{account['username']}** / {account['password']}\n\n{account['access']}")

def logout():
    """Handle user logout"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = None
    st.session_state.conversation_history = []
    st.rerun()

def display_user_info():
    """Display current user information in sidebar"""
    user = st.session_state.user_info
    permissions = user.permissions
    
    st.sidebar.markdown(f"""
    <div class="user-info">
        <h3>👤 {user.full_name}</h3>
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Access Level:</strong> {permissions.access_level.value.replace('_', ' ').title()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display access restrictions
    st.sidebar.markdown("### 🔒 Access Restrictions")
    restrictions = []
    if permissions.regions:
        restrictions.append(f"**Regions:** {', '.join(permissions.regions)}")
    if permissions.grades:
        restrictions.append(f"**Grades:** {', '.join(permissions.grades)}")
    if permissions.classes:
        restrictions.append(f"**Classes:** {', '.join(permissions.classes)}")
    if permissions.subjects:
        restrictions.append(f"**Subjects:** {', '.join(permissions.subjects)}")
    
    if restrictions:
        for restriction in restrictions:
            st.sidebar.markdown(restriction)
    else:
        st.sidebar.success("No restrictions - Full access")
    
    # Capabilities
    st.sidebar.markdown("### ⚡ Capabilities")
    st.sidebar.markdown(f"**View Sensitive Data:** {'✅' if permissions.can_view_sensitive_data else '❌'}")
    st.sidebar.markdown(f"**Export Data:** {'✅' if permissions.can_export_data else '❌'}")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

def display_dashboard():
    """Display dashboard with key metrics"""
    st.markdown("## 📊 Dashboard Overview")
    
    # Get dashboard data
    dashboard_data = data_manager.get_dashboard_data(st.session_state.username)
    
    if dashboard_data['status'] == 'success':
        data = dashboard_data['data']
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 Total Students", 
                value=data['total_students'],
                help="Number of unique students you can access"
            )
        
        with col2:
            st.metric(
                label="📝 Total Assignments", 
                value=data['total_assignments'],
                help="Total homework assignments in your scope"
            )
        
        with col3:
            st.metric(
                label="⏳ Pending Submissions", 
                value=data['pending_submissions'],
                delta=f"-{data['submission_rate']}% completion rate",
                help="Assignments not yet submitted"
            )
        
        with col4:
            st.metric(
                label="📋 Upcoming Quizzes", 
                value=data['upcoming_quizzes'],
                help="Scheduled quizzes in your scope"
            )
        
        # Additional metrics
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.metric(
                label="📈 Avg Quiz Score", 
                value=f"{data['avg_quiz_score']}/100",
                help="Average quiz performance"
            )
        
        with col6:
            st.metric(
                label="📊 Submission Rate", 
                value=f"{data['submission_rate']}%",
                help="Percentage of assignments submitted"
            )
        
        with col7:
            st.metric(
                label="🔄 Recent Activity", 
                value=f"{data['recent_submissions']} submissions",
                help="Submissions in the last 7 days"
            )
        
        # Visualizations
        if data['grade_distribution'] or data['subject_distribution']:
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if data['grade_distribution']:
                    st.markdown("### 📚 Grade Distribution")
                    fig = px.bar(
                        x=list(data['grade_distribution'].keys()),
                        y=list(data['grade_distribution'].values()),
                        title="Students by Grade",
                        color=list(data['grade_distribution'].values()),
                        color_continuous_scale="viridis"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if data['subject_distribution']:
                    st.markdown("### 📖 Subject Distribution")
                    fig = px.pie(
                        values=list(data['subject_distribution'].values()),
                        names=list(data['subject_distribution'].keys()),
                        title="Assignments by Subject"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error(f"Error loading dashboard: {dashboard_data.get('error', 'Unknown error')}")

def display_query_interface():
    """Display the natural language query interface"""
    st.markdown("## 🤖 AI Query Interface")
    st.markdown("Ask questions in simple English or Hindi about your student data!")
    
    # Query suggestions
    if not st.session_state.query_suggestions:
        st.session_state.query_suggestions = query_processor.nlp.get_query_suggestions("")
    
    # Display suggestions
    with st.expander("💡 Query Suggestions (Click to use)", expanded=True):
        cols = st.columns(2)
        for i, suggestion in enumerate(st.session_state.query_suggestions):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                    execute_query(suggestion)
    
    # Query input
    query_input = st.text_input(
        "Ask your question:",
        placeholder="e.g., 'Which students haven't submitted homework?' or 'Kaunse students ne homework submit nahi kiya?'",
        key="query_input"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("🔍 Search", use_container_width=True):
            if query_input.strip():
                execute_query(query_input)
            else:
                st.warning("Please enter a question!")
    
    with col2:
        if st.button("🔄 Clear History", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()
    
    with col3:
        if st.button("💡 New Suggestions", use_container_width=True):
            st.session_state.query_suggestions = query_processor.nlp.get_query_suggestions("")
            st.rerun()

def execute_query(query_text):
    """Execute a natural language query"""
    with st.spinner("🤖 Processing your query..."):
        result = data_manager.execute_query(st.session_state.username, query_text)
        
        # Add to conversation history
        st.session_state.conversation_history.append({
            'query': query_text,
            'result': result,
            'timestamp': datetime.now()
        })
        
        # Display result immediately
        display_query_result(result, query_text, "execute")

def display_query_result(result, query_text, context="main"):
    """Display the result of a query"""
    st.markdown("---")
    st.markdown(f"### Query: *{query_text}*")
    
    if result['status'] == 'success':
        # Display summary
        st.success(result['message'])
        if 'summary' in result:
            st.info(f"📊 **Summary:** {result['summary']}")
        
        # Display data
        if result['data']:
            st.markdown(f"### 📋 Results ({len(result['data'])} records)")
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(result['data'])
            st.dataframe(df, use_container_width=True)
            
            # Export option (if user has permission)
            user_permissions = rbac.get_user_permissions(st.session_state.username)
            if user_permissions and user_permissions.can_export_data:
                csv = df.to_csv(index=False)
                # Provide a unique key to avoid DuplicateWidgetID errors when multiple
                # download buttons are rendered in the same page (for example: latest
                # result + conversation history). Use context and timestamp to ensure uniqueness.
                import uuid
                unique_key = f"download_{context}_{uuid.uuid4().hex[:8]}"
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=unique_key,
                )
        
        # Display visualizations
        if 'visualization_data' in result and result['visualization_data']:
            st.markdown("### 📊 Visualizations")
            display_visualizations(result['visualization_data'])
        
        # Display follow-up questions
        if 'query_info' in result and 'follow_up_questions' in result['query_info']:
            follow_ups = result['query_info']['follow_up_questions']
            if follow_ups:
                st.markdown("### 🤔 Follow-up Questions")
                cols = st.columns(min(len(follow_ups), 3))
                for i, question in enumerate(follow_ups):
                    with cols[i % len(cols)]:
                        if st.button(question, key=f"followup_{context}_{i}_{question[:20]}"):
                            execute_query(question)
    
    else:
        st.error(f"Query failed: {result.get('error', 'Unknown error')}")

def display_visualizations(viz_data):
    """Display visualizations from query results"""
    cols = st.columns(min(len(viz_data), 2))
    
    for i, (viz_type, viz_info) in enumerate(viz_data.items()):
        with cols[i % len(cols)]:
            if viz_info['type'] == 'bar':
                fig = px.bar(
                    x=viz_info['labels'],
                    y=viz_info['values'],
                    title=viz_type.replace('_', ' ').title()
                )
            elif viz_info['type'] == 'pie':
                fig = px.pie(
                    values=viz_info['values'],
                    names=viz_info['labels'],
                    title=viz_type.replace('_', ' ').title()
                )
            elif viz_info['type'] == 'horizontal_bar':
                fig = px.bar(
                    x=viz_info['values'],
                    y=viz_info['labels'],
                    orientation='h',
                    title=viz_type.replace('_', ' ').title()
                )
            else:
                continue
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def display_conversation_history():
    """Display conversation history"""
    if st.session_state.conversation_history:
        st.markdown("## 💬 Conversation History")
        
        for i, conversation in enumerate(reversed(st.session_state.conversation_history[-5:])):
            with st.expander(f"Query {len(st.session_state.conversation_history) - i}: {conversation['query'][:50]}..."):
                st.markdown(f"**Time:** {conversation['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Query:** {conversation['query']}")
                
                result = conversation['result']
                if result['status'] == 'success':
                    st.success(result['message'])
                    if result['data']:
                        st.dataframe(pd.DataFrame(result['data']), use_container_width=True)
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")

def main():
    """Main application function"""
    if not st.session_state.authenticated:
        login_page()
    else:
        # Display user info in sidebar
        display_user_info()
        
        # Main content
        st.markdown('<h1 class="main-header">🎓 Dumroo AI Admin Panel</h1>', unsafe_allow_html=True)
        
        # Navigation tabs
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🤖 AI Query", "💬 History"])
        
        with tab1:
            display_dashboard()
        
        with tab2:
            display_query_interface()
            
            # Display recent query results
            if st.session_state.conversation_history:
                st.markdown("---")
                st.markdown("## 🔍 Latest Query Result")
                latest = st.session_state.conversation_history[-1]
                display_query_result(latest['result'], latest['query'], "dashboard")
        
        with tab3:
            display_conversation_history()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p>🎓 Dumroo AI Admin Panel | Natural Language Querying System with Role-Based Access Control</p>
            <p>Built with Streamlit, LangChain, and AI-powered query processing</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()