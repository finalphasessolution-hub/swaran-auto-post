# Swaran Collections – Facebook Auto Post

Automated Facebook product posting system using GitHub Actions and Python.

## Features
- Automatic product posting to Facebook Page.
- Runs through GitHub Actions.
- Uses secure GitHub Secrets for Facebook credentials.
- Prevents duplicate product posts.
- Maintains posting history in `posted_history.json`.

## Requirements
- Python 3.12+
- Facebook Page ID
- Facebook User Access Token
- GitHub Repository

## GitHub Secrets

Add the following secrets in:

**Settings → Secrets and variables → Actions**

- `FB_USER_TOKEN`
- `FB_PAGE_ID`

## Run Workflow

1. Open the GitHub repository.
2. Go to Actions.
3. Select the Facebook auto-post workflow.
4. Click Run workflow.
5. Check the Python execution logs.

## Important

- Never share Facebook access tokens publicly.
- Keep credentials inside GitHub Secrets.
- Products should only be marked as posted after Facebook confirms successful publishing.

## Project Files

- `fb_auto_post_cloud.py` – Main automation script.
- `posted_history.json` – Previously posted product history.
- `.github/workflows/` – GitHub Actions automation.

---
**Swaran Collections – Automated Facebook Posting System**
