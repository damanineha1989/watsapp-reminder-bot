import os
import json
from datetime import datetime
import pytz
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an assistant that extracts reminder information from messages.

Rules:
- Identify WHEN the reminder should trigger (trigger_datetime).
- Identify WHAT the reminder is about (task).
- The trigger datetime is when the alarm should go off, NOT the event date.
- Dates mentioned as part of the task should stay inside the task text.
- Infer intent like a human.
- If the trigger datetime is missing or unclear, set it to null.
- Respond ONLY in valid JSON.
- Assume timezone Asia/Kolkata unless stated otherwise.

Output JSON schema:
{
  "trigger_datetime": "ISO-8601 or null",
  "task": "string or null",
  "confidence": number,
  "needs_clarification": boolean
}
"""

def parse_message(text: str) -> dict:
    parsed = parse_reminder(text)

    trigger_dt = parsed.get("trigger_datetime")
    task = parsed.get("task")

    needs_clarification = parsed.get("needs_clarification", False)
    confidence = parsed.get("confidence", 0)

    return {
        "datetime": trigger_dt,
        "task": task,
        "needs_clarification": needs_clarification,
        "confidence": confidence,
    }



def parse_reminder(message: str):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f'Message:\n"{message}"'
            }
        ],
        temperature=0
    )

    return json.loads(response.choices[0].message.content)

