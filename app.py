# -*- coding: utf-8 -*-
from flask import Flask, request
from dotenv import load_dotenv
import os

load_dotenv()
print("DATABASE_URL =", os.getenv("DATABASE_URL"))

from models import Session, Reminder
from ai_parser import parse_message
from datetime import datetime
from twilio.twiml.messaging_response import MessagingResponse
import pytz

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():

    message = request.form.get("Body", "").strip()
    sender = request.form.get("From")

    resp = MessagingResponse()

    # LIST COMMAND
    if message.lower() == "list reminders":
        reply = list_reminders(sender)
        resp.message(reply)
        return str(resp)

    # Otherwise create reminder via OpenAI parser
    data = parse_message(message)

    if data.get("needs_clarification") or not data.get("datetime") or not data.get("task"):
        resp.message("I couldn't clearly understand the reminder. Can you rephrase?")
        return str(resp)

    task = data.get("task")
    iso_dt = data.get("datetime")

    if not iso_dt or not task:
        resp.message("I could not clearly understand the reminder. Please rephrase.")
        return str(resp)

    IST = pytz.timezone("Asia/Kolkata")

    time = datetime.fromisoformat(iso_dt)

    # Convert user input IST -> UTC before storing
    if time.tzinfo is None:
        time = IST.localize(time)

    time = time.astimezone(pytz.utc)

    session = Session()

    try:
        reminder = Reminder(
            phone=sender,
            task=task,
            reminder_time=time
        )

        session.add(reminder)
        session.commit()
    finally:
        session.close()

    display_time = time.astimezone(IST)

    reply_message = (
    "Reminder set\n\n"
    f"Task: {task}\n"
    f"Time: {display_time.strftime('%d %b %I:%M %p')}"
    )

    resp.message(reply_message)
    return str(resp)


IST = pytz.timezone("Asia/Kolkata")

def list_reminders(phone):

    session = Session()

    try:
        reminders = (
            session.query(Reminder)
            .filter(Reminder.phone == phone)
            .order_by(Reminder.reminder_time)
            .all()
        )

        if not reminders:
            return "No active reminders."

        message = "Your Reminders:\n\n"

        for r in reminders:
            time = r.reminder_time.replace(tzinfo=pytz.utc).astimezone(IST)
            message += f"{r.id}. {r.task}\n"
            message += f"   {time.strftime('%d %b %I:%M %p')}\n\n"

        return message

    finally:
        session.close()


if __name__ == "__main__":
    app.run(port=5000)