import streamlit as st
import requests
import json
import logging
import os

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

# API Configuration
API_URL = os.getenv("API_URL", "http://api:8000")

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
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

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
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            # Create conversation via API
            response = requests.post(
                f"{API_URL}/conversations",
                json={
                    "scenario": scenario,
                    "client": client,
                    "num_agents": num_agents,
                    "max_turns": max_turns
                },
                timeout=10
            )
            response.raise_for_status()
            conv_id = response.json()["conversation_id"]
            st.session_state.conversation_id = conv_id
            
            logger.info(f"Created conversation {conv_id}")
            
            # Start streaming conversation
            stream_response = requests.post(
                f"{API_URL}/conversations/{conv_id}/start",
                stream=True,
                timeout=600  # 10 min timeout
            )
            stream_response.raise_for_status()
            
            # Process SSE stream
            for line in stream_response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        message = json.loads(line_str[6:])
                        
                        # Check for error
                        if 'error' in message:
                            st.error(f"Error: {message['error']}")
                            break
                        
                        st.session_state.conversation.append(message)
                        
                        # Display all messages so far
                        with message_placeholder.container():
                            display_conversation(st.session_state.conversation)
                        
                        # Show status
                        with status_placeholder:
                            with st.spinner(f"💭 Agents are thinking..."):
                                pass
                        
                        # Check if stop was requested
                        if st.session_state.stop_requested:
                            status_placeholder.empty()
                            st.warning("⏹️ Conversation stopped by user")
                            break
            
            status_placeholder.empty()
            st.session_state.running = False
            st.success(f"✅ Conversation complete! {len(st.session_state.conversation)} messages")
            
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            logger.error(f"API request failed: {e}")
            st.session_state.running = False
        except Exception as e:
            st.error(f"Error: {e}")
            logger.error(f"Unexpected error: {e}")
            st.session_state.running = False
    
    elif st.session_state.conversation:
        # Display saved conversation
        display_conversation(st.session_state.conversation)
    else:
        st.info("👈 Configure the scenario and click Start to begin")

# Footer
st.divider()
st.caption("Callisto v0.1 | 100% Local | Powered by Mistral")
