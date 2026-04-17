import argparse
import sys
import logging

from app.service import refine_jira_story, extract_score, extract_priority
from app.jira import get_jira_ticket, add_comment, update_jira_ticket, search_jira_issues

# ------------------ Logging ------------------ #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------ Helpers ------------------ #

def safe_print_result(result):
    print("\n=== REFINED OUTPUT ===\n")
    print(result)

    score = extract_score(result)
    priority = extract_priority(result)

    print("\n--- METADATA ---")
    print(f"Score: {score}")
    print(f"Priority: {priority}")


# ------------------ Adhoc ------------------ #

def run_adhoc(args):
    try:
        logger.info(f"Running adhoc mode | Mode: {args.mode}")

        result = refine_jira_story(args.input, args.mode)
        safe_print_result(result)

    except Exception as e:
        logger.error(f"Adhoc failed: {str(e)}")
        print(f"\nError: {str(e)}")
        sys.exit(1)


# ------------------ Jira Direct ------------------ #

def run_jira_direct(args):
    try:
        logger.info(f"Running jira_direct | Issue: {args.issue}")

        raw = get_jira_ticket(args.issue)
        result = refine_jira_story(raw, args.mode)

        score = extract_score(result)
        priority = extract_priority(result)

        update_status = "no_update"

        if args.update == "comment":
            add_comment(args.issue, result)
            update_status = "comment_added"

        elif args.update == "overwrite":
            update_jira_ticket(args.issue, result)
            update_status = "description_updated"

        elif args.update == "none":
            update_status = "skipped"

        print("\n=== RESULT ===\n")
        print(f"Issue: {args.issue}")
        print(f"Score: {score}")
        print(f"Priority: {priority}")
        print(f"Update Status: {update_status}")

    except Exception as e:
        logger.error(f"Jira direct failed: {str(e)}")
        print(f"\nError processing {args.issue}: {str(e)}")
        sys.exit(1)


# ------------------ Jira Batch ------------------ #

def run_jira_batch(args):
    try:
        logger.info(f"Running jira_batch | JQL: {args.jql} | Limit: {args.limit}")

        issues = search_jira_issues(args.jql, args.limit)

        if not issues:
            print("\nNo issues found.")
            return

        scores = []
        priority_count = {"High": 0, "Medium": 0, "Low": 0}

        for issue in issues:
            key = issue.get("key")

            try:
                print(f"\nProcessing {key}...")

                summary = issue.get("summary", "")
                description = issue.get("description", "")

                raw = f"{summary}\n\n{description}"

                result = refine_jira_story(raw, args.mode)

                score = extract_score(result)
                priority = extract_priority(result)

                if score is not None:
                    scores.append(score)

                if priority in priority_count:
                    priority_count[priority] += 1

                # update behavior
                if args.update == "comment":
                    add_comment(key, result)
                    status = "comment_added"

                elif args.update == "overwrite":
                    update_jira_ticket(key, result)
                    status = "description_updated"

                elif args.update == "none":
                    status = "skipped"

                else:
                    status = "unknown"

                print(f"Score: {score} | Priority: {priority} | Status: {status}")

            except Exception as issue_error:
                logger.error(f"Error processing {key}: {str(issue_error)}")
                print(f"Failed: {key}")

        # summary
        print("\n=== SUMMARY ===")

        total = len(issues)
        avg_score = round(sum(scores)/len(scores), 2) if scores else None

        print(f"Processed: {total}")
        print(f"Average Score: {avg_score}")
        print("\nPriority Distribution:")
        for k, v in priority_count.items():
            print(f"{k}: {v}")

    except Exception as e:
        logger.error(f"Batch failed: {str(e)}")
        print(f"\nBatch Error: {str(e)}")
        sys.exit(1)


# ------------------ CLI Setup ------------------ #

parser = argparse.ArgumentParser(description="AI Jira Story Refiner CLI")

subparsers = parser.add_subparsers(dest="command")

# adhoc
adhoc = subparsers.add_parser("adhoc", help="Run on raw input text")
adhoc.add_argument("--input", required=True)
adhoc.add_argument("--mode", default="standard")

# jira direct
jira_direct = subparsers.add_parser("jira_direct", help="Run on single Jira ticket")
jira_direct.add_argument("--issue", required=True)
jira_direct.add_argument("--mode", default="standard")
jira_direct.add_argument("--update", default="comment", choices=["comment", "overwrite", "none"])

# jira batch
jira_batch = subparsers.add_parser("jira_batch", help="Run on multiple Jira tickets")
jira_batch.add_argument("--jql", required=True)
jira_batch.add_argument("--limit", type=int, default=5)
jira_batch.add_argument("--mode", default="standard")
jira_batch.add_argument("--update", default="comment", choices=["comment", "overwrite", "none"])

args = parser.parse_args()

if args.command == "adhoc":
    run_adhoc(args)
elif args.command == "jira_direct":
    run_jira_direct(args)
elif args.command == "jira_batch":
    run_jira_batch(args)
else:
    parser.print_help()
