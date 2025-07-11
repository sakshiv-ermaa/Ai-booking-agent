# APPOINTMENT SCHEDULER

A smart assistant that books appointments directly into your Google Calendar using simple chat.

---
working link : https://ai-booking-agentl.streamlit.app/

## WHAT IT DOES

- Chat with the bot to book meetings
- Skips weekends and busy slots
- Suggests next best time if needed
- Adds the event to Google Calendar
- Gives you a direct link to view it

---

##  How to run

1. Clone & Install

```bash
git clone https://github.com/sakshiv-ermaa/TailorTalk_assignment.git
cd TailorTalk
pip install -r requirements.txt

uvicorn backend.main:app --reload
install streamlit
streamlit run frontend/app.py

💬 Example inputs
Book a call tomorrow at 2pm

Schedule on July 5 at 10am
