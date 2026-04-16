# AI Jira Story Refiner

Convert messy Jira tickets into clean, developer-ready user stories using AI.

## Features
- Converts raw input into structured user stories
- Generates acceptance criteria (Gherkin format)
- Identifies edge cases and assumptions
- Highlights open questions

## Tech Stack
- Python
- FastAPI
- OpenAI API

## Setup

-bash
git clone https://github.com/yourusername/ai-jira-story-refiner.git
cd ai-jira-story-refiner
pip install -r requirements.txt

## Setup

-bash
uvicorn app.main:app --reload

Open - http://127.0.0.1:8000/docs
