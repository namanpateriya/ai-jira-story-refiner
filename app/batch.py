import logging
import time

from app.jira import search_jira_issues, add_comment, update_jira_ticket, extract_description_text, build_issue_text
from app.service import refine_jira_story, extract_score, extract_priority

# ------------------ Logging ------------------ #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ Batch Processor ------------------ #

def run_batch(jql: str, mode: str = "standard", limit: int = 5, update: str = "comment"):
    try:
        logger.info(f"Batch started | JQL: {jql} | Limit: {limit} | Mode: {mode}")

        issues = search_jira_issues(jql, limit)

        if not issues:
            logger.warning("No issues found for given JQL")
            return {
                "processed": 0,
                "message": "No issues found"
            }

        results = []
        scores = []
        priority_count = {"High": 0, "Medium": 0, "Low": 0}

        for issue in issues:
            try:
                key = issue["key"]
                logger.info(f"Processing issue: {key}")

                description = extract_description_text(issue["description"])
                raw_text = build_issue_text(issue)
                refined = refine_jira_story(raw_text, mode)

                score = extract_score(refined)
                priority = extract_priority(refined)

                if score is not None:
                    scores.append(score)

                if priority in priority_count:
                    priority_count[priority] += 1

                # Update behavior
                if update == "comment":
                    add_comment(key, refined)
                    status = "comment_added"

                elif update == "overwrite":
                    update_jira_ticket(key, refined)
                    status = "description_updated"

                else:
                    status = "no_update"

                results.append({
                    "key": key,
                    "score": score,
                    "priority": priority,
                    "status": status
                })

                logger.info(f"Completed issue: {key} | Score: {score} | Priority: {priority}")

                time.sleep(1)  # avoid rate limits

            except Exception as issue_error:
                logger.error(f"Error processing issue {issue['key']}: {str(issue_error)}")
                results.append({
                    "key": issue["key"],
                    "status": "failed"
                })

        summary = {
            "processed": len(results),
            "average_score": round(sum(scores)/len(scores), 2) if scores else None,
            "priority_distribution": priority_count
        }

        logger.info(f"Batch completed | Processed: {len(results)}")

        return {
            "results": results,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Batch failed: {str(e)}")
        raise
