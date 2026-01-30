# UI Specification - Callisto

**Project:** Multi-Agent Conversation Simulator  
**UI Framework:** Streamlit  
**Version:** Alpha  
**Date:** January 30, 2026

---

## Overview

This document provides complete specifications for the Callisto Streamlit UI, including all screens, components, user flows, and integration points with the backend system.

**Purpose:** Enable another developer/agent to implement the UI independently using this specification.

---

## Table of Contents

1. [UI Framework & Setup](#ui-framework--setup)
2. [Application Structure](#application-structure)
3. [Screen Specifications](#screen-specifications)
4. [Component Library](#component-library)
5. [User Flows](#user-flows)
6. [Integration Points](#integration-points)
7. [State Management](#state-management)
8. [Error Handling](#error-handling)
9. [Implementation Guide](#implementation-guide)

---

## UI Framework & Setup

### Technology Stack

**Framework:** Streamlit 1.30+

**Why Streamlit:**
- Fast development (UI in ~150 lines)
- Python-native (no separate frontend)
- Hot-reload during development
- Built-in components for chat, charts, forms
- Good for internal tools and demos

**Configuration File:** `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"

[server]
port = 8501
address = "0.0.0.0"
fileWatcherType = "poll"  # Required for Docker hot-reload
runOnSave = true
```

### Entry Point

**File:** `src/app.py`

**Docker Command:**
```bash
streamlit run src/app.py --server.fileWatcherType poll --server.address 0.0.0.0
```

---

## Application Structure

### High-Level Layout

```
┌──────────────────────────────────────────────────────────┐
│  Callisto - Multi-Agent Conversation Simulator      [🌙] │  <- Header
├─────────────┬────────────────────────────────────────────┤
│             │                                            │
│   Sidebar   │           Main Content Area               │
│   (Fixed)   │           (Dynamic Tabs)                  │
│             │                                            │
│   [Mode]    │   Tab: Create Scenario | Past Convos     │
│   [Client]  │                                            │
│   [Scenario]│   [Content varies by tab and mode]        │
│   [Options] │                                            │
│             │                                            │
│   [Actions] │                                            │
│             │                                            │
└─────────────┴────────────────────────────────────────────┘
```

### File Structure

```python
# src/app.py - Main entry point

import streamlit as st
from agents.suggester import suggest_agents
from agents.factory import create_agent
from agents.core import MultiAgentOrchestrator, HumanAgent
from rag.retrieval import RAGTool
from utils.persistence import save_conversation, load_conversations
from utils.tenants import list_tenants
import requests

# Page config
st.set_page_config(
    page_title="Callisto - Agent Simulator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'suggested_agents' not in st.session_state:
    st.session_state.suggested_agents = None

# Main UI code below...
```

---

## Screen Specifications

### Screen 1: Scenario Creation (Default)

**When Shown:** Default view when app loads or when "Create Scenario" tab selected

**Layout:**

```
┌─────────────┬────────────────────────────────────────────┐
│  Sidebar    │  Main Area                                 │
│             │                                            │
│ Client:     │  Scenario Creation Wizard                  │
│ [Dropdown]  │                                            │
│             │  ┌──────────────────────────────────────┐  │
│ Scenario:   │  │ Step 1: Configure Scenario          │  │
│ [Textarea]  │  └──────────────────────────────────────┘  │
│             │                                            │
│ ☐ I want to │  Selected Client: Toyota                   │
│   participate                                            │
│             │  Scenario Description:                     │
│             │  "Negotiate server purchase contract"     │
│ [Generate   │                                            │
│  Agents]    │  ☑ I want to participate as company agent │
│             │                                            │
│             │  ┌──────────────────────────────────────┐  │
│             │  │ Step 2: Review Suggested Agents     │  │
│             │  └──────────────────────────────────────┘  │
│             │                                            │
│             │  Agent 1: You (HPE - Sales Engineer)      │
│             │  Objective: Sell 100 servers              │
│             │                                            │
│             │  Agent 2: Yuki (Toyota - Procurement)     │
│             │  Objective: Get best price                │
│             │                                            │
│             │  [Run Simulation]  [Regenerate Agents]    │
└─────────────┴────────────────────────────────────────────┘
```

**Components:**

#### Sidebar - Scenario Input Form

```python
with st.sidebar:
    st.title("🤖 Callisto")
    st.markdown("---")
    
    # Client selection
    st.subheader("1. Select Client")
    available_clients = list_tenants()  # Get from Weaviate
    if not available_clients:
        st.warning("No clients found. Please ingest documents first.")
        st.stop()
    
    client = st.selectbox(
        "Client Company",
        options=available_clients,
        help="Select which company the client agents will represent"
    )
    
    st.markdown("---")
    
    # Scenario description
    st.subheader("2. Describe Scenario")
    scenario_description = st.text_area(
        "What should the agents discuss?",
        placeholder="Example: Negotiate server purchase contract with 30% discount request",
        height=100,
        help="Describe the conversation objective in natural language"
    )
    
    # Human participation
    participate = st.checkbox(
        "I want to participate",
        help="Check this to act as one of the agents yourself"
    )
    
    st.markdown("---")
    
    # Generate button
    generate_button = st.button(
        "🎲 Generate Agents",
        type="primary",
        disabled=not scenario_description,
        use_container_width=True
    )
```

#### Main Area - Agent Preview

```python
st.header("Scenario Creation")

if not st.session_state.suggested_agents:
    # Show instructions
    st.info("👈 Fill out the form in the sidebar and click 'Generate Agents' to begin")
    
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

else:
    # Show suggested agents
    st.subheader("Step 2: Review Suggested Agents")
    
    agents = st.session_state.suggested_agents
    
    # Display each agent
    for i, agent_config in enumerate(agents):
        with st.expander(
            f"Agent {i+1}: {agent_config['name']} ({agent_config['company']} - {agent_config['role']})",
            expanded=True
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Name:** {agent_config['name']}")
                st.markdown(f"**Company:** {agent_config['company']}")
                st.markdown(f"**Role:** {agent_config['role']}")
            
            with col2:
                st.markdown(f"**Type:** {'Human' if agent_config.get('is_human') else 'AI'}")
                st.markdown(f"**Objective:** {agent_config['objective']}")
            
            # Show system prompt preview (collapsed by default)
            if 'system_prompt' in agent_config:
                with st.expander("System Prompt (Advanced)", expanded=False):
                    st.code(agent_config['system_prompt'], language='text')
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        run_button = st.button(
            "▶️ Run Simulation",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        regenerate_button = st.button(
            "🔄 Regenerate",
            use_container_width=True
        )
    
    with col3:
        cancel_button = st.button(
            "❌ Cancel",
            use_container_width=True
        )
```

**User Interactions:**

1. **Select Client:** Dropdown populates from `list_tenants()` function
2. **Enter Scenario:** User types description in textarea
3. **Check Participate:** Optional - adds HumanAgent to configuration
4. **Click Generate:** Triggers `suggest_agents()` call to LLM
5. **Review Agents:** Expandable cards show agent details
6. **Run/Regenerate/Cancel:** Action buttons

---

### Screen 2: Active Conversation

**When Shown:** After clicking "Run Simulation" on Screen 1

**Layout:**

```
┌─────────────┬────────────────────────────────────────────┐
│  Sidebar    │  Main Area - Active Conversation          │
│             │                                            │
│ Metrics     │  ┌──────────────────────────────────────┐  │
│             │  │ Conversation: HPE ↔ Toyota          │  │
│ Turn: 5/30  │  └──────────────────────────────────────┘  │
│             │                                            │
│ Sentiment:  │  🏢 Sarah (HPE - Sales Engineer)          │
│ Company 0.7 │  "Our ProLiant DL380 Gen11 servers are   │
│ ████████░░  │   perfect for your data center needs..." │
│             │                                            │
│ Client 0.6  │  👤 Yuki (Toyota - IT Procurement)        │
│ ███████░░░  │  "We're also considering Dell's offering │
│             │   with a 25% discount..."                │
│             │                                            │
│ [Chart]     │  🏢 Sarah (HPE - Sales Engineer)          │
│  Sentiment  │  "I understand budget is important. Let  │
│   ┌──┐      │   me check what I can offer..."          │
│  1│░░│      │                                            │
│   │██│      │  [Generating response...] ⚡              │
│   │██│      │                                            │
│  0└──┘      │  ┌──────────────────────────────────────┐  │
│    Turns    │  │ Your response: _____________________ │  │
│             │  │ [Send]                               │  │
│ [End Conv]  │  └──────────────────────────────────────┘  │
│ [Save]      │                                            │
└─────────────┴────────────────────────────────────────────┘
```

**Components:**

#### Sidebar - Conversation Metrics

```python
with st.sidebar:
    st.title("📊 Conversation Metrics")
    
    # Turn counter
    st.metric(
        "Turn",
        f"{len(st.session_state.conversation)}/{st.session_state.max_turns}"
    )
    
    st.markdown("---")
    
    # Sentiment scores
    st.subheader("Sentiment")
    
    if st.session_state.conversation:
        # Calculate current sentiment by side
        company_messages = [msg for msg in st.session_state.conversation 
                          if msg['company'] == 'HPE']
        client_messages = [msg for msg in st.session_state.conversation 
                         if msg['company'] != 'HPE']
        
        company_sentiment = calculate_avg_sentiment(company_messages)
        client_sentiment = calculate_avg_sentiment(client_messages)
        
        st.metric("Company", f"{company_sentiment:.2f}")
        st.progress(company_sentiment)
        
        st.metric("Client", f"{client_sentiment:.2f}")
        st.progress(client_sentiment)
    
    st.markdown("---")
    
    # Sentiment chart
    st.subheader("Sentiment Over Time")
    
    if len(st.session_state.conversation) >= 2:
        # Create dataframe for chart
        import pandas as pd
        
        sentiment_data = {
            'Turn': [],
            'Company': [],
            'Client': []
        }
        
        for i, msg in enumerate(st.session_state.conversation):
            sentiment_data['Turn'].append(i + 1)
            if msg['company'] == 'HPE':
                sentiment_data['Company'].append(msg['sentiment'])
                sentiment_data['Client'].append(None)
            else:
                sentiment_data['Company'].append(None)
                sentiment_data['Client'].append(msg['sentiment'])
        
        df = pd.DataFrame(sentiment_data)
        st.line_chart(df.set_index('Turn'))
    else:
        st.info("Sentiment chart appears after 2+ turns")
    
    st.markdown("---")
    
    # Action buttons
    if st.button("⏹️ End Conversation", use_container_width=True):
        st.session_state.conversation_active = False
        st.rerun()
    
    if st.button("💾 Save & Exit", use_container_width=True):
        save_conversation(st.session_state.conversation)
        st.success("Conversation saved!")
        st.session_state.conversation = []
        st.session_state.orchestrator = None
        st.rerun()
```

#### Main Area - Chat Interface

```python
st.header("Active Conversation")

# Conversation header
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"**Scenario:** {st.session_state.scenario_description}")
with col2:
    st.markdown(f"**Client:** {st.session_state.client}")
with col3:
    if st.session_state.orchestrator.waiting_for_human:
        st.warning("⏳ Waiting for your input")

st.markdown("---")

# Chat messages container
chat_container = st.container()

with chat_container:
    # Display all messages
    for msg in st.session_state.conversation:
        # Determine avatar and style based on company
        is_company = (msg['company'] == 'HPE')  # Adjust based on your company
        avatar = "🏢" if is_company else "👤"
        
        with st.chat_message(
            "assistant" if is_company else "user",
            avatar=avatar
        ):
            # Agent name and role
            st.markdown(f"**{msg['agent']}** ({msg['company']} - {msg['role']})")
            
            # Message content
            st.markdown(msg['message'])
            
            # Sentiment indicator (small)
            sentiment_emoji = "😊" if msg['sentiment'] > 0.7 else "😐" if msg['sentiment'] > 0.4 else "😟"
            st.caption(f"{sentiment_emoji} Sentiment: {msg['sentiment']:.2f}")

# Streaming message placeholder (for real-time updates)
if st.session_state.get('streaming_message'):
    with st.chat_message("assistant", avatar="🏢"):
        st.markdown(st.session_state.streaming_message)

# Human input (if in interactive mode)
if st.session_state.orchestrator.has_human_agent:
    if st.session_state.orchestrator.waiting_for_human:
        user_input = st.chat_input(
            "Your response as company agent...",
            key="human_input"
        )
        
        if user_input:
            # Process human input
            process_human_message(user_input)
            st.rerun()
    else:
        st.chat_input(
            "Waiting for AI agents to respond...",
            disabled=True,
            key="disabled_input"
        )

# Auto-scroll to bottom (Streamlit does this automatically for chat)
```

**Real-Time Streaming Implementation:**

```python
def stream_agent_response(agent, message, history):
    """Stream LLM response token by token"""
    
    # Placeholder for streaming message
    message_placeholder = st.empty()
    full_response = ""
    
    # Call Ollama streaming API
    for token in agent.respond_stream(message, history):
        full_response += token
        message_placeholder.markdown(full_response + "▌")  # Cursor
    
    # Final message without cursor
    message_placeholder.markdown(full_response)
    
    return full_response
```

**User Interactions:**

1. **Watch Messages:** Chat scrolls automatically as new messages appear
2. **See Sentiment:** Each message shows sentiment emoji and score
3. **Track Progress:** Sidebar shows turn count and sentiment trends
4. **Respond (Human Mode):** Type in chat_input when it's your turn
5. **End Early:** Click "End Conversation" to stop before max turns
6. **Save:** Click "Save & Exit" to persist and return to main screen

---

### Screen 3: Past Conversations

**When Shown:** When "Past Conversations" tab selected

**Layout:**

```
┌─────────────┬────────────────────────────────────────────┐
│  Sidebar    │  Main Area - Past Conversations           │
│             │                                            │
│ Filters     │  ┌──────────────────────────────────────┐  │
│             │  │ Past Conversations                   │  │
│ Client:     │  └──────────────────────────────────────┘  │
│ [ All ▼ ]   │                                            │
│             │  📅 Jan 30, 2026 - 10:30 AM               │
│ Date Range: │  HPE ↔ Toyota - Server Purchase           │
│ [________]  │  Turns: 12 | Final Sentiment: 0.75       │
│             │  Outcome: Agreement reached               │
│ Sort By:    │  [View] [Export] [Delete]                 │
│ [ Recent ▼] │                                            │
│             │  📅 Jan 29, 2026 - 3:15 PM                │
│             │  HPE ↔ Microsoft - Enterprise Contract    │
│ [Apply]     │  Turns: 24 | Final Sentiment: 0.62       │
│             │  Outcome: Negotiating                     │
│             │  [View] [Export] [Delete]                 │
│             │                                            │
│             │  📅 Jan 28, 2026 - 11:00 AM               │
│             │  HPE ↔ Toyota - Support SLA               │
│             │  Turns: 8 | Final Sentiment: 0.88        │
│             │  Outcome: Deal closed                     │
│             │  [View] [Export] [Delete]                 │
└─────────────┴────────────────────────────────────────────┘
```

**Components:**

#### Sidebar - Filters

```python
with st.sidebar:
    st.title("🔍 Filters")
    
    # Client filter
    all_clients = ["All"] + list_tenants()
    client_filter = st.selectbox(
        "Client",
        options=all_clients
    )
    
    # Date range
    st.subheader("Date Range")
    date_from = st.date_input("From")
    date_to = st.date_input("To")
    
    # Sort options
    sort_by = st.selectbox(
        "Sort By",
        options=["Most Recent", "Oldest First", "Highest Sentiment", "Most Turns"]
    )
    
    # Apply button
    if st.button("Apply Filters", use_container_width=True):
        st.session_state.filter_applied = True
        st.rerun()
    
    # Clear filters
    if st.button("Clear Filters", use_container_width=True):
        st.session_state.filter_applied = False
        st.rerun()
```

#### Main Area - Conversation List

```python
st.header("Past Conversations")

# Load conversations from Weaviate
conversations = load_conversations(
    client_filter=client_filter if client_filter != "All" else None,
    date_from=date_from,
    date_to=date_to,
    sort_by=sort_by
)

if not conversations:
    st.info("No conversations found. Run a simulation to create your first conversation!")
else:
    st.markdown(f"Found **{len(conversations)}** conversations")
    
    # Display each conversation as a card
    for conv in conversations:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"📅 **{conv['timestamp']}**")
                st.markdown(f"{conv['company']} ↔ {conv['client']}")
                st.caption(conv['scenario_description'])
            
            with col2:
                st.metric("Turns", conv['metrics']['total_turns'])
            
            with col3:
                st.metric("Final Sentiment", f"{conv['metrics']['final_client_sentiment']:.2f}")
            
            with col4:
                if st.button("👁️", key=f"view_{conv['id']}"):
                    st.session_state.viewing_conversation = conv['id']
                    st.rerun()
            
            # Outcome badge
            outcome = conv['metrics'].get('outcome', 'Unknown')
            if outcome == 'agreement':
                st.success(f"✅ {outcome.title()}")
            elif outcome == 'negotiating':
                st.warning(f"⏳ {outcome.title()}")
            else:
                st.info(f"ℹ️ {outcome.title()}")
            
            # Action buttons
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button("📄 Export", key=f"export_{conv['id']}"):
                    export_conversation(conv)
                    st.success("Exported to JSON!")
            
            with col_b:
                if st.button("🗑️ Delete", key=f"delete_{conv['id']}"):
                    if st.session_state.get(f'confirm_delete_{conv["id"]}'):
                        delete_conversation(conv['id'])
                        st.rerun()
                    else:
                        st.session_state[f'confirm_delete_{conv["id"]}'] = True
                        st.warning("Click again to confirm delete")
            
            st.markdown("---")
```

#### Conversation Replay Modal

```python
# When user clicks "View" button
if st.session_state.get('viewing_conversation'):
    conv_id = st.session_state.viewing_conversation
    conv = load_conversation_by_id(conv_id)
    
    # Show as a modal/dialog (use expander as workaround)
    with st.expander(f"Conversation: {conv['scenario_description']}", expanded=True):
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{conv['company']} ↔ {conv['client']}**")
            st.caption(f"Date: {conv['timestamp']}")
        with col2:
            if st.button("✖️ Close"):
                st.session_state.viewing_conversation = None
                st.rerun()
        
        st.markdown("---")
        
        # Show agents used
        st.subheader("Agents")
        for agent in conv['agents']:
            st.markdown(f"- **{agent['name']}** ({agent['company']} - {agent['role']})")
        
        st.markdown("---")
        
        # Show conversation
        st.subheader("Conversation")
        
        for msg in conv['conversation']:
            avatar = "🏢" if msg['company'] == conv['company'] else "👤"
            
            with st.chat_message("assistant" if msg['company'] == conv['company'] else "user", avatar=avatar):
                st.markdown(f"**{msg['agent']}** ({msg['company']} - {msg.get('role', 'Unknown')})")
                st.markdown(msg['message'])
                st.caption(f"Sentiment: {msg['sentiment']:.2f}")
        
        # Show metrics
        st.markdown("---")
        st.subheader("Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Turns", conv['metrics']['total_turns'])
        with col2:
            st.metric("Final Client Sentiment", f"{conv['metrics']['final_client_sentiment']:.2f}")
        with col3:
            st.metric("Final Company Sentiment", f"{conv['metrics']['final_company_sentiment']:.2f}")
```

---

## Component Library

### Reusable Components

#### 1. Agent Card Component

```python
def render_agent_card(agent_config: dict, index: int):
    """Render an agent configuration card"""
    
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
            agent_type = 'Human' if agent_config.get('is_human') else 'AI'
            st.markdown(f"**Type:** {agent_type}")
            st.markdown(f"**Objective:** {agent_config['objective']}")
        
        # Tools
        if 'tools' in agent_config:
            st.markdown(f"**Tools:** {', '.join(agent_config['tools'])}")
        
        # System prompt (advanced)
        if 'system_prompt' in agent_config:
            with st.expander("System Prompt (Advanced)", expanded=False):
                st.code(agent_config['system_prompt'], language='text')
```

#### 2. Sentiment Display Component

```python
def render_sentiment_display(sentiment: float, label: str = "Sentiment"):
    """Render sentiment score with emoji and color"""
    
    # Emoji based on sentiment
    if sentiment > 0.7:
        emoji = "😊"
        color = "green"
    elif sentiment > 0.4:
        emoji = "😐"
        color = "orange"
    else:
        emoji = "😟"
        color = "red"
    
    # Display
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<h1 style='text-align: center;'>{emoji}</h1>", unsafe_allow_html=True)
    with col2:
        st.metric(label, f"{sentiment:.2f}")
        st.progress(sentiment)
```

#### 3. Loading Spinner Component

```python
def show_loading_spinner(message: str = "Processing..."):
    """Show loading spinner with custom message"""
    
    with st.spinner(message):
        yield
```

#### 4. Error Display Component

```python
def show_error(error_message: str, details: str = None):
    """Display error message with optional details"""
    
    st.error(f"❌ {error_message}")
    
    if details:
        with st.expander("Error Details"):
            st.code(details)
```

---

## User Flows

### Flow 1: Create and Run Autonomous Scenario

```
User Action                           System Response                    UI Update
───────────────────────────────────────────────────────────────────────────────
1. Opens app                       → Load default screen              → Show scenario wizard
2. Selects client "Toyota"         → Update session state             → Dropdown shows "Toyota"
3. Types scenario description      → Update session state             → Textarea shows text
4. Clicks "Generate Agents"        → Call suggest_agents(LLM)        → Show loading spinner
                                   → Parse JSON response              → Display agent cards
5. Reviews suggested agents        → (No action)                      → Agents expanded
6. Clicks "Run Simulation"         → Create agents                    → Switch to conversation view
                                   → Start orchestrator               
7. (Autonomous - no user action)   → Agents exchange messages         → Chat updates in real-time
                                   → Calculate sentiment each turn    → Chart updates
                                   → Check termination                
8. Conversation ends               → Save to Weaviate                 → Show "Save & Exit" button
9. Clicks "Save & Exit"            → Export JSON                      → Return to scenario wizard
                                   → Clear session state              → Reset form
```

### Flow 2: Participate in Conversation (Human Mode)

```
User Action                           System Response                    UI Update
───────────────────────────────────────────────────────────────────────────────
1-3. (Same as Flow 1)
4. Checks "I want to participate"  → Update session state             → Checkbox checked
5. Clicks "Generate Agents"        → Call suggest_agents(LLM)        → Show loading spinner
                                   → Add HumanAgent to config         → Show 2 agents (You + AI)
6. Reviews agents                  → (No action)                      → Your agent marked "Human"
7. Clicks "Run Simulation"         → Create agents                    → Switch to conversation view
                                   → Start orchestrator               → Show chat input (enabled)
8. Client agent sends message      → Append to history                → New message appears
                                   → Calculate sentiment              → Chart updates
                                   → Wait for human                   → Show "Waiting for your input"
9. User types response             → (No action)                      → Text appears in input
10. User presses Enter             → Process human message            → Message added to chat
                                   → Client agent responds            → New AI message streams in
11. (Repeat 8-10)                  → Continue conversation            → Chat grows
12. Clicks "End Conversation"      → Force termination                → Conversation stops
13. Clicks "Save & Exit"           → Save with human messages marked  → Return to wizard
```

### Flow 3: Regenerate Agents

```
User Action                           System Response                    UI Update
───────────────────────────────────────────────────────────────────────────────
1-4. (Same as Flow 1)
5. Reviews suggested agents        → (No action)                      → Shows 2 agents
6. Clicks "Regenerate Agents"      → Call suggest_agents(LLM) again  → Show loading spinner
                                   → Different seed/temperature       → New agents appear
7. Reviews new agents              → (No action)                      → Different names/roles
8. Satisfied, clicks "Run"         → (Continue Flow 1 from step 6)    
```

### Flow 4: View Past Conversation

```
User Action                           System Response                    UI Update
───────────────────────────────────────────────────────────────────────────────
1. Clicks "Past Conversations" tab → Query Weaviate                   → Show conversation list
2. Selects client filter "Toyota"  → Filter conversations             → List updates (fewer items)
3. Clicks "View" on a conversation → Load full conversation           → Show replay modal
4. Scrolls through messages        → (No action)                      → Messages display
5. Views metrics                   → (No action)                      → Metrics shown
6. Clicks "Close"                  → Clear viewing state              → Return to list
7. Clicks "Export" on conversation → Generate JSON file               → Download triggered
                                   → Save to data/conversations/      → Success message
```

---

## Integration Points

### 1. Backend Integration

#### Scenario Suggestion (LLM Call)

```python
# Called when user clicks "Generate Agents"

from agents.suggester import suggest_agents

suggested_agents = suggest_agents(
    scenario_description=scenario_description,
    client_company=client,
    include_human=participate
)

# Returns: List[Dict] with agent configurations
# [
#   {"name": "Sarah", "company": "HPE", "role": "Sales", ...},
#   {"name": "Yuki", "company": "Toyota", "role": "Procurement", ...}
# ]

st.session_state.suggested_agents = suggested_agents
```

#### Agent Creation

```python
# Called when user clicks "Run Simulation"

from agents.factory import create_agent
from agents.core import MultiAgentOrchestrator, HumanAgent
from rag.retrieval import RAGTool

agents = []

for agent_config in st.session_state.suggested_agents:
    if agent_config.get('is_human'):
        agent = HumanAgent(name=agent_config['name'])
    else:
        # Create RAG tool with tenant
        rag_tool = RAGTool(tenant=agent_config['company'].lower().replace(' ', '_'))
        
        agent = create_agent(
            name=agent_config['name'],
            company=agent_config['company'],
            role=agent_config['role'],
            objective=agent_config['objective'],
            tools=[rag_tool]
        )
    
    agents.append(agent)

# Create orchestrator
orchestrator = MultiAgentOrchestrator(
    agents=agents,
    max_turns=30
)

st.session_state.orchestrator = orchestrator
```

#### Conversation Execution

```python
# Run conversation loop (async or in background)

def run_conversation():
    """Execute conversation and update UI in real-time"""
    
    initial_message = st.session_state.suggested_agents[0].get('initial_message', "Let's begin.")
    
    for turn_data in st.session_state.orchestrator.run_stream(initial_message):
        # turn_data = {"agent": "Sarah", "message": "...", "sentiment": 0.7, ...}
        
        # Add to conversation history
        st.session_state.conversation.append(turn_data)
        
        # Trigger UI update
        st.rerun()
```

#### Persistence

```python
# Save conversation

from utils.persistence import save_conversation

conversation_data = {
    "scenario": {
        "description": st.session_state.scenario_description,
        "client_company": st.session_state.client,
        "timestamp": datetime.now().isoformat()
    },
    "agents": st.session_state.suggested_agents,
    "conversation": st.session_state.conversation,
    "metrics": calculate_metrics(st.session_state.conversation)
}

save_conversation(conversation_data)
# Saves to Weaviate ConversationHistory collection
# Exports to data/conversations/<timestamp>.json
```

### 2. Weaviate Integration

#### List Available Clients

```python
from utils.tenants import list_tenants

def list_tenants() -> List[str]:
    """Get all tenants from Weaviate Documents collection"""
    
    client = weaviate.Client("http://weaviate:8080")
    collection = client.collections.get("Documents")
    tenants = collection.tenants.get()
    
    return [t.name for t in tenants]
```

#### Load Past Conversations

```python
from utils.persistence import load_conversations

def load_conversations(
    client_filter: str = None,
    date_from: date = None,
    date_to: date = None,
    sort_by: str = "Most Recent"
) -> List[Dict]:
    """Query ConversationHistory collection"""
    
    client = weaviate.Client("http://weaviate:8080")
    collection = client.collections.get("ConversationHistory")
    
    # Build filter
    filters = []
    if client_filter:
        filters.append({"path": ["client_company"], "operator": "Equal", "valueText": client_filter})
    if date_from:
        filters.append({"path": ["timestamp"], "operator": "GreaterThanEqual", "valueDate": date_from.isoformat()})
    
    # Query
    results = collection.query.fetch_objects(
        filters=filters,
        limit=100
    )
    
    # Sort
    # ... sorting logic
    
    return results
```

### 3. Ollama Integration (Streaming)

```python
import requests
import json

def stream_llm_response(agent, message, history):
    """Stream response from Ollama and update UI in real-time"""
    
    # Build messages
    messages = [
        {"role": "system", "content": agent.system_prompt}
    ]
    for msg in history[-5:]:  # Last 5 turns for context
        messages.append({"role": "user", "content": msg['message']})
    messages.append({"role": "user", "content": message})
    
    # Stream from Ollama
    response = requests.post(
        "http://ollama:11434/api/chat",
        json={
            "model": "llama3.1",
            "messages": messages,
            "stream": True
        },
        stream=True
    )
    
    # Display streaming
    message_placeholder = st.empty()
    full_response = ""
    
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            if "message" in chunk:
                token = chunk["message"]["content"]
                full_response += token
                
                # Update UI with cursor
                message_placeholder.markdown(full_response + "▌")
    
    # Final message without cursor
    message_placeholder.markdown(full_response)
    
    return full_response
```

---

## State Management

### Session State Variables

Streamlit's `st.session_state` is used to persist data across reruns:

```python
# Initialize in app.py

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    
    # Scenario creation
    st.session_state.suggested_agents = None
    st.session_state.scenario_description = ""
    st.session_state.client = None
    st.session_state.participate = False
    
    # Active conversation
    st.session_state.conversation = []
    st.session_state.orchestrator = None
    st.session_state.conversation_active = False
    st.session_state.max_turns = 30
    st.session_state.streaming_message = ""
    
    # Past conversations
    st.session_state.viewing_conversation = None
    st.session_state.filter_applied = False
    
    # UI state
    st.session_state.current_tab = "Create Scenario"
```

### State Transitions

```
Initial State
    ↓
[User fills form] → suggested_agents = None
    ↓
[Click Generate] → suggested_agents = [agent1, agent2]
    ↓
[Click Run] → orchestrator created, conversation_active = True
    ↓
[Conversation runs] → conversation = [msg1, msg2, ...]
    ↓
[Click Save] → conversation saved, state reset
    ↓
Back to Initial State
```

---

## Error Handling

### Error Scenarios & UI Response

#### 1. Ollama Not Responding

```python
try:
    response = requests.post("http://ollama:11434/api/chat", ...)
except requests.ConnectionError:
    st.error("❌ Cannot connect to Ollama. Is it running?")
    st.info("Run: `docker-compose logs ollama` to check status")
    st.stop()
except requests.Timeout:
    st.error("❌ Ollama request timed out. Try again or use a smaller model.")
    st.stop()
```

#### 2. Weaviate Connection Error

```python
try:
    tenants = list_tenants()
except Exception as e:
    st.error("❌ Cannot connect to Weaviate")
    with st.expander("Error Details"):
        st.code(str(e))
    st.info("Run: `docker-compose restart weaviate`")
    st.stop()
```

#### 3. Invalid LLM Response (Scenario Generation)

```python
try:
    suggested_agents = suggest_agents(scenario, client, participate)
except json.JSONDecodeError:
    st.error("❌ LLM returned invalid response. Please try again.")
    if st.button("Regenerate"):
        st.rerun()
except Exception as e:
    st.error(f"❌ Error generating agents: {str(e)}")
    st.stop()
```

#### 4. No Tenants Found

```python
available_clients = list_tenants()

if not available_clients:
    st.warning("⚠️ No clients found in database.")
    st.info("""
    Please ingest documents first:
    
    ```bash
    docker-compose exec app python scripts/ingest_documents.py \\
      --company "Toyota" --path /app/data/documents/toyota/
    ```
    """)
    st.stop()
```

#### 5. Conversation Save Error

```python
try:
    save_conversation(conversation_data)
    st.success("✅ Conversation saved successfully!")
except Exception as e:
    st.error("❌ Failed to save conversation")
    st.warning("Exporting to JSON as fallback...")
    
    # Fallback to JSON only
    json_path = f"data/conversations/{datetime.now().isoformat()}.json"
    with open(json_path, 'w') as f:
        json.dump(conversation_data, f, indent=2)
    
    st.success(f"✅ Saved to {json_path}")
```

---

## Implementation Guide

### Step-by-Step Implementation

#### Phase 1: Basic Structure (Day 13)

1. Create `src/app.py` with page config
2. Add sidebar with client dropdown (hardcoded initially)
3. Add scenario textarea
4. Add "Generate Agents" button (dummy action)
5. Test: UI renders, form accepts input

#### Phase 2: Backend Integration (Day 13-14)

6. Integrate `list_tenants()` for client dropdown
7. Connect "Generate Agents" to `suggest_agents()`
8. Display agent cards from LLM response
9. Add "Regenerate" functionality
10. Test: End-to-end scenario generation

#### Phase 3: Conversation View (Day 14)

11. Create conversation screen with chat container
12. Add sidebar metrics (turn counter)
13. Integrate orchestrator for autonomous mode
14. Display messages as they're generated
15. Test: Autonomous 2-agent conversation

#### Phase 4: Streaming & Sentiment (Day 15)

16. Implement streaming LLM responses
17. Add sentiment analysis per turn
18. Create sentiment chart with `st.line_chart()`
19. Update chart in real-time
20. Test: Sentiment tracks correctly

#### Phase 5: Human Mode (Day 18-19)

21. Add `st.chat_input()` for human responses
22. Detect when it's human's turn
23. Enable/disable input based on turn
24. Process human input through orchestrator
25. Test: Human can participate successfully

#### Phase 6: Persistence & Replay (Day 16-17)

26. Add "Save & Exit" button
27. Integrate `save_conversation()`
28. Create "Past Conversations" tab
29. Load and filter conversations
30. Implement conversation replay view
31. Test: Conversations persist and reload

#### Phase 7: Polish (Day 20-21)

32. Add error handling for all API calls
33. Improve loading states with spinners
34. Add helpful tooltips and hints
35. Test all user flows
36. Fix bugs and edge cases

---

## Testing Checklist

### Manual Testing

- [ ] App loads without errors
- [ ] Client dropdown populates from Weaviate
- [ ] Scenario description accepts text
- [ ] "Generate Agents" calls LLM successfully
- [ ] Agent cards display correctly
- [ ] "Regenerate" produces different agents
- [ ] "Run Simulation" starts conversation
- [ ] Messages appear in real-time
- [ ] Streaming shows token-by-token
- [ ] Sentiment chart updates each turn
- [ ] Turn counter increments correctly
- [ ] Conversation ends at max turns or termination
- [ ] "Save & Exit" persists conversation
- [ ] Past conversations tab shows saved items
- [ ] Filters work (client, date)
- [ ] Conversation replay displays correctly
- [ ] Export creates JSON file
- [ ] Human mode: chat input appears
- [ ] Human mode: user can type and send
- [ ] Human mode: AI responds to user
- [ ] Error messages show for connection issues
- [ ] App recovers gracefully from errors

---

## Performance Considerations

### Optimization Tips

1. **Lazy Loading:** Don't query past conversations until tab is clicked
2. **Pagination:** Limit past conversations to 20 per page
3. **Caching:** Use `@st.cache_data` for tenant list
4. **Debouncing:** Don't update chart every single token (batch updates)
5. **Memory:** Clear large conversation objects after save

### Example: Caching Tenant List

```python
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_available_clients():
    """Cached tenant list"""
    return list_tenants()

# Usage
available_clients = get_available_clients()
```

---

## Accessibility

### Best Practices

- Use semantic HTML (Streamlit handles most of this)
- Provide alt text for emojis (use labels)
- Ensure sufficient color contrast
- Support keyboard navigation (Streamlit default)
- Add tooltips with `help=` parameter

---

## Future Enhancements

### Phase 2+ UI Features

1. **Scenario Templates**
   - Save successful scenarios as templates
   - Template library in sidebar
   - One-click scenario load

2. **Advanced Metrics Dashboard**
   - Multiple sentiment dimensions
   - Token usage tracking
   - Response time per agent

3. **Conversation Branching**
   - Checkpoint system
   - "Restart from turn X" feature
   - Compare different outcomes

4. **Export Options**
   - PDF export with formatting
   - Markdown export
   - CSV export of metrics

5. **Dark/Light Mode Toggle**
   - User preference saved
   - Toggle in header

6. **Mobile Responsive** (if moving away from Streamlit)
   - Optimized for tablet/phone
   - Touch-friendly controls

---

## Handoff Checklist

**Before implementing, ensure you have:**

- [x] Access to `src/agents/suggester.py` API
- [x] Access to `src/agents/factory.py` API
- [x] Access to `src/agents/core.py` (Agent, Orchestrator classes)
- [x] Access to `src/rag/retrieval.py` (RAGTool)
- [x] Access to `src/utils/persistence.py` (save/load functions)
- [x] Access to `src/utils/tenants.py` (list_tenants function)
- [x] Streamlit 1.30+ installed
- [x] Docker environment running (Weaviate, Ollama accessible)
- [x] Sample data ingested for testing

**Questions to ask backend team:**

1. What's the exact function signature for `suggest_agents()`?
2. What's the return format from `create_agent()`?
3. How does `orchestrator.run_stream()` work? (Async? Generator?)
4. What's the Weaviate ConversationHistory schema?
5. How should errors from Ollama be handled?

---

## Contact & Support

For questions about this UI specification, contact the project lead or refer to:
- [Technical Requirements Document](Technical%20Requirements%20Document%20-%20Callisto.md)
- [Implementation Plan](Implementation%20Plan%20-%20Callisto.md)

---

**End of UI Specification**
