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
    page_title="The Grid - Multi-Agent Simulator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_URL = os.getenv("API_URL", "http://api:8000")

# Initialize session state
if 'assistant_history' not in st.session_state:
    st.session_state.assistant_history = []
if 'scenario_config' not in st.session_state:
    st.session_state.scenario_config = None
if 'scenario_messages' not in st.session_state:
    st.session_state.scenario_messages = []
if 'scenario_running' not in st.session_state:
    st.session_state.scenario_running = False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def display_chat_message(role: str, content: str) -> None:
    """Display a chat message."""
    with st.chat_message(role):
        st.write(content)


def display_scenario_message(msg: dict) -> None:
    """Display a scenario message."""
    with st.chat_message("assistant" if msg['company'] == "HPE" else "user"):
        gen_time = msg.get('generation_time')
        if gen_time:
            st.markdown(f"**{msg['agent']}** ({msg['company']}) - *{gen_time:.2f}s*")
        else:
            st.markdown(f"**{msg['agent']}** ({msg['company']})")
        st.write(msg['message'])


def parse_scenario_config(message: str) -> dict:
    """Parse JSON config from assistant message."""
    try:
        # Look for JSON block in message
        if "{" in message and "}" in message:
            start = message.index("{")
            end = message.rindex("}") + 1
            config = json.loads(message[start:end])
            
            # Validate all required fields are present
            required_fields = ["ready", "agents", "scenario", "client", "max_turns"]
            if all(field in config for field in required_fields) and config.get("ready"):
                logger.info(f"Valid config parsed: {config}")
                return config
            else:
                missing = [f for f in required_fields if f not in config]
                logger.warning(f"Config missing fields: {missing}")
    except Exception as e:
        logger.error(f"Failed to parse config: {e}")
    return None


# ============================================================================
# LAYOUT
# ============================================================================

st.title("⚡ The Grid")
st.caption("Multi-Agent Conversation Simulator")
st.divider()

# Two-column layout
col1, col2 = st.columns([1, 2])

# ============================================================================
# LEFT PANEL - ASSISTANT CHAT
# ============================================================================

with col1:
    st.subheader("💬 Configure Scenario")
    
    # Display chat history
    chat_container = st.container(height=400)
    with chat_container:
        if not st.session_state.assistant_history:
            st.info("👋 Hi! I'm Grid. Tell me what scenario you'd like to simulate.")
        else:
            for msg in st.session_state.assistant_history:
                display_chat_message(msg["role"], msg["content"])
    
    # Chat input
    if not st.session_state.scenario_running:
        user_input = st.chat_input("Type your message...")
        
        if user_input:
            # Add user message to history
            st.session_state.assistant_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Call assistant API
            try:
                response = requests.post(
                    f"{API_URL}/assistant/chat",
                    json={
                        "message": user_input,
                        "history": st.session_state.assistant_history[:-1]  # Exclude current message
                    },
                    stream=True,
                    timeout=60
                )
                response.raise_for_status()
                
                # Parse SSE stream
                assistant_message = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data = json.loads(line_str[6:])
                            if 'error' in data:
                                st.error(f"Error: {data['error']}")
                                break
                            assistant_message = data.get('message', '')
                
                if assistant_message:
                    # Add assistant response to history
                    st.session_state.assistant_history.append({
                        "role": "assistant",
                        "content": assistant_message
                    })
                    
                    # Check if scenario is ready
                    config = parse_scenario_config(assistant_message)
                    if config:
                        st.session_state.scenario_config = config
                    
                    st.rerun()
                
            except Exception as e:
                st.error(f"Assistant error: {e}")
                logger.error(f"Assistant chat failed: {e}")
    
    # Start scenario button
    st.divider()
    if st.session_state.scenario_config and not st.session_state.scenario_running:
        config = st.session_state.scenario_config
        
        # Validate required fields
        required_fields = ["scenario", "client", "agents", "max_turns"]
        missing_fields = [f for f in required_fields if f not in config]
        
        if missing_fields:
            st.warning(f"⚠️ Config incomplete: Missing {', '.join(missing_fields)}")
            st.json(config)
        else:
            st.success("✅ Scenario ready!")
            st.json({
                "Scenario": config["scenario"],
                "Client": config["client"],
                "Agents": config["agents"],
                "Max Turns": config["max_turns"]
            })
            
            if st.button("▶️ Start Scenario", type="primary", use_container_width=True):
                st.session_state.scenario_running = True
                st.session_state.scenario_messages = []
                st.rerun()
    
    if st.session_state.scenario_running:
        if st.button("⏹️ Stop Scenario", type="secondary", use_container_width=True):
            st.session_state.scenario_running = False
            st.rerun()
    
    if st.session_state.scenario_messages and not st.session_state.scenario_running:
        if st.button("🔄 New Scenario", use_container_width=True):
            st.session_state.assistant_history = []
            st.session_state.scenario_config = None
            st.session_state.scenario_messages = []
            st.rerun()

# ============================================================================
# RIGHT PANEL - SCENARIO SIMULATION
# ============================================================================

with col2:
    st.subheader("🎭 Scenario Simulation")
    
    if st.session_state.scenario_running:
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            config = st.session_state.scenario_config
            
            # Debug logging
            logger.info(f"Starting scenario with config: {config}")
            
            # Start scenario via API
            payload = {
                "scenario": config["scenario"],
                "client": config["client"],
                "agents": config["agents"],
                "max_turns": config["max_turns"]
            }
            logger.info(f"Sending payload: {payload}")
            
            response = requests.post(
                f"{API_URL}/scenarios/start",
                json=payload,
                stream=True,
                timeout=600
            )
            response.raise_for_status()
            
            # Process SSE stream
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data = json.loads(line_str[6:])
                        
                        if 'error' in data:
                            st.error(f"Error: {data['error']}")
                            break
                        
                        st.session_state.scenario_messages.append(data)
                        
                        # Display all messages
                        with message_placeholder.container():
                            for msg in st.session_state.scenario_messages:
                                display_scenario_message(msg)
                        
                        # Show progress
                        with status_placeholder:
                            st.info(f"💭 Turn {data.get('turn', '?')}/{config['max_turns']}...")
            
            status_placeholder.empty()
            st.session_state.scenario_running = False
            st.success(f"✅ Scenario complete! {len(st.session_state.scenario_messages)} messages")
            
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text
            st.error(f"Scenario error: {e}")
            st.error(f"Details: {error_detail}")
            logger.error(f"Scenario failed: {e} - Details: {error_detail}")
            st.session_state.scenario_running = False
        except Exception as e:
            st.error(f"Scenario error: {e}")
            logger.error(f"Scenario failed: {e}")
            st.session_state.scenario_running = False
    
    elif st.session_state.scenario_messages:
        # Display saved scenario
        for msg in st.session_state.scenario_messages:
            display_scenario_message(msg)
    else:
        st.info("👈 Chat with Grid to configure a scenario, then click Start")

# Footer
st.divider()
st.caption("The Grid v0.1 | Powered by External LLM API")
