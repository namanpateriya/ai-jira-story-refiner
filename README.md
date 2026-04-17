# AI Jira Story Refiner

Convert messy inputs or Jira tickets into structured, developer-ready user stories using AI.

Supports:

* Adhoc JSON input
* Direct Jira ticket refinement
* Batch Jira backlog processing

---

## 🚀 Features

* User story generation
* Gherkin acceptance criteria
* Edge cases & assumptions
* Ticket quality scoring (0–10)
* Priority suggestion (Low / Medium / High)
* Batch backlog processing
* Jira integration (read + comment)

---

## ⚙️ Setup

```bash
git clone https://github.com/yourusername/ai-jira-story-refiner.git
cd ai-jira-story-refiner
pip install -r requirements.txt
```

Create `.env` file:

```
OPENAI_API_KEY=your_key
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email
JIRA_API_TOKEN=your_token
```

---

# 🧠 Execution Modes

---

## 1️⃣ Adhoc Mode (JSON Input)

Run AI on raw input text.

### Command

```bash
python cli.py adhoc \
--input "User login fails sometimes. Needs validation." \
--mode brutal
```

### Output

```
User Story:
As a user, I want to log in securely...

Acceptance Criteria:
- Given valid credentials...
- When user logs in...
- Then access is granted

Edge Cases:
- Invalid password attempts
- Network failure

Assumptions:
- User is registered

Open Questions:
- Should MFA be mandatory?

Ticket Quality Score: 4/10
Reason: Vague requirements, missing edge cases

Priority Suggestion: High
```

---

## 2️⃣ Jira Direct Mode

Refine a single Jira issue.

### Command

```bash
python cli.py jira_direct \
--issue PROJ-123 \
--mode standard \
--update comment
```

### Behavior

* Fetches Jira ticket
* Runs refinement
* Adds result as comment (default)

### Output

```
Processed: PROJ-123
Score: 5
Priority: Medium
Status: Comment Added
```

---

## 3️⃣ Jira Batch Mode (🔥 Powerful)

Process multiple Jira issues using JQL.

### Command

```bash
python cli.py jira_batch \
--jql "project = PROJ AND status = 'To Do'" \
--limit 5 \
--mode brutal \
--update comment
```

### Output

```
Processing PROJ-101...
Score: 3 | Priority: High

Processing PROJ-102...
Score: 7 | Priority: Medium

=== SUMMARY ===
Processed: 5 issues
Average Score: 4.8
High Priority: 3
```

---

# 🔧 CLI Options

| Flag       | Description                  |
| ---------- | ---------------------------- |
| `--input`  | Raw input text (adhoc)       |
| `--issue`  | Jira issue key               |
| `--jql`    | Jira query                   |
| `--limit`  | Max issues to process        |
| `--mode`   | standard / detailed / brutal |
| `--update` | comment / overwrite / none   |

---

# ⚠️ Safety Modes

* `comment` → Recommended (non-destructive)
* `overwrite` → Updates description
* `none` → Dry run

---

# 📊 Use Cases

* Improve backlog quality
* Prepare sprint-ready tickets
* Audit Jira hygiene
* Automate PM workflows

---

# 🚀 Roadmap

* Duplicate detection
* Ticket clustering
* Sprint readiness scoring
* Chrome extension

---

Built for speed, clarity, and real-world use 🚀
