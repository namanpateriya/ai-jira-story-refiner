import os
import requests
import logging
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv()

# ------------------ Logging ------------------ #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ Config ------------------ #
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    raise Exception("Missing Jira configuration")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ------------------ Helpers ------------------ #

def extract_description_text(description):
    """
    Converts Jira ADF (or plain text) into readable text.
    """
    if not description:
        return ""

    # If already string → return directly
    if isinstance(description, str):
        return description

    # Handle ADF JSON
    if isinstance(description, dict):
        try:
            texts = []

            def parse_content(content):
                for block in content:
                    if "content" in block:
                        parse_content(block["content"])
                    if block.get("type") == "text":
                        texts.append(block.get("text", ""))

            parse_content(description.get("content", []))

            return " ".join(texts).strip()

        except Exception as e:
            logger.warning(f"ADF parsing failed, fallback to string: {str(e)}")
            return str(description)

    return str(description)
    
def get_jira_ticket(issue_key: str):
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

        logger.info(f"Fetching Jira ticket: {issue_key}")

        response = requests.get(url, headers=headers, auth=auth, timeout=10)

        if response.status_code != 200:
            logger.error(f"Failed to fetch ticket {issue_key} | Status: {response.status_code}")
            raise Exception("Jira fetch failed")

        data = response.json()

        summary = data["fields"].get("summary", "")
        description_raw = data["fields"].get("description", "")
        description = extract_description_text(description_raw)

        return f"{summary}\n\n{description}"

    except Exception as e:
        logger.error(f"Error fetching Jira ticket {issue_key}: {str(e)}")
        raise


def update_jira_ticket(issue_key: str, refined_text: str):
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": text}
                        ]
                    }
                ]
            }
        }

        logger.info(f"Updating Jira ticket: {issue_key}")

        response = requests.put(url, json=payload, headers=headers, auth=auth, timeout=10)

        if response.status_code not in [200, 204]:
            logger.error(f"Failed to update ticket {issue_key} | Status: {response.status_code}")
            raise Exception("Jira update failed")

        return True

    except Exception as e:
        logger.error(f"Error updating Jira ticket {issue_key}: {str(e)}")
        raise


def add_comment(issue_key: str, text: str):
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"

        payload = {
            "body": text
        }

        logger.info(f"Adding comment to Jira ticket: {issue_key}")

        response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=10)

        if response.status_code not in [200, 201]:
            logger.error(f"Failed to comment on {issue_key} | Status: {response.status_code}")
            raise Exception("Jira comment failed")

        return True

    except Exception as e:
        logger.error(f"Error adding comment to {issue_key}: {str(e)}")
        raise


def search_jira_issues(jql: str, max_results: int = 10):
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/search"

        params = {
            "jql": jql,
            "maxResults": max_results
        }

        logger.info(f"Searching Jira issues | JQL: {jql} | Limit: {max_results}")

        response = requests.get(url, headers=headers, auth=auth, params=params, timeout=10)

        if response.status_code != 200:
            logger.error(f"Jira search failed | Status: {response.status_code}")
            raise Exception("Jira search failed")

        data = response.json()

        issues = []
        for issue in data.get("issues", []):
            issues.append({
                "key": issue["key"],
                "summary": issue["fields"].get("summary", ""),
                "description": extract_description_text(issue["fields"].get("description", ""))
            })

        logger.info(f"Found {len(issues)} issues")

        return issues

    except Exception as e:
        logger.error(f"Error searching Jira issues: {str(e)}")
        raise

def build_issue_text(issue: dict) -> str:
    """
    Standard way to convert Jira issue into LLM input text.
    """
    summary = issue.get("summary", "")
    description = issue.get("description", "")

    return f"{summary}\n\n{description}".strip()
