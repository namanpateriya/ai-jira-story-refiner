from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from app.service import refine_jira_story, extract_score, extract_priority
from app.jira import get_jira_ticket, add_comment, update_jira_ticket

# ------------------ Logging ------------------ #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ App ------------------ #
app = FastAPI(title="AI Jira Story Refiner")

# ------------------ Models ------------------ #
class JiraInput(BaseModel):
    description: str
    mode: str = "standard"

class JiraUpdateInput(BaseModel):
    mode: str = "standard"
    update: str = "comment"  # comment / overwrite / none

# ------------------ Routes ------------------ #

@app.get("/")
def health():
    return {"status": "running"}


@app.post("/refine")
def refine(input: JiraInput):
    try:
        logger.info(f"Adhoc refinement started | Mode: {input.mode}")

        result = refine_jira_story(input.description, input.mode)

        score = extract_score(result)
        priority = extract_priority(result)

        logger.info("Adhoc refinement completed")

        return {
            "refined_story": result,
            "score": score,
            "priority": priority
        }

    except Exception as e:
        logger.error(f"Error in /refine: {str(e)}")
        raise HTTPException(status_code=500, detail="Refinement failed")


@app.post("/jira/{issue_key}")
def refine_jira(issue_key: str, input: JiraUpdateInput):
    try:
        logger.info(f"Jira refinement started | Issue: {issue_key} | Mode: {input.mode}")

        raw_text = get_jira_ticket(issue_key)

        if not raw_text:
            raise Exception("Empty Jira ticket content")

        refined = refine_jira_story(raw_text, input.mode)

        score = extract_score(refined)
        priority = extract_priority(refined)

        # Update behavior
        if input.update == "comment":
            add_comment(issue_key, refined)
            update_status = "comment_added"

        elif input.update == "overwrite":
            update_jira_ticket(issue_key, refined)
            update_status = "description_updated"

        else:
            update_status = "no_update"

        logger.info(f"Jira refinement completed | Issue: {issue_key}")

        return {
            "issue_key": issue_key,
            "score": score,
            "priority": priority,
            "update_status": update_status,
            "refined_story": refined
        }

    except Exception as e:
        logger.error(f"Error in /jira/{issue_key}: {str(e)}")
        raise HTTPException(status_code=500, detail="Jira refinement failed")
