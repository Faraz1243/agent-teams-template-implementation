from typing import Optional
from fastapi import FastAPI, Body, Depends
from chatbot import orchestrator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel, Field, UUID4
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from services.services import create_thread, add_message_to_thread, get_thread_messages
from config.cloud_sql_connector import get_db
from uuid import UUID




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await orchestrator.async_init()
    yield
    # Shutdown
    await orchestrator.aclose()

app = FastAPI(
    lifespan = lifespan,
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or your Next.js domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ====================Base Models====================
class ChatRequest(BaseModel):
    message: str
    user_id: str
    thread_id: str = None


# ===================API Endpoints===================
# Root endpoint
@app.get("/", response_class = HTMLResponse)
def read_root():
    return """<h1 style="text-align:centre, foreground:teal">ChatBot API Running Smoothly :)</h1>"""

@app.post("/chat")  
async def chat(
    payload: ChatRequest,
    db = Depends(get_db)
):
    try:
        if not payload.user_id:
            return {"error": "user_id is required."}
        if not payload.message:
            return {"error": "message is required."}
  
        ans = await orchestrator.chatbot_with_memory(
            user_request=payload.message, 
            user_id=payload.user_id, 
            thread_id=payload.thread_id
        ) 

        res = {
            "thread_id": payload.thread_id,
            "message": ans.replace('\n', '<br>')
        }
        return res
    except Exception as e:
        return {"error": str(e)}

@app.get("/threads/{thread_id}")
async def get_messages(
    thread_id: str,
    db = Depends(get_db)
):
    try:
        thread_uuid = UUID(thread_id)
    except ValueError:
        return {"error": "thread_id must be a valid UUID."}

    messages = await get_thread_messages(thread_uuid, db)

    res = [
        {
            "message": msg.message,
            "sender_role": msg.sender_role,
            "timestamp": msg.created_at
        }
        for msg in messages
    ]

    return {"messages": res}
