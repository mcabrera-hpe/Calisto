"""
FastAPI backend for Callisto.

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

from src.agents import MultiAgentOrchestrator
from src.api.models import ConversationRequest, ConversationResponse
from src.api.helpers import create_agent
from src.utils.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Callisto API", version="0.1.0")

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
    return {"status": "ok", "service": "Callisto API"}


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
