from apscheduler.schedulers.background import BackgroundScheduler
from models import Session, Reminder
from sender import send_whatsapp
from datetime import datetime
import pytz

def check_reminders():

    session = Session()
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.utcnow().replace(tzinfo=pytz.utc)

    reminders = session.query(Reminder).filter(
        Reminder.reminder_time <= now
    ).all()

    for r in reminders:
        send_whatsapp(r.phone, f"Reminder: {r.task}")
        print("Now:", now)
        print("Reminder:", r.reminder_time)
        session.delete(r)

    session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, "interval", seconds=10)
scheduler.start()
