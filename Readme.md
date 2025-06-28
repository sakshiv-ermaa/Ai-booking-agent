# APPOINTMENT SCHEDULER

A smart assistant that books appointments directly into your Google Calendar using simple chat.

---

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
git clone https://github.com/YOUR_USERNAME/ai-appointment-scheduler.git
cd ai-appointment-scheduler
pip install -r requirements.txt
Set up credentials

Put your Google service account key in backend/credentials.json

Share your calendar with that email

Create .env

env
Copy
Edit
GOOGLE_CREDS_PATH=backend/credentials.json
CALENDAR_ID=your_calendar_id@group.calendar.google.com
Start the app

bash
Copy
Edit
uvicorn backend.main:app --reload
streamlit run frontend/app.py

💬 Example inputs
Book a call tomorrow at 2pm

Schedule on July 5 at 10am