from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from app.service import refine_jira_story, extract_score, extract_priority
from app.jira import get_jira_ticket, add_comment, update_jira_ticket, search_jira_issues
from app.batch import run_batch

# ------------------ Logging ------------------ #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Jira Story Refiner API")


# ------------------ Models ------------------ #

class AdhocInput(BaseModel):
    input: str
    mode: str = "standard"


class JiraUpdateInput(BaseModel):
    mode: str = "standard"
    update: str = "comment"  # comment / overwrite / none


class JiraBatchInput(BaseModel):
    jql: str
    limit: int = 5
    mode: str = "standard"
    update: str = "comment"


# ------------------ Health ------------------ #

@app.get("/")
def health():
    return {"status": "running"}


# ------------------ 1. ADHOC ------------------ #

@app.post("/adhoc")
def adhoc(input: AdhocInput):
    try:
        logger.info(f"API Adhoc | Mode: {input.mode}")

        result = refine_jira_story(input.input, input.mode)

        return {
            "refined_story": result,
            "score": extract_score(result),
            "priority": extract_priority(result)
        }

    except Exception as e:
        logger.error(f"Adhoc API error: {str(e)}")
        raise HTTPException(status_code=500, detail="Adhoc processing failed")


# ------------------ 2. JIRA DIRECT ------------------ #

@app.post("/jira/{issue_key}")
def jira_direct(issue_key: str, input: JiraUpdateInput):
    try:
        logger.info(f"API Jira Direct | Issue: {issue_key}")

        raw = get_jira_ticket(issue_key)
        refined = refine_jira_story(raw, input.mode)

        score = extract_score(refined)
        priority = extract_priority(refined)

        if input.update == "comment":
            add_comment(issue_key, refined)
            status = "comment_added"

        elif input.update == "overwrite":
            update_jira_ticket(issue_key, refined)
            status = "description_updated"

        else:
            status = "no_update"

        return {
            "issue_key": issue_key,
            "score": score,
            "priority": priority,
            "update_status": status,
            "refined_story": refined
        }

    except Exception as e:
        logger.error(f"Jira Direct API error: {str(e)}")
        raise HTTPException(status_code=500, detail="Jira processing failed")


# ------------------ 3. JIRA BATCH ------------------ #

@app.post("/jira/batch")
def jira_batch(input: JiraBatchInput):
    try:
        logger.info(f"API Jira Batch | JQL: {input.jql}")

        result = run_batch(
            jql=input.jql,
            mode=input.mode,
            limit=input.limit,
            update=input.update
        )

        return result

    except Exception as e:
        logger.error(f"Jira Batch API error: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch processing failed")
