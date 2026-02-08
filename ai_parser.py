import os
import json
from datetime import datetime
import pytz
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_message(text):

    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": f"""
You extract reminder information.

Current date and time is:
{now.strftime('%Y-%m-%d %H:%M:%S')}
Timezone: IST (Asia/Kolkata)

When user says relative time like:
- after 1 min
- tomorrow
- next Monday

Convert it into absolute ISO datetime.

Return JSON:
task
datetime
"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return json.loads(response.choices[0].message.content)
