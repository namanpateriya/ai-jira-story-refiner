import argparse
from app.service import refine_jira_story

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, required=True)
parser.add_argument("--mode", type=str, default="standard")

args = parser.parse_args()

result = refine_jira_story(args.input, args.mode)
print("\n=== Refined Story ===\n")
print(result)
