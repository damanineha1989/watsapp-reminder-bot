import os
from twilio.rest import Client



def send_whatsapp(to, message):

    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )

    client.messages.create(
        from_="whatsapp:+14155238886",
        body=message,
        to=to
    )
