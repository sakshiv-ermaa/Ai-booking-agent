import streamlit as st
import requests
import hashlib
import time
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="AI Booking Assistant", page_icon="🗓️")
st.title("📅 AI Appointment Scheduler")

# Session management
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()

# Display chat
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

    # If assistant message and contains Google Calendar link, show button
    if msg["role"] == "assistant":
        match = re.search(r"(https://calendar\.google\.com/calendar/event\?eid=[\w\-]+)", msg["content"])
        if match:
            st.markdown(
                f'<a href="{match.group(1)}" target="_blank">'
                f'<button style="background-color:#4285F4; color:white; border:none; padding:8px 16px; border-radius:5px; cursor:pointer;">'
                f'📅 View Event on Google Calendar</button></a>',
                unsafe_allow_html=True
            )

# User input
if prompt := st.chat_input("Example: 'Book Friday at 2pm'"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        response = requests.post(
            "https://fastapi-backend-ceps.onrender.com/chat",
            params={
                "message": prompt,
                "session_id": st.session_state.session_id
            },
            timeout=10
        ).json()

        bot_reply = response.get("response", "⚠️ System error")
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        bot_reply = "🔌 Connection error - try again"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        bot_reply = "⚠️ Unexpected error"

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    st.chat_message("assistant").write(bot_reply)

    # Button for calendar link if present
    match = re.search(r"(https://calendar\.google\.com/calendar/event\?eid=[\w\-]+)", bot_reply)
    if match:
        st.markdown(
            f'<a href="{match.group(1)}" target="_blank">'
            f'<button style="background-color:#4285F4; color:white; border:none; padding:8px 16px; border-radius:5px; cursor:pointer;">'
            f'📅 View Event on Google Calendar</button></a>',
            unsafe_allow_html=True
        )

# Debug info
if st.sidebar.checkbox("Show debug info"):
    st.sidebar.write("Session ID:", st.session_state.session_id)
    if st.sidebar.button("Reset Conversation"):
        st.session_state.clear()
        st.rerun()
