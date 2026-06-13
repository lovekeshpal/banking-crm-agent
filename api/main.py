import os
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agent.graph import run_agent, agent
from agent.state import AgentState
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

app = FastAPI(title="Banking CRM Agent API")

# ─── CORS — allows Angular to talk to FastAPI ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-memory session store ──────────────────────────────────────────────────
# Stores conversation history per session
sessions: dict = {}


# ─── Request/Response Models ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "Banking CRM Agent is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Create new session if none provided
    session_id = request.session_id or str(uuid.uuid4())

    # Get or create session state
    if session_id not in sessions:
        sessions[session_id] = {
            "user_query": request.message,
            "messages": [],
            "customers": [],
            "scored_customers": [],
            "customers_with_products": [],
            "outreach_messages": [],
            "next_action": None,
            "final_response": None
        }
    else:
        # Continuing conversation — update query, reset agent state
        # but keep message history for context
        existing_messages = sessions[session_id].get("messages", [])
        sessions[session_id] = {
            "user_query": request.message,
            "messages": existing_messages,
            "customers": [],
            "scored_customers": [],
            "customers_with_products": [],
            "outreach_messages": [],
            "next_action": None,
            "final_response": None
        }

    # Run agent
    result = agent.invoke(sessions[session_id])

    # Save updated state back to session
    sessions[session_id] = result

    return ChatResponse(
        response=result["final_response"] or "I could not process that request.",
        session_id=session_id
    )


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    if session_id not in sessions:
        return {"error": "Session not found"}
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "customers_found": len(session.get("customers", [])),
        "high_value_customers": len(session.get("scored_customers", [])),
        "messages_generated": len(session.get("outreach_messages", []))
    }


@app.delete("/sessions/{session_id}")
def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "Session cleared"}