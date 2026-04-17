import os
import logging
import re
from openai import OpenAI
from app.prompt import get_system_prompt
from dotenv import load_dotenv
load_dotenv()


# ------------------ Logging ------------------ #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ Client ------------------ #
if not os.getenv("OPENAI_API_KEY"):
    raise Exception("Missing OPENAI_API_KEY")
    
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------ Helper Function ------------------ #
def ensure_required_fields(text: str) -> str:
    if "Ticket Quality Score:" not in text:
        text += "\n\nTicket Quality Score: 5/10"
    
    if "Priority Suggestion:" not in text:
        text += "\nPriority Suggestion: Medium"

    return text
    
# ------------------ Core Function ------------------ #

def refine_jira_story(raw_input: str, mode: str = "standard") -> str:
    try:
        if not raw_input:
            raise ValueError("Empty input provided")

        logger.info(f"Refinement started | Mode: {mode}")

        system_prompt = get_system_prompt(mode)

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_input}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content

        if not result:
            raise Exception("Empty response from LLM")

        # enforce required fields
        result = ensure_required_fields(result)

        logger.info("Refinement completed successfully")

        return result

    except Exception as e:
        logger.error(f"Error in refine_jira_story: {str(e)}")
        raise


# ------------------ Extraction Utilities ------------------ #

def extract_score(text: str):
    try:
        match = re.search(r"Ticket Quality Score:\s*(\d+)", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        logger.error(f"Error extracting score: {str(e)}")
        return None


def extract_priority(text: str):
    try:
        match = re.search(r"Priority Suggestion:\s*(Low|Medium|High)", text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        logger.error(f"Error extracting priority: {str(e)}")
        return None
