import os
from openai import OpenAI
from app.prompt import SYSTEM_PROMPT

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def refine_jira_story(raw_input: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_input}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
