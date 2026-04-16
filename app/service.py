import os
from openai import OpenAI
from app.prompt import get_system_prompt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def refine_jira_story(raw_input: str, mode: str = "standard") -> str:
    system_prompt = get_system_prompt(mode)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_input}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
