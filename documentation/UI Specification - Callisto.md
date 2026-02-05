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
│  🤖 Callisto                                             │  <- Header
│  Multi-Agent Conversation Simulator                      │
├─────────────┬────────────────────────────────────────────┤
│             │                                            │
│   Setup     │           Conversation                     │
│  (Column 1) │           (Column 2)                       │
│             │                                            │
│  Client:    │   [Messages display here]                 │
│  [Dropdown] │                                            │
│             │   💭 Agent is thinking... [spinner]       │
│  Scenario:  │                                            │
│  [Textarea] │                                            │
│             │                                            │
│  Max Turns: │                                            │
│  [Slider]   │                                            │
│             │                                            │
│  # Agents:  │                                            │
│  [Number]   │                                            │
│             │                                            │
│  [▶️ Start] │                                            │
│  [⏹️ Stop]  │                                            │
│  [🔄 New]   │                                            │
└─────────────┴────────────────────────────────────────────┘
│  Callisto v0.1 | 100% Local | Powered by Mistral        │  <- Footer
└──────────────────────────────────────────────────────────┘
```

### Simplified Design Principles

**No Tabs:** Single page layout for simplicity
**No Wizards:** Direct input and execution
**Real-time Feedback:** Streaming messages with visual indicators
**Minimal Chrome:** Focus on the conversation

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

### Single Page Layout

**Layout:** Simple two-column design

**Left Column - Setup Panel:**
- Client selection dropdown
- Scenario description textarea  
- Max turns slider (1-10)
- Number of agents selector (2-5)
- Action buttons (Start/Stop/New)

**Right Column - Conversation Display:**
- Real-time message stream
- Loading indicators with agent names
- Status messages (complete/stopped/error)

**No Tabs, No Wizards, No Separate Screens**

### Layout Implementation

```
┌─────────────┬────────────────────────────────────────────┐
│  Setup      │  Conversation                              │
│             │                                            │
│ Client:     │  🏢 Sarah (HPE)                            │
│ [Toyota ▼]  │  "Our servers offer excellent value..."   │
│             │                                            │
│ Scenario:   │  👤 Yuki (Toyota)                          │
│ [Negotiate  │  "What's your best price for 100 units?"  │
│  server     │                                            │
│  purchase]  │  💭 Sarah is thinking... [spinner]        │
│             │                                            │
│ Max Turns:  │                                            │
│ [━━━━○━━━]  │                                            │
│     5       │                                            │
│             │                                            │
│ # Agents:   │                                            │
│ [    2   ]  │                                            │
│             │                                            │
│ [▶️ Start]  │                                            │
└─────────────┴────────────────────────────────────────────┘
```

**Components:**

#### Left Column - Setup Panel

```python
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
```

#### Right Column - Conversation Display

```python
with col2:
    st.subheader("Conversation")
    
    if st.session_state.running:
        # Create agents dynamically based on num_agents
        agent_configs = [
            {"name": "Sarah", "company": "HPE", "role": "Sales Engineer", 
             "objective": "Sell servers and close the deal"},
            {"name": "Yuki", "company": client, "role": "IT Procurement Manager", 
             "objective": "Get the best price and terms"},
            {"name": "Marcus", "company": client, "role": "Technical Lead", 
             "objective": "Ensure technical requirements are met"},
            {"name": "Lisa", "company": "HPE", "role": "Account Manager", 
             "objective": "Build relationship and ensure customer satisfaction"},
            {"name": "Ken", "company": client, "role": "CFO", 
             "objective": "Minimize costs and maximize ROI"}
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
        orchestrator = MultiAgentOrchestrator(agents=agents, max_turns=max_turns)
        
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            for message in orchestrator.run_streaming(initial_message=f"Let's discuss: {scenario}"):
                st.session_state.conversation.append(message)
                
                # Display all messages so far
                with message_placeholder.container():
                    for msg in st.session_state.conversation:
                        with st.chat_message("assistant" if msg['company'] == "HPE" else "user"):
                            st.markdown(f"**{msg['agent']}** ({msg['company']})")
                            st.write(msg['message'])
                
                # Show who's next with a spinner
                current_turn = len(st.session_state.conversation)
                if current_turn < max_turns * num_agents and not st.session_state.stop_requested:
                    next_agent_index = current_turn % num_agents
                    next_agent = agents[next_agent_index]
                    with status_placeholder:
                        with st.spinner(f"💭 {next_agent.name} is thinking..."):
                            pass
                
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
                st.markdown(f"**{msg['agent']}** ({msg['company']})")
                st.write(msg['message'])
    else:
        st.info("👈 Configure the scenario and click Start to begin")
```

**User Interactions:**

1. **Select Client:** Dropdown populates from `list_tenants()` function
2. **Enter Scenario:** User types description in textarea
3. **Check Participate:** Optional - adds HumanAgent to configuration
4. **Click Generate:** Triggers `suggest_agents()` call to LLM
5. **Review Agents:** Expandable cards show agent details
6. **Run/Regenerate/Cancel:** Action buttons
Choose from dropdown (Toyota, Microsoft, HPE)
2. **Enter Scenario:** Type description in textarea
3. **Set Max Turns:** Adjust slider (1-10 turns)
4. **Set Number of Agents:** Choose 2-5 agents
5. **Click Start:** Begins conversation with pre-configured agents
6. **Watch Stream:** Messages appear in real-time with loading indicators
7. **Click Stop:** Interrupts conversation mid-execution
8. **Click New:** Resets form and conversation for fresh start

**Key Features:**
- **Pre-configured Agents:** No LLM generation needed - uses hardcoded agent pool
- **Real-time Streaming:** Messages appear as they're generated
- **Visual Feedback:** Spinner shows which agent is currently thinking
- **Interrupt Control:** Stop button allows user to end conversation early
- **Multi-agent Support:** Supports 2-5 agents in round-robin conversation

---

### Removed Features

The following features from the original spec have been removed for simplicity:

- ~~Scenario Creation Wizard~~ → Direct input
- ~~Agent Suggestion/Generation via LLM~~ → Pre-configured agents
- ~~Human Participation Mode~~ → Autonomous only
- ~~Past Conversations Tab~~ → Not implemented
- ~~Sentiment Tracking~~ → Not implemented  
- ~~Metrics Dashboard~~ → Not implemented
- ~~Sidebar with detailed metrics~~ → Single column layout
- ~~Save/Load functionality~~ → Not implemented
- ~~Multiple tabs/views~~ → Single page only

---

### Screen 2: Active Conversation (Legacy - Not Implemented)

**Note:** The original multi-screen design with separate conversation view has been replaced with the single-page streaming layout described above.

---

### Screen 3: Past Conversations (Not Implemented)

**Note:** Past conversations feature removed for MVP simplicity.
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
        Chat Message Display

```python
# Display a single message in the conversation
with st.chat_message("assistant" if msg['company'] == "HPE" else "user"):
    st.markdown(f"**{msg['agent']}** ({msg['company']})")
    st.write(msg['message'])
```

#### 2. Loading Spinner with Agent Name

```python
# Show which agent is currently generating a response
with st.spinner(f"💭 {agent.name} is thinking..."):
    pass  # Placeholder that gets replaced when message arrives
```

#### 3. Status Messages

```python
# Conversation complete
st.success(f"✅ Conversation complete! {len(messages)} messages")

# Conversation stopped by user
st.warning("⏹️ Conversation stopped by user")

# Error occurred
st.error(f"Error: {error_message}"
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
            Run Autonomous Multi-Agent Conversation

```
User Action                           System Response                    UI Update
───────────────────────────────────────────────────────────────────────────────
1. Opens app                       → Load default screen              → Show setup panel + empty conversation
2. Selects client "Toyota"         → Update session state             → Dropdown shows "Toyota"
3. Types scenario description      → Update session state             → Textarea shows text
4. Adjusts max turns to 5          → Update session state             → Slider shows 5
5. Sets number of agents to 3      → Update session state             → Shows "3"
6. Clicks "▶️ Start"               → Create 3 agents from pool        → Conversation panel activates
                                   → Initialize orchestrator          → Show first message
                                   → Start streaming                  
7. (Autonomous execution)          → Agent 1 generates message        → Message appears in chat
                                   → Show "Agent 2 thinking..."       → Spinner with agent name
                                   → Agent 2 generates message        → Message appears
                                   → Show "Agent 3 thinking..."       → Spinner updates
                                   → Agent 3 generates message        → Message appears
                                   → Cycle continues                  → Chat grows in real-time
8. Conversation ends (max turns)   → Orchestrator completes           → Show "✅ Conversation complete!"
9. Clicks "🔄 New Conversation"    → Clear session state              → Reset form and conversation
```

### Flow 2: Interrupt Conversation Mid-Execution

```
User Action                           System Response                    UI Update
───────────────────────────────────────────────────────────────────────────────
1-6. (Same as Flow 1)
7. Conversation is running         → Messages streaming               → Chat updating in real-time
8. User clicks "⏹️ Stop"           → Set stop_requested flag          → Button changes to "⏹️ Stop"
9. Current message completes       → Check stop flag                  → Last message appears
                                   → Break loop                       → Show "⏹️ Conversation stopped"
                                   → Clear spinner                    
10. User reviews partial convo     → (No action)                      → Messages remain visible
11. Clicks "🔄 New Conversation"   → Clear session state              → Reset form
```

### Flow 3: Adjust Agent Count

```
User Action                           System Response                    UI Update
───────────────────────────────────────────────────────────────────────────────
1-5. (Similar to Flow 1)
6. Sets agents to 5                → Update session state             → Number input shows "5"
7. Clicks "▶️ Start"               → Create 5 agents:                 → Conversation starts
                                     - Sarah (HPE)
                                     - Yuki (Toyota)
                                     - Marcus (Toyota)
                                     - Lisa (HPE)
                                     - Ken (Toyota)
8. Round-robin with 5 agents       → Each agent takes turn            → 5-way conversation flows
                                   → Spinner shows next agent name    
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
     Agent Creation (Pre-configured)

```python
# Pre-configured agent pool (5 agents available)
agent_configs = [
    {"name": "Sarah", "company": "HPE", "role": "Sales Engineer", 
     "objective": "Sell servers and close the deal"},
    {"name": "Yuki", "company": client, "role": "IT Procurement Manager", 
     "objective": "Get the best price and terms"},
    {"name": "Marcus", "company": client, "role": "Technical Lead", 
     "objective": "Ensure technical requirements are met"},
    {"name": "Lisa", "company": "HPE", "role": "Account Manager", 
     "objective": "Build relationship and ensure customer satisfaction"},
    {"name": "Ken", "company": client, "role": "CFO", 
     "objective": "Minimize costs and maximize ROI"}
]

# Create agents based on user selection (2-5)
agents = []
for i in range(num_agents):
    config = agent_configs[i]
    agents.append(Agent(
        name=config["name"],
        company=config["company"],
        role=config["role"],
        objective=config["objective"],
        model=DEFAULT_MODEL  # mistral
    ))
```

#### Conversation Execution (Streaming)

```python
from agents.core import MultiAgentOrchestrator

# Create orchestrator
orchestrator = MultiAgentOrchestrator(agents=agents, max_turns=max_turns)

# Stream conversation with real-time UI updates
for message in orchestrator.run_streaming(initial_message=f"Let's discuss: {scenario}"):
    # message = {"turn": N, "agent": "Sarah", "company": "HPE", 
    #            "role": "Sales Engineer", "message": "...", "timestamp": "..."}
    
    st.session_state.conversation.append(message)
    
    # Update UI (Streamlit reruns automatically on state change)
    display_messages()
    show_next_agent_spinner()
    
    # Check for stop request
    if st.session_state.stop_requested:
        break
```

### 2. Removed Integrations

The following integrations from the original spec are NOT implemented:

- ~~Weaviate tenant listing~~ → Hardcoded client list
- ~~LLM agent suggestion~~ → Pre-configured agents
- ~~Sentiment analysis~~ → Not implemented
- ~~Conversation persistence~~ → Not implemented  
- ~~Past conversation retrieval~~ → Not implemented

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

26. conversation' not in st.session_state:
    st.session_state.conversation = []
if 'scenario' not in st.session_state:
    st.session_state.scenario = ""
if 'client' not in st.session_state:
    st.session_state.client = "Toyota"
if 'running' not in st.session_state:
    st.session_state.running = False
if 'stop_requested' not in st.session_state:
    st.session_state.stop_requested = False
```

### State Transitions

```
Initial State (running=False, conversation=[])
    ↓
[User clicks Start] → running=True
    ↓
[Conversation streams] → conversation grows with messages
    ↓
[User clicks Stop OR max turns reached] → running=False, stop_requested=True
    ↓
[User clicks New] → conversation=[], scenario="", running=False
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
Completed ✅)

1. ✅ Create `src/app.py` with page config
2. ✅ Add two-column layout
3. ✅ Add client dropdown (hardcoded list)
4. ✅ Add scenario textarea
5. ✅ Add max turns slider
6. ✅ Add number of agents input
7. ✅ Add Start/Stop/New buttons

#### Phase 2: Backend Integration (Completed ✅)

8. ✅ Create pre-configured agent pool (5 agents)
9. ✅ Connect Start button to create agents
10. ✅ Integrate MultiAgentOrchestrator
11. ✅ Implement streaming conversation display
12. ✅ Add real-time message updates

#### Phase 3: Visual Feedback (Completed ✅)

13. ✅ Add spinner with agent names
14. ✅ Show loading state while agent thinks
15. ✅ Display success/warning/error messages
16. ✅ Handle stop functionality

#### Phase 4: Polish (Completed ✅)

17. ✅ Add error handling for API calls
18. ✅ Improve loading states with spinners
19. ✅ Test all user flows
20. ✅ Fix bugs and edge cases

### Not Implemented (Out of Scope for MVP)

- ❌ Sentiment analysis and tracking
- ❌ Past conversations feature
- ❌ Conversation persistence to database
- ❌ LLM-powered agent suggestion
- ❌ Human participation mode
- ❌ Advanced metrics dashboard (Current Implementation)

- [x] App loads without errors
- [x] Client dropdown shows 3 options (Toyota, Microsoft, HPE)
- [x] Scenario description accepts text
- [x] Max turns slider works (1-10)
- [x] Number of agents input works (2-5)
- [x] "Start Conversation" button initiates streaming
- [x] Messages appear in real-time as agents respond
- [x] Spinner shows which agent is thinking
- [x] Stop button interrupts conversation mid-stream
- [x] Conversation ends at max turns or when stopped
- [x] "New Conversation" clears state and resets form
- [x] Error messages show for connection issues
- [x] App handles 2, 3, 4, and 5 agent conversations
- [x] Round-robin turn-taking works correctly
- [x] Messages display with agent name and company

### Features Not Tested (Not Implemented)

- [ ] ~~Sentiment chart updates~~
- [ ] ~~Past conversations tab~~
- [ ] ~~Conversation persistence~~
- [ ] ~~Human participation mode~~
- [ ] ~~Agent regeneration~~otential Phase 2 Features

1. **Agent Customization**
   - Allow users to edit agent names/roles/objectives
   - Save custom agent configurations
   - Import/export agent profiles

2. **LLM-Powered Agent Generation**
   - Use LLM to suggest agents based on scenario
   - Dynamic agent creation from natural language

3. **Human Participation Mode**
   - Enable user to join as one of the agents
   - Chat input for human responses
   - Turn management for human/AI mix

4. **Conversation Persistence**
   - Save conversations to Weaviate
   - Past conversations browser
   - Replay and analysis features

5. **Sentiment Analysis**
   - Real-time sentiment tracking per message
   - Sentiment charts over time
   - Sentiment-based insights

6. **Advanced Metrics**
   - Response time tracking
   - Token usage statistics
   - Conversation quality scores

7. **Export & Sharing**
   - PDF export with formatting
   - Markdown/JSON export
   - Share conversation links

### Current MVP Scope

**Implemented:**
- ✅ Simple 2-column layout
- ✅ Pre-configured agent pool (5 agents)
- ✅ Multi-agent support (2-5 agents)
- ✅ Real-time streaming conversation
- ✅ Visual feedback (spinners, status messages)
- ✅ Stop/interrupt functionality
- ✅ Basic error handling

**Not Implemented (Future):**
- ❌ Agent suggestion via LLM
- ❌ Human participation
- ❌ Conversation persistence
- ❌ Past conversations
- ❌ Sentiment analysis
- ❌ Advanced metric