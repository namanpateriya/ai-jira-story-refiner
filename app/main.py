from fastapi import FastAPI
from pydantic import BaseModel
from app.service import refine_jira_story
from app.jira import get_jira_ticket, update_jira_ticket

app = FastAPI(title="AI Jira Story Refiner")

class JiraInput(BaseModel):
    description: str
    mode: str = "standard"

@app.post("/refine")
def refine(input: JiraInput):
    result = refine_jira_story(input.description, input.mode)
    return {"refined_story": result}

@app.get("/")
def health():
    return {"status": "running"}

@app.post("/refine-jira/{issue_key}")
def refine_jira(issue_key: str, mode: str = "standard"):
    
    raw_text = get_jira_ticket(issue_key)
    
    refined = refine_jira_story(raw_text, mode)

    update_jira_ticket(issue_key, refined)

    return {
        "issue_key": issue_key,
        "refined_story": refined
    }
