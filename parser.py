import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def parse_diff_to_graph(diff_text):
    print("🧠 Engineering prompt and parsing diff into JSON graph structure...")
    
    url = "http://localhost:11434/api/generate"
    
    # Strict prompt engineering to force a graph schema
    system_instruction = """
    You are a code architecture analyzer. You must output raw JSON only. Do not include markdown formatting like ```json or any conversational text.
    
    Analyze the Git diff and convert it into a structural dependency graph with nodes and edges.
    Identify any contract mismatches, breaking changes, or missing payload fields. If found, set "has_error" to true and describe the conflict.

    The output JSON schema must strictly match this structure:
    {
        "nodes": [{"id": "string", "label": "string", "type": "file|component|module"}],
        "edges": [{"source": "string", "target": "string", "relationship": "string"}],
        "has_error": boolean,
        "error_details": "string or null"
    }
    """
    
    prompt = f"{system_instruction}\n\nGit Diff to analyze:\n{diff_text}"
    
    payload = {
        "model": "llama3:latest",
        "prompt": prompt,
        "format": "json", # Forces Ollama to output valid JSON
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            raw_response = response.json().get("response", "{}")
            
            # Parse the string text into a real Python dictionary
            graph_data = json.loads(raw_response)
            return graph_data
        else:
            print(f"❌ Ollama Error: Status code {response.status_code}")
            return None
    except json.JSONDecodeError:
        print("❌ JSON Parsing Error: The model output invalid JSON structure.")
        print(f"Raw Output was: {raw_response}")
        return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

if __name__ == "__main__":
    # Test sample simulating a breaking change payload mismatch
    mock_diff = """
    diff --git a/api/user.py b/api/user.py
    index 12345..67890 100644
    --- a/api/user.py
    +++ b/api/user.py
    @@ -10,4 +10,4 @@
    - def create_user(username, email):
    + def create_user(username): # REMOVED EMAIL FIELD - BREAKING CHANGE
         print(username)
    """
    
    result = parse_diff_to_graph(mock_diff)
    if result:
        print("\n📊 Generated Graph Structure Output:")
        print(json.dumps(result, indent=2))
