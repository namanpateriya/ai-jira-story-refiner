import json
import logging
from copy import deepcopy

from openai import OpenAI
from evaluation.evaluator import evaluate
from app.prompt import get_system_prompt
from dotenv import load_dotenv

import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------ Step 1: Collect Failures ------------------ #

def collect_failures(results):
    failures = []

    for r in results:
        if "error" in r:
            continue

        if not (r["score_pass"] and r["priority_pass"] and r["format_valid"]):
            failures.append({
                "input": r["input"],
                "score": r["score"],
                "expected_range": r["expected_range"],
                "priority": r["priority"],
                "expected_priority": r["expected_priority"],
                "format_valid": r["format_valid"]
            })

    return failures


# ------------------ Step 2: Summarize Failures ------------------ #

def summarize_failures(failures):
    summary = {
        "score_failures": 0,
        "priority_failures": 0,
        "format_failures": 0
    }

    for f in failures:
        if f["score"] is None or not (f["expected_range"][0] <= f["score"] <= f["expected_range"][1]):
            summary["score_failures"] += 1

        if f["priority"] != f["expected_priority"]:
            summary["priority_failures"] += 1

        if not f["format_valid"]:
            summary["format_failures"] += 1

    return summary


# ------------------ Step 3: Generate Improved Prompt ------------------ #

def generate_improved_prompt(base_prompt, failures, summary):
    try:
        prompt = f"""
You are an expert prompt engineer.

Your task is to improve the following system prompt based on evaluation failures.

CURRENT PROMPT:
{base_prompt}

FAILURE SUMMARY:
{summary}

FAILED CASES:
{json.dumps(failures[:5], indent=2)}

GOAL:
- Improve score accuracy
- Improve priority classification
- Ensure format consistency

RULES:
- Keep prompt structure similar
- Add only necessary constraints
- Do not overcomplicate

Return ONLY the improved prompt.
"""

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Prompt improvement failed: {str(e)}")
        return base_prompt


# ------------------ Step 4: Optimization Loop ------------------ #

def optimize_prompt(iterations=3, mode="standard"):
    current_prompt = get_system_prompt(mode)

    for i in range(iterations):
        print(f"\n=== ITERATION {i+1} ===")

        # Run evaluation
        results = evaluate()

        # Collect failures
        failures = collect_failures(results)

        if not failures:
            print("No failures. Prompt is stable.")
            break

        summary = summarize_failures(failures)

        print(f"Failures: {summary}")

        # Improve prompt
        new_prompt = generate_improved_prompt(current_prompt, failures, summary)

        if new_prompt.strip() == current_prompt.strip():
            print("No improvement detected. Stopping.")
            break

        current_prompt = new_prompt

    return current_prompt


# ------------------ Entry ------------------ #

if __name__ == "__main__":
    final_prompt = optimize_prompt(iterations=3)

    print("\n=== FINAL OPTIMIZED PROMPT ===\n")
    print(final_prompt)
