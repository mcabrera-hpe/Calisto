import streamlit as st
import requests
import os
import json
import logging
from datetime import datetime

# Import agent classes
from agents.core import Agent, MultiAgentOrchestrator

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
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")
MAX_TURNS = int(os.getenv("MAX_TURNS", "30"))

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'scenario' not in st.session_state:
    st.session_state.scenario = ""
if 'client' not in st.session_state:
    st.session_state.client = "Toyota"
if 'running' not in st.session_state:
    st.session_state.running = False
if 'stop_requested' not in st.session_state:
    st.session_state.stop_requested = False

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

def run_simulation(agent_configs: list, initial_message: str, max_turns: int = 3):
    """Run the multi-agent simulation"""
    logger.info(f"Starting simulation with {len(agent_configs)} agents")
    
    # Create Agent instances from configs
    agents = []
    for config in agent_configs:
        if not config.get('is_human'):  # Skip human agents for now
            agent = Agent(
                name=config['name'],
                company=config['company'],
                role=config['role'],
                objective=config['objective'],
                model=DEFAULT_MODEL
            )
            agents.append(agent)
    
    # Create orchestrator and run conversation
    orchestrator = MultiAgentOrchestrator(agents=agents, max_turns=max_turns)
    conversation_history = orchestrator.run(initial_message=initial_message)
    
    return conversation_history

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
# MAIN APP
# ============================================================================

# Header
st.title("🤖 Callisto")
st.caption("Multi-Agent Conversation Simulator")
st.divider()

# Simple two-column layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Setup")
    
    # Client selection
    client = st.selectbox(
        "Client Company",
        options=["Toyota", "Microsoft", "HPE"],
        key="client"
    )
    
    # Scenario input
    scenario = st.text_area(
        "Scenario",
        placeholder="Example: Negotiate server purchase with 30% discount",
        height=100,
        key="scenario"
    )
    
    # Max turns
    max_turns = st.slider("Max Turns", 1, 10, 5)
    
    # Number of agents
    num_agents = st.number_input("Number of Agents", min_value=2, max_value=5, value=2, step=1)
    
    st.divider()
    
    # Control buttons
    if not st.session_state.running:
        if st.button("▶️ Start Conversation", type="primary", disabled=not scenario, use_container_width=True):
            st.session_state.running = True
            st.session_state.conversation = []
            st.session_state.stop_requested = False
            st.rerun()
    else:
        if st.button("⏹️ Stop", type="secondary", use_container_width=True):
            st.session_state.stop_requested = True
            st.session_state.running = False
            st.rerun()
    
    if st.session_state.conversation:
        if st.button("🔄 New Conversation", use_container_width=True):
            st.session_state.conversation = []
            st.session_state.scenario = ""
            st.session_state.running = False
            st.rerun()

with col2:
    st.subheader("Conversation")
    
    # Conversation container
    if st.session_state.running:
        # Create agents dynamically based on num_agents
        agent_configs = [
            {
                "name": "Sarah",
                "company": "HPE",
                "role": "Sales Engineer",
                "objective": "Sell servers and close the deal"
            },
            {
                "name": "Yuki",
                "company": client,
                "role": "IT Procurement Manager",
                "objective": "Get the best price and terms"
            },
            {
                "name": "Marcus",
                "company": client,
                "role": "Technical Lead",
                "objective": "Ensure technical requirements are met"
            },
            {
                "name": "Lisa",
                "company": "HPE",
                "role": "Account Manager",
                "objective": "Build relationship and ensure customer satisfaction"
            },
            {
                "name": "Ken",
                "company": client,
                "role": "CFO",
                "objective": "Minimize costs and maximize ROI"
            }
        ]
        
        # Create only the number of agents requested
        agents = []
        for i in range(num_agents):
            config = agent_configs[i]
            agents.append(Agent(
                name=config["name"],
                company=config["company"],
                role=config["role"],
                objective=config["objective"],
                model=DEFAULT_MODEL
            ))
        
        # Run streaming conversation
        orchestrator = MultiAgentOrchestrator(
            agents=agents,
            max_turns=max_turns
        )
        
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            for message in orchestrator.run_streaming(initial_message=f"Let's discuss: {scenario}"):
                st.session_state.conversation.append(message)
                
                # Display all messages so far
                with message_placeholder.container():
                    for msg in st.session_state.conversation:
                        with st.chat_message("assistant" if msg['company'] == "HPE" else "user"):
                            # Show agent name and generation time if available
                            gen_time = msg.get('generation_time')
                            if gen_time:
                                st.markdown(f"**{msg['agent']}** ({msg['company']}) - *{gen_time:.2f}s*")
                            else:
                                st.markdown(f"**{msg['agent']}** ({msg['company']})")
                            st.write(msg['message'])
                
                # Show who's next with a spinner
                current_turn = len(st.session_state.conversation)
                if current_turn < max_turns * num_agents and not st.session_state.stop_requested:
                    # Calculate which agent is next in round-robin
                    next_agent_index = current_turn % num_agents
                    next_agent = agents[next_agent_index]
                    with status_placeholder:
                        with st.spinner(f"💭 {next_agent.name} is thinking..."):
                            pass  # Spinner will be replaced on next iteration
                
                # Check if stop was requested
                if st.session_state.stop_requested:
                    status_placeholder.empty()
                    st.warning("⏹️ Conversation stopped by user")
                    break
            
            status_placeholder.empty()
            st.session_state.running = False
            st.success(f"✅ Conversation complete! {len(st.session_state.conversation)} messages")
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.running = False
    
    elif st.session_state.conversation:
        # Display saved conversation
        for msg in st.session_state.conversation:
            with st.chat_message("assistant" if msg['company'] == "HPE" else "user"):
                # Show agent name and generation time if available
                gen_time = msg.get('generation_time')
                if gen_time:
                    st.markdown(f"**{msg['agent']}** ({msg['company']}) - *{gen_time:.2f}s*")
                else:
                    st.markdown(f"**{msg['agent']}** ({msg['company']})")
                st.write(msg['message'])
    else:
        st.info("👈 Configure the scenario and click Start to begin")

# Footer
st.divider()
st.caption("Callisto v0.1 | 100% Local | Powered by Mistral")
