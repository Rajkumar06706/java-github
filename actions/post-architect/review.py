import os
import requests
import json
import time

from pathlib import Path
github_token = os.environ["GITHUB_TOKEN"] 
api_key = os.environ["GEMINI_API_KEY"]
ACTION_PATH = Path(os.environ["ACTION_PATH"])

with open("pr.diff", "r", encoding="utf-8") as f:
    diff = f.read()

with open(ACTION_PATH / "standards.md", encoding="utf-8") as f:
    standards = f.read()

prompt = f"""
{standards}

Pull Request Diff:

{diff[:15000]}
"""

url = (
"https://generativelanguage.googleapis.com/v1beta/"
f"models/gemini-2.5-flash:generateContent?key={api_key}"
)

payload = {
"contents": [
{
"parts": [
{
"text": prompt
}
]
}
]
}

for attempt in range(3):
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        break

    print(f"Attempt {attempt + 1} failed: {response.status_code}")
    time.sleep(10)

response.raise_for_status()

response_json = response.json()

review = (response_json["candidates"][0]["content"]["parts"][0]["text"])

print(review)

with open("review.json", "w", encoding="utf-8") as f:
    f.write(review)

# POST REVIEW BACK TO PR
pr_number = os.environ["GITHUB_PR_NUMBER"]  # or get from context
repo = os.environ["GITHUB_REPOSITORY"]  # format: owner/repo
owner, repo_name = repo.split("/")

github_api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{pr_number}/comments"

comment_payload = {
    "body": review
}

headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}

comment_response = requests.post(github_api_url, json=comment_payload, headers=headers)
comment_response.raise_for_status()

print(f"Review posted to PR #{pr_number}")
