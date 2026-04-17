import os
import requests
from requests.auth import HTTPBasicAuth

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def get_jira_ticket(issue_key: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

    response = requests.get(url, headers=headers, auth=auth)
    data = response.json()

    description = data["fields"].get("description", "")
    summary = data["fields"].get("summary", "")

    return f"{summary}\n\n{description}"


def update_jira_ticket(issue_key: str, refined_text: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

    payload = {
        "fields": {
            "description": refined_text
        }
    }

    response = requests.put(url, json=payload, headers=headers, auth=auth)
    return response.status_code

def search_jira_issues(jql: str, max_results: int = 10):
    url = f"{JIRA_BASE_URL}/rest/api/3/search"

    params = {
        "jql": jql,
        "maxResults": max_results
    }

    response = requests.get(url, headers=headers, auth=auth, params=params)
    data = response.json()

    issues = []
    for issue in data["issues"]:
        issues.append({
            "key": issue["key"],
            "summary": issue["fields"]["summary"],
            "description": issue["fields"].get("description", "")
        })

    return issues
