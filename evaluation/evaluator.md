# Evaluator Guide — AI Jira Story Refiner

This module helps you **measure, validate, and improve** the quality of AI-generated Jira stories.

Instead of guessing whether outputs are “good,” the evaluator provides:

* Objective metrics (score + priority accuracy)
* Structural validation (format, completeness)
* LLM-based qualitative scoring (clarity, usefulness)

---

# What This Evaluator Does

### Evaluates across 3 layers

#### 1. Basic Metrics

* Score Accuracy (within expected range)
* Priority Accuracy

#### 2. Advanced Metrics

* Format validation (all sections present)
* Output length sanity
* Completeness score (section coverage)

#### 3. LLM-as-Judge

* Clarity (0–10)
* Completeness (0–10)
* Developer usefulness (0–10)

---

# Setup

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 2. Set Environment Variables

Create a `.env` file:

```bash
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
```

---

## 3. Add Evaluation Dataset

Ensure file exists:

```bash
evaluation/test_cases.json
```

### Example:

```json
[
  {
    "input": "User login fails sometimes",
    "expected_score_range": [3, 6],
    "expected_priority": "High"
  }
]
```

---

# How to Run

```bash
python -m app.evaluator
```

---

# Sample Output (Per Test Case)

```text
Evaluating: User login fails sometimes

Score: 4 | Pass: True
Priority: High | Pass: True
Format Valid: True
Completeness: 0.86
```

---

# Structured Result Example

Each case produces structured output internally:

```json
{
  "input": "User login fails sometimes",
  "score": 4,
  "expected_range": [3, 6],
  "score_pass": true,
  "priority": "High",
  "expected_priority": "High",
  "priority_pass": true,
  "format_valid": true,
  "length_valid": true,
  "completeness_score": 0.86,
  "judge_clarity": 8,
  "judge_completeness": 7,
  "judge_usefulness": 8
}
```

---

# Final Evaluation Summary

At the end of execution:

```text
=== FINAL SUMMARY ===

Total Cases: 20
Score Accuracy: 75.00%
Priority Accuracy: 85.00%
Format Accuracy: 95.00%
Avg Completeness: 0.88
Avg Clarity (LLM): 7.80
Avg Usefulness (LLM): 7.50
```

---

# How to Interpret Results

### Score Accuracy

* Measures how close your scoring logic is to expected ranges
* Low value → prompt needs calibration

### Priority Accuracy

* Measures correctness of prioritization logic
* Low value → unclear urgency mapping

### Format Accuracy

* Ensures output structure consistency
* <100% → prompt enforcement issue

### Completeness Score

* % of required sections present
* Helps detect missing logic or skipped sections

### LLM Judge Scores

* Clarity → readability and structure
* Completeness → coverage of requirements
* Usefulness → practical value for developers

---

# Recommended Workflow

```text
Run evaluator → Analyze failures → Improve prompt → Repeat
```

Focus on:

* Low score accuracy → adjust scoring rules
* Missing sections → tighten prompt constraints
* Low usefulness → improve acceptance criteria depth

---
