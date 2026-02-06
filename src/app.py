import streamlit as st
import requests
import json
import logging
from datetime import datetime

# Import agent classes
from agents.core import Agent, MultiAgentOrchestrator

# Import shared configuration
from utils.config import WEAVIATE_URL, OLLAMA_URL, DEFAULT_MODEL, MAX_TURNS
from utils.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Callisto - Multi-Agent Simulator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

def create_agent(index: int, client: str) -> Agent:
    """Factory function to create agents based on index.
    
    Args:
        index: Agent index (0-4)
        client: Client company name
        
    Returns:
        Configured Agent instance
    """
    agent_configs = [
        ("Sarah", "HPE", "Sales Engineer", "Sell servers and close the deal"),
        ("Yuki", client, "IT Procurement Manager", "Get the best price and terms"),
        ("Marcus", client, "Technical Lead", "Ensure technical requirements are met"),
        ("Lisa", "HPE", "Account Manager", "Build relationship and ensure customer satisfaction"),
        ("Ken", client, "CFO", "Minimize costs and maximize ROI")
    ]
    name, company, role, objective = agent_configs[index]
    return Agent(name, company, role, objective, DEFAULT_MODEL)

def display_conversation(messages: list) -> None:
    """Display conversation messages in Streamlit chat format.
    
    Args:
        messages: List of message dicts with agent, company, message, and optional generation_time
    """
    for msg in messages:
        with st.chat_message("assistant" if msg['company'] == "HPE" else "user"):
            gen_time = msg.get('generation_time')
            if gen_time:
                st.markdown(f"**{msg['agent']}** ({msg['company']}) - *{gen_time:.2f}s*")
            else:
                st.markdown(f"**{msg['agent']}** ({msg['company']})")
            st.write(msg['message'])

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
        agents = [create_agent(i, client) for i in range(num_agents)]
        
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
                    display_conversation(st.session_state.conversation)
                
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
        display_conversation(st.session_state.conversation)
    else:
        st.info("👈 Configure the scenario and click Start to begin")

# Footer
st.divider()
st.caption("Callisto v0.1 | 100% Local | Powered by Mistral")
