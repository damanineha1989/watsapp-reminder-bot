from flask import Flask, request
from dotenv import load_dotenv
import os

load_dotenv()
print("DATABASE_URL =", os.getenv("DATABASE_URL"))

from models import Session, Reminder
from ai_parser import parse_message
from datetime import datetime
from twilio.twiml.messaging_response import MessagingResponse
import scheduler
import pytz




app = Flask(__name__)



@app.route("/webhook", methods=["POST"])
def webhook():

    message = request.form.get("Body").lower().strip()
    sender = request.form.get("From")

    resp = MessagingResponse()

    # ⭐ LIST COMMAND
    if message == "list reminders":
        reply = list_reminders(sender)
        resp.message(reply)
        return str(resp)

    # ⭐ Otherwise create reminder
    data = parse_message(message)

    task = data["task"]
    tz = pytz.timezone("Asia/Kolkata")

    IST = pytz.timezone("Asia/Kolkata")

    time = datetime.fromisoformat(data["datetime"])

    # Convert user input IST → UTC before storing
    if time.tzinfo is None:
        time = IST.localize(time)

    time = time.astimezone(pytz.utc)

    session = Session()

    reminder = Reminder(
        phone=sender,
        task=task,
        reminder_time=time
    )

    session.add(reminder)
    session.commit()

    IST = pytz.timezone("Asia/Kolkata")

    display_time = time.astimezone(IST)

    resp.message(
        f"✅ Reminder set\n\nTask: {task}\nTime: {display_time.strftime('%d %b %I:%M %p')}"
    )

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
            return "📭 No active reminders."

        message = "📋 Your Reminders:\n\n"

        for r in reminders:

            # ⭐ Convert to IST if timezone missing
            time = r.reminder_time
            time = r.reminder_time.replace(tzinfo=pytz.utc)
            time = time.astimezone(IST)

            message += f"{r.id}. {r.task}\n"
            message += f"   ⏰ {time.strftime('%d %b %I:%M %p')}\n\n"

        return message

    finally:
        session.close()



if __name__ == "__main__":
    app.run(port=5000)
