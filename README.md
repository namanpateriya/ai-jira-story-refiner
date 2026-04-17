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
OPENAI_MODEL=your_model
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email
JIRA_API_TOKEN=your_token
```

For API based execution

```
uvicorn app.main:app --reload
Open Swagger UI - http://127.0.0.1:8000/docs
```

For CLI based execution
Run using the client cli.py with appropriate options

---

# 🧠 Execution Modes

---

1️⃣ **Adhoc Mode** - Run AI on raw input text. \
2️⃣ **Jira Direct Mode** - Refine a single Jira issue. \
3️⃣ **Jira Batch Mode** - Process multiple Jira issues using JQL.

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
