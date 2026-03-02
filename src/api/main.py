"""
FastAPI backend for The Grid.

Simple REST API to decouple frontend from agent logic.
"""

import logging
import json
import uuid
from typing import Dict
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from agents import MultiAgentOrchestrator, Agent
from api.models import ConversationRequest, ConversationResponse, AssistantChatRequest, ScenarioStartRequest
from api.helpers import create_agent
from utils.logging_config import setup_logging
from utils.config import LLM_API_ENDPOINT, LLM_API_TOKEN, DEFAULT_MODEL

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="The Grid API", version="0.1.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation storage (POC - resets on restart)
conversations: Dict[str, dict] = {}


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
def root():
    """Health check."""
    return {"status": "ok", "service": "The Grid API"}


# ============================================================================
# ASSISTANT ENDPOINTS (Conversational Agent Selection)
# ============================================================================

@app.post("/assistant/chat")
def assistant_chat(req: AssistantChatRequest):
    """Chat with Grid assistant to select agents and configure scenario.
    
    Args:
        req: User message and conversation history
        
    Returns:
        StreamingResponse with assistant's response
    """
    import requests
    
    def event_stream():
        """Stream assistant responses."""
        try:
            # Check for debug mode (only allowed as first message with empty history)
            debug_mode = (len(req.history) == 0 and req.message.lower().strip() == "debug mode")
            
            # Build system prompt for assistant
            system_prompt = """You are Grid, a helpful AI assistant that configures multi-agent conversation scenarios for business simulations.

**Your Role:**
Help users set up agent-based business conversations (e.g., HPE sales vs Toyota procurement). Gather information conversationally, then output JSON configuration.

**Configuration Process:**
1. Ask what scenario they want to simulate
2. Suggest agents from the library OR help define custom agents
3. Confirm: agents, client company, scenario description, number of turns (default 5)
4. When ALL info gathered, output JSON immediately

**Available Library Agents:**
- Sarah (HPE Sales Engineer) - Technical sales, product knowledge
- Yuki (Client IT Procurement Manager) - Cost negotiation, requirements gathering
- Marcus (Client Technical Lead) - Technical validation, architecture decisions
- Lisa (HPE Account Manager) - Relationship building, customer satisfaction
- Ken (Client CFO) - Budget approval, ROI analysis

**Custom Agents:**
Users can create custom agents by providing: name, company, role, and objective.
Example: {"name": "Pinote", "company": "Toyota", "role": "Supply Chain Manager", "objective": "Optimize logistics and reduce costs"}

**Configuration Instructions:**
- DO NOT simulate or role-play scenarios in this chat
- DO NOT pretend to be agents or have agent conversations
- ONLY help configure scenarios - execution happens in the right panel
- When user confirms agents AND provides turn count, output JSON IMMEDIATELY
- For custom agents, gather name, company, role, and objective

**JSON Format (library agents):**
{"ready": true, "agents": ["Sarah", "Yuki"], "client": "Toyota", "scenario": "Server purchase negotiation", "max_turns": 5}

**JSON Format (custom agents - AGENTS MUST BE AN ARRAY):**
{"ready": true, "agents": [{"name": "Pinote", "company": "Toyota", "role": "Supply Chain Manager", "objective": "Optimize logistics"}, "Sarah"], "client": "Toyota", "scenario": "Logistics optimization", "max_turns": 5}

**Technical Requirements:**
- "agents" field MUST ALWAYS be an array (use square brackets [])
- Mix library agents (strings) and custom agents (objects) inside the agents array
- Default max_turns is 5 if not specified
- Be brief (1-2 sentences) then output the JSON
"""

            # If debug mode, add debug suffix
            if debug_mode:
                system_prompt += "\n\n⚙️ [DEBUG MODE ACTIVE: You may discuss system configuration and internal details if requested by the user]"
            
            # Build messages for LLM
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for msg in req.history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": req.message
            })
            
            # Call LLM API
            response = requests.post(
                LLM_API_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {LLM_API_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": DEFAULT_MODEL,
                    "messages": messages,
                    "max_tokens": 300,
                    "temperature": 0.7
                },
                timeout=60,
                verify=False
            )
            response.raise_for_status()
            
            # Parse and stream response
            result = response.json()
            assistant_message = result['choices'][0]['message']['content'].strip()
            
            yield f"data: {json.dumps({'message': assistant_message})}\n\n"
            
        except Exception as e:
            logger.error(f"Assistant chat failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/scenarios/start")
