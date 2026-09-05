import os
import json
import urllib.request
import urllib.error

api_key = os.getenv("GEMINI_API_KEY")
candidate_models = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-flash-latest",
    "gemma-2-9b-it",
    "gemma-2-27b-it"
]

for model in candidate_models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Say 'hello' in one word."}]}]
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            ans = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"✓ Model {model} SUCCEEDED: {ans.strip()}")
            break
    except urllib.error.HTTPError as e:
        print(f"✗ Model {model}: HTTP {e.code} ({e.read().decode('utf-8')[:80]})")
    except Exception as e:
        print(f"✗ Model {model}: {e}")
