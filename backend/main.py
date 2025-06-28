from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .agents import run_conversation, ConversationState
from .db import SessionLocal, init_db, Conversation
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
async def chat(
    message: str = Query(...),
    session_id: str = Query("default"),
    db: Session = Depends(get_db)
):
    try:
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        convo = db.query(Conversation).filter(Conversation.session_id == session_id).first()
        if not convo:
            convo = Conversation(session_id=session_id)
            db.add(convo)
            db.commit()
            db.refresh(convo)

        # Prepare conversation state
        state: ConversationState = {
            "user_input": message,
            "intent": convo.intent or "",
            "date": convo.date or "",
            "time": convo.time or "",
            "response": "",  # Clear previous response
            "suggested_time": convo.suggested_time or "",
            "awaiting_confirmation": convo.awaiting_confirmation or False,
            "greeted": convo.greeted or False
        }

        # Process user message
        response, new_state = run_conversation(state)
        logger.info(f"State updated: {new_state}")

        # Save updated state back to DB
        for key, value in new_state.items():
            if hasattr(convo, key):
                setattr(convo, key, value)

        db.commit()
        return {"response": response}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
