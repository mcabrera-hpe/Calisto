import streamlit as st
import requests
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Callisto - Multi-Agent Simulator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Environment variables
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.1")
MAX_TURNS = int(os.getenv("MAX_TURNS", "30"))

# Initialize session state
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'create_scenario'
if 'suggested_agents' not in st.session_state:
    st.session_state.suggested_agents = None
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'conversation_active' not in st.session_state:
    st.session_state.conversation_active = False
if 'scenario_description' not in st.session_state:
    st.session_state.scenario_description = ""
if 'client' not in st.session_state:
    st.session_state.client = None
if 'participate' not in st.session_state:
    st.session_state.participate = False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_weaviate_health():
    """Check if Weaviate is accessible"""
    try:
        response = requests.get(f"{WEAVIATE_URL}/v1/.well-known/ready", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Weaviate health check failed: {e}")
        return False

def check_ollama_health():
    """Check if Ollama is accessible"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        return False

def list_tenants():
    """Get list of available client companies from Weaviate"""
    # Placeholder - will be implemented with Weaviate integration
    return ["HPE", "Toyota", "Microsoft"]

def suggest_agents_llm(scenario: str, client: str, include_human: bool):
    """Use LLM to suggest agent configurations based on scenario"""
    # Placeholder for LLM-powered agent suggestion
    # This will call Ollama with few-shot prompts
    
    logger.info(f"Generating agents for scenario: {scenario}")
    
    # Mock response for now
    if include_human:
        return [
            {
                "name": "You",
                "company": "HPE",
                "role": "Sales Engineer",
                "objective": "Close the deal with favorable terms",
                "is_human": True,
                "tools": ["rag"]
            },
            {
                "name": "Yuki Tanaka",
                "company": client,
                "role": "IT Procurement Manager",
                "objective": "Secure best price and service terms",
                "is_human": False,
                "tools": ["rag"]
            }
        ]
    else:
        return [
            {
                "name": "Sarah Chen",
                "company": "HPE",
                "role": "Sales Engineer",
                "objective": "Sell server infrastructure",
                "is_human": False,
                "tools": ["rag"]
            },
            {
                "name": "Yuki Tanaka",
                "company": client,
                "role": "IT Procurement Manager",
                "objective": "Negotiate best terms for server purchase",
                "is_human": False,
                "tools": ["rag"]
            }
        ]

# ============================================================================
# REUSABLE COMPONENTS
# ============================================================================

def render_agent_card(agent_config: dict, index: int):
    """Render an agent configuration card"""
    
    agent_type = "👤 Human" if agent_config.get('is_human') else "🤖 AI"
    
    with st.expander(
        f"Agent {index + 1}: {agent_config['name']} ({agent_config['company']} - {agent_config['role']})",
        expanded=True
    ):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Name:** {agent_config['name']}")
            st.markdown(f"**Company:** {agent_config['company']}")
            st.markdown(f"**Role:** {agent_config['role']}")
        
        with col2:
            st.markdown(f"**Type:** {agent_type}")
            st.markdown(f"**Objective:** {agent_config['objective']}")
        
        # Tools
        if 'tools' in agent_config and agent_config['tools']:
            st.markdown(f"**Tools:** {', '.join(agent_config['tools'])}")

# ============================================================================
# VIEW: CREATE SCENARIO
# ============================================================================

def render_create_scenario_view():
    """Render the scenario creation wizard"""
    
    # Sidebar - Scenario Input Form
    with st.sidebar:
        st.title("🤖 Callisto")
        st.markdown("**Multi-Agent Simulator**")
        st.markdown("---")
        
        # Client selection
        st.subheader("1. Select Client")
        available_clients = list_tenants()
        
        if not available_clients:
            st.warning("⚠️ No clients found. Please ingest documents first.")
            st.stop()
        
        client = st.selectbox(
            "Client Company",
            options=available_clients,
            help="Select which company the client agents will represent"
        )
        st.session_state.client = client
        
        st.markdown("---")
        
        # Scenario description
        st.subheader("2. Describe Scenario")
        scenario_description = st.text_area(
            "What should the agents discuss?",
            placeholder="Example: Negotiate server purchase contract with 30% discount request",
            height=100,
            help="Describe the conversation objective in natural language",
            value=st.session_state.scenario_description
        )
        st.session_state.scenario_description = scenario_description
        
        # Human participation
        participate = st.checkbox(
            "I want to participate",
            value=st.session_state.participate,
            help="Check this to act as one of the agents yourself"
        )
        st.session_state.participate = participate
        
        st.markdown("---")
        
        # Generate button
        generate_button = st.button(
            "🎲 Generate Agents",
            type="primary",
            disabled=not scenario_description,
            use_container_width=True
        )
        
        if generate_button:
            with st.spinner("Generating agents..."):
                suggested = suggest_agents_llm(
                    scenario_description,
                    client,
                    participate
                )
                st.session_state.suggested_agents = suggested
                st.rerun()
        
        # System status
        st.markdown("---")
        st.caption("**System Status**")
        weaviate_ok = check_weaviate_health()
        ollama_ok = check_ollama_health()
        st.caption(f"Weaviate: {'✅' if weaviate_ok else '❌'}")
        st.caption(f"Ollama: {'✅' if ollama_ok else '❌'}")
    
    # Main Area
    st.header("🎬 Scenario Creation")
    
    if not st.session_state.suggested_agents:
        # Show instructions
        st.info("👈 Fill out the form in the sidebar and click **'Generate Agents'** to begin")
        
        # Show example scenarios
        st.subheader("Example Scenarios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Simple B2B Sale**
            - Client: Toyota
            - Scenario: "Negotiate server purchase contract"
            - Agents: 2 (Sales, Procurement)
            """)
        
        with col2:
            st.markdown("""
            **Complex Enterprise Deal**
            - Client: Microsoft  
            - Scenario: "Multi-party contract with technical and legal review"
            - Agents: 4 (Sales, Tech, Procurement, Legal)
            """)
        
        st.markdown("---")
        st.subheader("💡 Quick Start")
        st.markdown("""
        1. Select a **client company** from the dropdown
        2. Describe what you want the agents to **discuss**
        3. Optionally check **"I want to participate"** to join the conversation
        4. Click **"Generate Agents"** to create the scenario
        5. Review the suggested agents and click **"Run Simulation"**
        """)
    
    else:
        # Show suggested agents
        st.subheader("✨ Step 2: Review Suggested Agents")
        
        agents = st.session_state.suggested_agents
        
        # Display each agent
        for i, agent_config in enumerate(agents):
            render_agent_card(agent_config, i)
        
        st.markdown("---")
        
        # Action buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("▶️ Run Simulation", type="primary", use_container_width=True):
                st.session_state.conversation_active = True
                st.session_state.current_view = 'active_conversation'
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate", use_container_width=True):
                with st.spinner("Regenerating agents..."):
                    suggested = suggest_agents_llm(
                        st.session_state.scenario_description,
                        st.session_state.client,
                        st.session_state.participate
                    )
                    st.session_state.suggested_agents = suggested
                    st.rerun()
        
        with col3:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.suggested_agents = None
                st.session_state.scenario_description = ""
                st.rerun()

