import json
import logging
from statistics import mean

from app.service import refine_jira_story, extract_score, extract_priority
from openai import OpenAI
from dotenv import load_dotenv

import os

load_dotenv()

# ------------------ Logging ------------------ #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ OpenAI Client ------------------ #
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------ Config ------------------ #

REQUIRED_SECTIONS = [
    "User Story",
    "Acceptance Criteria",
    "Edge Cases",
    "Assumptions",
    "Open Questions",
    "Ticket Quality Score",
    "Priority Suggestion"
]


# ------------------ Validators ------------------ #

def check_format(output: str):
    return all(section in output for section in REQUIRED_SECTIONS)


def check_length(output: str):
    return 200 <= len(output) <= 2000


def check_completeness(output: str):
    filled_sections = sum(1 for section in REQUIRED_SECTIONS if section in output)
    return filled_sections / len(REQUIRED_SECTIONS)


# ------------------ LLM Judge ------------------ #

def judge_output(output: str):
    try:
        prompt = f"""
You are an expert evaluator of product requirement outputs.

Evaluate the following output on:
1. Clarity (0-10)
2. Completeness (0-10)
3. Usefulness for developers (0-10)

Return STRICT JSON:
{{
  "clarity": number,
  "completeness": number,
  "usefulness": number
}}

OUTPUT:
{output}
"""

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content

        return json.loads(content)

    except Exception as e:
        logger.warning(f"LLM judge failed: {str(e)}")
        return {
            "clarity": None,
            "completeness": None,
            "usefulness": None
        }


# ------------------ Evaluation ------------------ #

def evaluate():
    with open("evaluation/test_cases.json") as f:
        test_cases = json.load(f)

    results = []

    for case in test_cases:
        input_text = case["input"]
        expected_range = case["expected_score_range"]
        expected_priority = case["expected_priority"]

        print(f"\nEvaluating: {input_text}")

        try:
            output = refine_jira_story(input_text, mode="standard")

            score = extract_score(output)
            priority = extract_priority(output)

            # -------- Basic Metrics -------- #
            score_pass = (
                score is not None and
                expected_range[0] <= score <= expected_range[1]
            )

            priority_pass = (priority == expected_priority)

            # -------- Advanced Metrics -------- #
            format_valid = check_format(output)
            length_valid = check_length(output)
            completeness_score = check_completeness(output)

            # -------- LLM Judge -------- #
            judge_scores = judge_output(output)

            result = {
                "input": input_text,
                "score": score,
                "expected_range": expected_range,
                "score_pass": score_pass,
                "priority": priority,
                "expected_priority": expected_priority,
                "priority_pass": priority_pass,
                "format_valid": format_valid,
                "length_valid": length_valid,
                "completeness_score": round(completeness_score, 2),
                "judge_clarity": judge_scores["clarity"],
                "judge_completeness": judge_scores["completeness"],
                "judge_usefulness": judge_scores["usefulness"]
            }

            results.append(result)

            # -------- Print Per Case -------- #
            print(f"Score: {score} | Pass: {score_pass}")
            print(f"Priority: {priority} | Pass: {priority_pass}")
            print(f"Format Valid: {format_valid}")
            print(f"Completeness: {completeness_score:.2f}")

        except Exception as e:
            logger.error(f"Evaluation failed for input: {input_text}")
            results.append({
                "input": input_text,
                "error": str(e)
            })

    return results


# ------------------ Summary ------------------ #

def summarize(results):
    valid_results = [r for r in results if "error" not in r]

    total = len(valid_results)

    score_accuracy = sum(r["score_pass"] for r in valid_results) / total
    priority_accuracy = sum(r["priority_pass"] for r in valid_results) / total
    format_accuracy = sum(r["format_valid"] for r in valid_results) / total

    avg_completeness = mean(r["completeness_score"] for r in valid_results)

    avg_clarity = mean([r["judge_clarity"] for r in valid_results if r["judge_clarity"]])
    avg_usefulness = mean([r["judge_usefulness"] for r in valid_results if r["judge_usefulness"]])

    print("\n=== FINAL SUMMARY ===\n")
    print(f"Total Cases: {total}")
    print(f"Score Accuracy: {score_accuracy:.2%}")
    print(f"Priority Accuracy: {priority_accuracy:.2%}")
    print(f"Format Accuracy: {format_accuracy:.2%}")
    print(f"Avg Completeness: {avg_completeness:.2f}")
    print(f"Avg Clarity (LLM): {avg_clarity:.2f}")
    print(f"Avg Usefulness (LLM): {avg_usefulness:.2f}")


# ------------------ Entry ------------------ #

if __name__ == "__main__":
    results = evaluate()
    summarize(results)
