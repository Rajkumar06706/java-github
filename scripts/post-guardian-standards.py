import json
import os
import requests
import time
api_pass="g@tl@b"
api_key = os.environ["GEMINI_API_KEY"]

with open("pr.diff", "r", encoding="utf-8") as f:
    diff = f.read()

with open("standards/post-guardian-standards.md", "r", encoding="utf-8") as f:
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

#print(review)

with open("review.json", "w", encoding="utf-8") as f:
    f.write(review)
