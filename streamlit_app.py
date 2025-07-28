import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path
import asyncio
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from utils.data_loader import data_loader
from activities.rag_analyzer import RAGAnalyzer
from activities.slack_poster import SlackPoster

# Page config
st.set_page_config(
    page_title="GTM Opportunity Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .opportunity-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    .high-intent {
        border-left: 4px solid #dc3545;
    }
    .medium-intent {
        border-left: 4px solid #ffc107;
    }
    .low-intent {
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🎯 GTM Opportunity Agent (Hunter)</h1>
        <p style="color: white; margin: 0.5rem 0 0 0;">Autonomous AI agent transforming data into revenue-generating actions</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("🔧 Agent Controls")
        
        # Refresh data
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
        
        # Settings
        st.subheader("⚙️ Settings")
        intent_threshold = st.slider("Intent Score Threshold", 0, 100, 75)
        auto_refresh = st.checkbox("Auto-refresh (5s)", False)
        
        # Reset demo data
        if st.button("🔄 Reset Demo Data"):
            reset_demo_data()
            st.success("Demo data reset!")
            st.rerun()

    # Auto-refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()

    # Main dashboard
    create_dashboard(intent_threshold)

def create_dashboard(intent_threshold):
    """Create the main dashboard interface."""
    
    # Load data
    accounts = data_loader.load_mock_accounts()
    high_intent_accounts = data_loader.get_high_intent_accounts(intent_threshold)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Accounts",
            value=len(accounts),
            delta=f"{len([a for a in accounts if not a.get('processed', False)])} unprocessed"
        )
    
    with col2:
        st.metric(
            label="🎯 High-Intent Accounts",
            value=len(high_intent_accounts),
            delta=f"Threshold: {intent_threshold}"
        )
    
    with col3:
        avg_intent = sum(a.get('intent_score', 0) for a in accounts) / len(accounts) if accounts else 0
        st.metric(
            label="📈 Avg Intent Score",
            value=f"{avg_intent:.1f}/100",
            delta=f"{len([a for a in accounts if a.get('intent_score', 0) >= 80])} hot leads"
        )
    
    with col4:
        total_revenue = sum(
            float(a.get('revenue', '0').replace('$', '').replace('M', '000000').replace('B', '000000000').replace(',', ''))
            for a in accounts
        )
        st.metric(
            label="💰 Total Revenue Potential",
            value=f"${total_revenue/1000000:.1f}M",
            delta="Pipeline value"
        )

    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Intent score distribution
        intent_scores = [a.get('intent_score', 0) for a in accounts]
        fig_hist = px.histogram(
            x=intent_scores,
            nbins=20,
            title="📊 Intent Score Distribution",
            labels={"x": "Intent Score", "y": "Number of Accounts"},
            color_discrete_sequence=["#667eea"]
        )
        fig_hist.add_vline(x=intent_threshold, line_dash="dash", line_color="red", 
                          annotation_text=f"Threshold ({intent_threshold})")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Industry breakdown
        industries = [a.get('industry', 'Unknown') for a in accounts]
        industry_counts = pd.Series(industries).value_counts()
        fig_pie = px.pie(
            values=industry_counts.values,
            names=industry_counts.index,
            title="🏢 Accounts by Industry"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # High-intent accounts section
    if high_intent_accounts:
        st.header("🚨 High-Intent Opportunities")
        
        # Process account button
        selected_account = st.selectbox(
            "Select account to process:",
            options=[f"{a['company_name']} ({a['intent_score']}/100)" for a in high_intent_accounts],
            index=0
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("🤖 Analyze with AI", type="primary"):
                process_account_workflow(high_intent_accounts[0])
        
        with col2:
            if st.button("📱 Send to Slack"):
                send_to_slack_demo(high_intent_accounts[0])
        
        with col3:
            st.info("💡 Demo Mode")

        # Display high-intent accounts
        for account in high_intent_accounts:
            display_opportunity_card(account)
    
    else:
        st.info("No high-intent accounts found above the threshold. Try lowering the threshold or reset demo data.")

    # All accounts table
    st.header("📋 All Accounts")
    
    # Create DataFrame for display
    df = pd.DataFrame(accounts)
    if not df.empty:
        # Add processed status
        df['Status'] = df['processed'].apply(lambda x: '✅ Processed' if x else '⏳ Pending')
        df['Intent Level'] = df['intent_score'].apply(get_intent_level)
        
        # Display table
        display_df = df[['company_name', 'industry', 'intent_score', 'employee_count', 'revenue', 'Intent Level', 'Status']]
        display_df.columns = ['Company', 'Industry', 'Intent Score', 'Employees', 'Revenue', 'Intent Level', 'Status']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

def display_opportunity_card(account):
    """Display an individual opportunity card."""
    intent_score = account.get('intent_score', 0)
    intent_class = get_intent_class(intent_score)
    
    with st.container():
        st.markdown(f"""
        <div class="opportunity-card {intent_class}">
            <h3>🏢 {account.get('company_name', 'Unknown Company')}</h3>
            <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                <div>
                    <strong>Intent Score:</strong> {intent_score}/100<br>
                    <strong>Industry:</strong> {account.get('industry', 'Unknown')}<br>
                    <strong>Employees:</strong> {account.get('employee_count', 'Unknown')}
                </div>
                <div>
                    <strong>Revenue:</strong> {account.get('revenue', 'Unknown')}<br>
                    <strong>Last Activity:</strong> {account.get('last_activity', 'Unknown')}<br>
                    <strong>Status:</strong> {'✅ Processed' if account.get('processed') else '⏳ Pending'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Intent signals
        signals = account.get('intent_signals', [])
        if signals:
            st.write("**🔍 Recent Intent Signals:**")
            for i, signal in enumerate(signals[:3]):  # Show top 3 signals
                signal_type = signal.get('type', '').replace('_', ' ').title()
                user_title = signal.get('user_title', 'Unknown Role')
                st.write(f"• {signal_type} by {user_title}")

def process_account_workflow(account):
    """Process an account through the AI workflow."""
    
    with st.spinner("🤖 Analyzing account with AI..."):
        progress_bar = st.progress(0)
        
        # Step 1: Initialize RAG
        progress_bar.progress(25)
        st.write("📚 Loading knowledge base...")
        
        try:
            analyzer = RAGAnalyzer()
            progress_bar.progress(50)
            
            # Step 2: Analyze
            st.write("🧠 Analyzing account...")
            analysis_result = analyzer.analyze_account(account)
            progress_bar.progress(75)
            
            # Step 3: Display results
            st.write("📊 Generating opportunity brief...")
            progress_bar.progress(100)
            
            # Display results
            st.success("✅ Analysis complete!")
            
            # Show opportunity brief
            st.subheader("📄 Opportunity Brief")
            st.markdown(analysis_result.get('opportunity_brief', 'No brief generated'))
            
            # Show recommended actions
            st.subheader("⚡ Recommended Actions")
            actions = analysis_result.get('recommended_actions', [])
            for i, action in enumerate(actions, 1):
                st.write(f"{i}. {action}")
            
            # Mark as processed
            data_loader.mark_account_processed(account.get('account_id'))
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            st.info("💡 This might happen in demo mode without full LLM setup")

def send_to_slack_demo(account):
    """Demonstrate Slack integration."""
    
    with st.spinner("📱 Sending to Slack..."):
        try:
            poster = SlackPoster()
            
            # Create mock analysis result
            mock_result = {
                'company_name': account.get('company_name'),
                'intent_score': account.get('intent_score'),
                'opportunity_brief': f"High-intent opportunity for {account.get('company_name')}",
                'urgency_level': 'HIGH'
            }
            
            result = poster.post_opportunity_brief(mock_result)
            
            if result.get('success'):
                st.success("✅ Posted to Slack successfully!")
                st.info(f"📱 Posted to {result.get('channel', '#gtm-opportunities')}")
            else:
                st.warning("⚠️ Posted in mock mode (no real Slack integration)")
                
        except Exception as e:
            st.error(f"❌ Slack posting failed: {str(e)}")

def get_intent_level(score):
    """Get intent level label from score."""
    if score >= 85:
        return "🔥 Very High"
    elif score >= 75:
        return "🚨 High"
    elif score >= 60:
        return "📈 Medium"
    else:
        return "📊 Low"

def get_intent_class(score):
    """Get CSS class for intent level."""
    if score >= 75:
        return "high-intent"
    elif score >= 60:
        return "medium-intent"
    else:
        return "low-intent"

def reset_demo_data():
    """Reset all accounts to unprocessed state."""
    accounts = data_loader.load_mock_accounts()
    for account in accounts:
        account['processed'] = False
    
    with open(data_loader.mock_data_path, 'w') as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    main() 