# ============================================================================
# VIEW: ACTIVE CONVERSATION
# ============================================================================

def render_active_conversation_view():
    """Render the active conversation interface"""
    
    # Sidebar - Conversation Metrics
    with st.sidebar:
        st.title("📊 Conversation Metrics")
        
        # Turn counter
        turn_count = len(st.session_state.conversation)
        st.metric("Turn", f"{turn_count}/{MAX_TURNS}")
        
        st.markdown("---")
        
        # Placeholder for sentiment
        st.subheader("Sentiment")
        st.caption("(Sentiment tracking will be implemented)")
        
        st.markdown("---")
        
        # Action buttons
        if st.button("⏹️ End Conversation", use_container_width=True):
            st.session_state.conversation_active = False
            st.session_state.current_view = 'create_scenario'
            st.success("Conversation ended!")
            st.rerun()
        
        if st.button("💾 Save & Exit", use_container_width=True):
            # Save conversation (placeholder)
            st.success("Conversation saved!")
            st.session_state.conversation = []
            st.session_state.conversation_active = False
            st.session_state.current_view = 'create_scenario'
            st.rerun()
    
    # Main Area
    st.header("💬 Active Conversation")
    
    # Conversation header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Scenario:** {st.session_state.scenario_description}")
    with col2:
        st.markdown(f"**Client:** {st.session_state.client}")
    
    st.markdown("---")
    
    # Chat container
    if not st.session_state.conversation:
        st.info("🚀 Conversation will start here. Agents will exchange messages automatically.")
        
        # Placeholder for development
        if st.button("Simulate Agent Message (Dev)"):
            # Add a mock message
            st.session_state.conversation.append({
                "agent": "Sarah Chen",
                "company": "HPE",
                "role": "Sales Engineer",
                "message": "Hello! I'm excited to discuss our server solutions with you today.",
                "timestamp": datetime.now().isoformat(),
                "sentiment": 0.8
            })
            st.rerun()
    else:
        # Display messages
        for msg in st.session_state.conversation:
            is_company = (msg['company'] == 'HPE')
            avatar = "🏢" if is_company else "👤"
            
            with st.chat_message("assistant" if is_company else "user", avatar=avatar):
                st.markdown(f"**{msg['agent']}** ({msg['company']} - {msg['role']})")
                st.markdown(msg['message'])
                if 'sentiment' in msg:
                    sentiment_emoji = "😊" if msg['sentiment'] > 0.7 else "😐" if msg['sentiment'] > 0.4 else "😟"
                    st.caption(f"{sentiment_emoji} Sentiment: {msg['sentiment']:.2f}")
        
        # Human input (if participating)
        if st.session_state.participate:
            user_input = st.chat_input("Your response as company agent...")
            if user_input:
                # Add human message
                st.session_state.conversation.append({
                    "agent": "You",
                    "company": "HPE",
                    "role": "Sales Engineer",
                    "message": user_input,
                    "timestamp": datetime.now().isoformat(),
                    "sentiment": 0.7,  # Placeholder
                    "is_human": True
                })
                st.rerun()

