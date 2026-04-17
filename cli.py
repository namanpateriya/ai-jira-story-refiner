import argparse
from app.service import refine_jira_story, extract_score, extract_priority
from app.jira import get_jira_ticket, add_comment, update_jira_ticket, search_jira_issues

def run_adhoc(args):
    result = refine_jira_story(args.input, args.mode)
    print(result)

def run_jira_direct(args):
    raw = get_jira_ticket(args.issue)
    result = refine_jira_story(raw, args.mode)

    score = extract_score(result)
    priority = extract_priority(result)

    if args.update == "comment":
        add_comment(args.issue, result)
    elif args.update == "overwrite":
        update_jira_ticket(args.issue, result)

    print(f"Processed: {args.issue}")
    print(f"Score: {score} | Priority: {priority}")

def run_jira_batch(args):
    issues = search_jira_issues(args.jql, args.limit)

    scores = []

    for issue in issues:
        print(f"\nProcessing {issue['key']}...")

        raw = f"{issue['summary']}\n\n{issue['description']}"
        result = refine_jira_story(raw, args.mode)

        score = extract_score(result)
        priority = extract_priority(result)

        scores.append(score if score else 0)

        if args.update == "comment":
            add_comment(issue["key"], result)
        elif args.update == "overwrite":
            update_jira_ticket(issue["key"], result)

        print(f"Score: {score} | Priority: {priority}")

    print("\n=== SUMMARY ===")
    print(f"Processed: {len(issues)}")
    if scores:
        print(f"Average Score: {sum(scores)/len(scores):.2f}")

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest="command")

# adhoc
adhoc = subparsers.add_parser("adhoc")
adhoc.add_argument("--input", required=True)
adhoc.add_argument("--mode", default="standard")

# jira direct
jira_direct = subparsers.add_parser("jira_direct")
jira_direct.add_argument("--issue", required=True)
jira_direct.add_argument("--mode", default="standard")
jira_direct.add_argument("--update", default="comment")

# jira batch
jira_batch = subparsers.add_parser("jira_batch")
jira_batch.add_argument("--jql", required=True)
jira_batch.add_argument("--limit", type=int, default=5)
jira_batch.add_argument("--mode", default="standard")
jira_batch.add_argument("--update", default="comment")

args = parser.parse_args()

if args.command == "adhoc":
    run_adhoc(args)
elif args.command == "jira_direct":
    run_jira_direct(args)
elif args.command == "jira_batch":
    run_jira_batch(args)
else:
    parser.print_help()
