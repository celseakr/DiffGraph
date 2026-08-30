import requests

# Direct execution targeting the specific FastAPI port address
url = "http://localhost:8000/webhook"

payload = {
    "action": "opened",
    "number": 1,
    "repository": {
        "full_name": "octocat/Hello-World"
    },
    "pull_request": {
        "diff_url": "https://github.com"
    }
}

print(f"📡 Sending mock payload directly to FastAPI server at {url}...")

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"🔹 Server Response Status: {response.status_code}")
    print(f"🔹 Server Body Response: {response.json()}")
except requests.exceptions.ConnectionError:
    print("❌ Connection Failed! Check if 'python main.py' is actively running in your other window.")
except Exception as e:
    print(f"❌ An error occurred: {e}")
