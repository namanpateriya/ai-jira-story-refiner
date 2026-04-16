# AI Jira Story Refiner
Convert messy Jira tickets into clean, developer-ready user stories using AI.

## Features
- Converts raw input into structured user stories
- Generates acceptance criteria (Gherkin format)
- Identifies edge cases and assumptions
- Highlights open questions
- Multiple modes - standard (default), detailed, and brutal

## Tech Stack
- Python
- FastAPI
- OpenAI API

## Setup
git clone https://github.com/yourusername/ai-jira-story-refiner.git
cd ai-jira-story-refiner
pip install -r requirements.txt

## How to Run

# Option 1 - Using APIs
uvicorn app.main:app --reload

Approach 1:
Open - http://127.0.0.1:8000/docs
POST /refine
Input:
{
  "description": "User should login but sometimes fails"
}

Approach 2: 
curl -X POST "http://127.0.0.1:8000/refine" \
-H "Content-Type: application/json" \
-d '{
  "description": "User login fails sometimes",
  "mode": "brutal"
}'

# Option 2 - From client without API calls
python cli.py --input "User login fails sometimes" --mode brutal
