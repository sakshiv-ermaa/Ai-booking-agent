# agents.py
from langgraph.graph import StateGraph, END
from typing import TypedDict
from datetime import datetime, timedelta
from .utils import extract_multiple_datetimes, is_weekend, format_nice, get_next_weekday
from .calendar_service import is_slot_available, book_event, suggest_next_available
import logging

logger = logging.getLogger(__name__)

class ConversationState(TypedDict):
    user_input: str
    intent: str
    date: str
    time: str
    response: str
    suggested_time: str
    awaiting_confirmation: bool
    greeted: bool

def parse_intent(state: ConversationState) -> ConversationState:
    message = state["user_input"].strip().lower()

    greeting_words = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(greet in message for greet in greeting_words) and not state.get("greeted"):
        state.update({
            "greeted": True,
            "intent": "greeting",
            "awaiting_confirmation": False,
            "response": "👋 Hi there! I can help you schedule meetings. Try something like 'Book a call tomorrow at 3pm'."
        })
        return state

    if not state.get("greeted"):
        state.update({
            "greeted": True,
            "intent": "",
            "awaiting_confirmation": False,
            "response": "👋 Hi! I can help schedule meetings. Example: 'Book Friday at 2pm'"
        })
        return state

    # Confirmation logic
    if state.get("awaiting_confirmation"):
        if any(word in message for word in ["yes", "sure", "confirm", "book"]):
            try:
                dt = datetime.strptime(state["suggested_time"], "%Y-%m-%d %H:%M")
                confirmation = book_event(dt)
                state.update({
                    "response": confirmation,
                    "awaiting_confirmation": False,
                    "date": "",
                    "time": ""
                })
            except Exception as e:
                state["response"] = f"⚠️ Error: {str(e)}"
        elif any(word in message for word in ["no", "cancel"]):
            state.update({
                "response": "No problem! What time would work better?",
                "awaiting_confirmation": False
            })
        else:
            state["response"] = "Please confirm: Should I book this? (yes/no)"
        return state

    booking_triggers = ["book", "schedule", "meeting", "appointment", "call", "set up"]
    time_phrases = ["at", "around", "by", "before", "after", "pm", "am", ":"]
    date_phrases = ["today", "tomorrow"] + [d.lower() for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]

    has_booking = any(trigger in message for trigger in booking_triggers)
    has_time = any(phrase in message for phrase in time_phrases)
    has_date = any(phrase in message for phrase in date_phrases) or any(word in message for word in ["next week", "this week"])

    state["intent"] = "booking" if (has_booking or (has_time and has_date)) else "unknown"
    return state

def extract_parts(state: ConversationState) -> ConversationState:
    if state.get("intent") != "booking":
        return state

    matches = extract_multiple_datetimes(state["user_input"])
    logger.info(f"Extracted datetime matches: {matches}")

    if matches:
        dt, _ = matches[0]  # pick the first match
        state["date"] = dt.date().isoformat()
        state["time"] = dt.strftime("%H:%M")

    return state

def respond(state: ConversationState) -> ConversationState:
    if state.get("response"):
        return state

    if state.get("intent") == "unknown":
        state["response"] = "I can help schedule a meeting. Try saying: 'Book Friday at 2pm'"
        return state

    if not state.get("date"):
        state["response"] = "📅 What day should I book it for? (e.g. 'Friday' or 'July 5th')"
        return state

    if not state.get("time"):
        state["response"] = "⏰ What time should I book it for? (e.g. '2pm')"
        return state

    try:
        dt = datetime.strptime(f"{state['date']} {state['time']}", "%Y-%m-%d %H:%M")

        original_dt = dt
        if is_weekend(dt.date()):
            dt = get_next_weekday(dt)

        if original_dt != dt:
            state["response"] = f"⚠️ Weekends are unavailable. I’ve shifted it to the next working day: {format_nice(dt)}. Should I book it? (yes/no)"
            state.update({
                "suggested_time": dt.strftime("%Y-%m-%d %H:%M"),
                "awaiting_confirmation": True
            })
            return state

        if is_slot_available(dt):
            state.update({
                "suggested_time": dt.strftime("%Y-%m-%d %H:%M"),
                "awaiting_confirmation": True,
                "response": f"✅ That time is free! Should I book it for {format_nice(dt)}? (yes/no)"
            })
        else:
            next_slot = suggest_next_available(dt)
            state.update({
                "suggested_time": next_slot.strftime("%Y-%m-%d %H:%M"),
                "awaiting_confirmation": True,
                "response": f"⛔ That time is already booked. How about {format_nice(next_slot)}? (yes/no)"
            })
    except Exception as e:
        logger.error(f"Datetime conversion failed: {e}")
        state["response"] = "⚠️ I couldn't understand the time. Try again with something like '3pm tomorrow'."

    return state

def run_conversation(state: ConversationState) -> tuple[str, ConversationState]:
    try:
        builder = StateGraph(ConversationState)
        builder.add_node("parse_intent", parse_intent)
        builder.add_node("extract_parts", extract_parts)
        builder.add_node("respond", respond)

        builder.set_entry_point("parse_intent")
        builder.add_edge("parse_intent", "extract_parts")
        builder.add_edge("extract_parts", "respond")
        builder.add_edge("respond", END)

        graph = builder.compile()
        final_state = graph.invoke(state)

        return final_state["response"], final_state
    except Exception as e:
        logger.error(f"Conversation error: {e}")
        return "⚠️ System error - please try again", state
