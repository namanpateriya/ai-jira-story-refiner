from fastapi import FastAPI
from pydantic import BaseModel
from app.service import refine_jira_story

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