# ============================================================================
# VIEW: PAST CONVERSATIONS
# ============================================================================

def render_past_conversations_view():
    """Render the past conversations list"""
    
    # Sidebar - Filters
    with st.sidebar:
        st.title("🔍 Filters")
        
        # Client filter
        all_clients = ["All"] + list_tenants()
        client_filter = st.selectbox("Client", options=all_clients)
        
        # Sort options
        sort_by = st.selectbox(
            "Sort By",
            options=["Most Recent", "Oldest First", "Highest Sentiment", "Most Turns"]
        )
        
        st.markdown("---")
        
        if st.button("Apply Filters", use_container_width=True):
            st.rerun()
        
        if st.button("Clear Filters", use_container_width=True):
            st.rerun()
    
    # Main Area
    st.header("📚 Past Conversations")
    
    # Placeholder - no conversations yet
    st.info("💡 No conversations saved yet. Run a simulation to create your first conversation!")
    
    st.markdown("---")
    st.markdown("**Conversations will appear here after you:**")
    st.markdown("1. Create a scenario")
    st.markdown("2. Run the simulation")
    st.markdown("3. Save the conversation")

# ============================================================================
# MAIN APP LAYOUT
# ============================================================================

# Header
st.title("🤖 Callisto")
st.markdown("**Multi-Agent Conversation Simulator** | Alpha v0.1.0")

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Create Scenario", "💬 Active Conversation", "📚 Past Conversations"])

with tab1:
    if st.session_state.current_view == 'create_scenario' or not st.session_state.conversation_active:
        render_create_scenario_view()
    else:
        st.info("Conversation is active. Go to the 'Active Conversation' tab to view it.")
        if st.button("Go to Active Conversation"):
            st.session_state.current_view = 'active_conversation'
            st.rerun()

with tab2:
    if st.session_state.conversation_active:
        render_active_conversation_view()
    else:
        st.info("No active conversation. Create a scenario first!")
        if st.button("Go to Create Scenario"):
            st.session_state.current_view = 'create_scenario'
            st.rerun()

with tab3:
    render_past_conversations_view()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Callisto v0.1.0 Alpha | Running on Docker Compose | 100% Local</small>
</div>
""", unsafe_allow_html=True)
