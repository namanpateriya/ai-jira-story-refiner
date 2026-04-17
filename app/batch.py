from app.jira import search_jira_issues, add_comment
from app.service import refine_jira_story


def run_batch(jql: str, mode: str = "standard", limit: int = 5):
    issues = search_jira_issues(jql, limit)

    results = []

    for issue in issues:
        print(f"Processing {issue['key']}...")

        raw_text = f"{issue['summary']}\n\n{issue['description']}"
        refined = refine_jira_story(raw_text, mode)

        # safer → comment instead of overwrite
        add_comment(issue["key"], refined)

        results.append({
            "key": issue["key"],
            "score": extract_score(refined),  # simple parsing
            "status": "processed"
        })

    return results