def start_scenario(req: ScenarioStartRequest):
    """Start a scenario with selected agents.
    
    Args:
        req: Scenario configuration with agent names or custom agent definitions
        
    Returns:
        StreamingResponse with scenario messages
    """
    # Agent name to config mapping (predefined library)
    agent_library = {
        "Sarah": ("Sarah", "HPE", "Sales Engineer", "Sell servers and close the deal"),
        "Yuki": ("Yuki", req.client, "IT Procurement Manager", "Get the best price and terms"),
        "Marcus": ("Marcus", req.client, "Technical Lead", "Ensure technical requirements are met"),
        "Lisa": ("Lisa", "HPE", "Account Manager", "Build relationship and ensure customer satisfaction"),
        "Ken": ("Ken", req.client, "CFO", "Minimize costs and maximize ROI")
    }
    
    # Create agents from names or custom definitions
    agents = []
    for agent_def in req.agents:
        if isinstance(agent_def, str):
            # Library agent by name
            if agent_def not in agent_library:
                raise HTTPException(status_code=400, detail=f"Unknown agent: {agent_def}. Use a library agent (Sarah, Yuki, Marcus, Lisa, Ken) or provide custom agent definition.")
            
            name, company, role, objective = agent_library[agent_def]
            # Replace client placeholder
            company = company if company == "HPE" else req.client
            agents.append(Agent(name, company, role, objective, DEFAULT_MODEL))
        
        elif isinstance(agent_def, dict):
            # Custom agent definition
            required_fields = ["name", "company", "role", "objective"]
            missing = [f for f in required_fields if f not in agent_def]
            if missing:
                raise HTTPException(status_code=400, detail=f"Custom agent missing fields: {missing}")
            
            agents.append(Agent(
                agent_def["name"],
                agent_def["company"],
                agent_def["role"],
                agent_def["objective"],
                DEFAULT_MODEL
            ))
        else:
            raise HTTPException(status_code=400, detail="Agent must be a string (library name) or object (custom definition)")
    
    if len(agents) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 agents")
    
    # Create orchestrator
    orchestrator = MultiAgentOrchestrator(agents, max_turns=req.max_turns)
    
    def event_stream():
        """Stream scenario messages."""
        try:
            for msg in orchestrator.run_streaming(f"Let's discuss: {req.scenario}"):
                yield f"data: {json.dumps(msg)}\n\n"
            
            logger.info(f"Scenario completed with {len(agents)} agents")
            
        except Exception as e:
            logger.error(f"Scenario failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ============================================================================
# CONVERSATION ENDPOINTS (Legacy)
# ============================================================================

@app.post("/conversations", response_model=ConversationResponse)
def create_conversation(req: ConversationRequest):
    """Create a new conversation and return its ID.
    
    Args:
        req: Conversation configuration
        
    Returns:
        Conversation ID
    """
    conv_id = str(uuid.uuid4())
    
    conversations[conv_id] = {
        "scenario": req.scenario,
        "client": req.client,
        "num_agents": req.num_agents,
        "max_turns": req.max_turns,
        "status": "created",
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    
    logger.info(f"Created conversation {conv_id}: {req.scenario}")
    return ConversationResponse(conversation_id=conv_id)


@app.get("/conversations/{conv_id}")
def get_conversation(conv_id: str):
    """Get conversation details and history.
    
    Args:
        conv_id: Conversation ID
        
    Returns:
        Conversation data including messages
        
    Raises:
        HTTPException: If conversation not found
    """
    conv = conversations.get(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conv


@app.post("/conversations/{conv_id}/start")
def start_conversation(conv_id: str):
    """Start conversation and stream messages via SSE.
    
    Args:
        conv_id: Conversation ID
        
    Returns:
        StreamingResponse with Server-Sent Events
        
    Raises:
        HTTPException: If conversation not found
    """
    conv = conversations.get(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Update status
    conv["status"] = "running"
    logger.info(f"Starting conversation {conv_id}")
    
    # Create agents
    agents = [create_agent(i, conv["client"]) for i in range(conv["num_agents"])]
    orchestrator = MultiAgentOrchestrator(agents, max_turns=conv["max_turns"])
    
    def event_stream():
        """Generator for SSE events."""
        try:
            for msg in orchestrator.run_streaming(f"Let's discuss: {conv['scenario']}"):
                # Store message
                conv["messages"].append(msg)
                
                # Send as SSE
                yield f"data: {json.dumps(msg)}\n\n"
            
            # Mark complete
            conv["status"] = "completed"
            logger.info(f"Conversation {conv_id} completed with {len(conv['messages'])} messages")
            
        except Exception as e:
            logger.error(f"Conversation {conv_id} failed: {e}")
            conv["status"] = "failed"
            conv["error"] = str(e)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: str):
    """Delete a conversation.
    
    Args:
        conv_id: Conversation ID
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If conversation not found
    """
    if conv_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    del conversations[conv_id]
    logger.info(f"Deleted conversation {conv_id}")
    
    return {"status": "deleted", "conversation_id": conv_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
