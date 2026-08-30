import os
import requests
from fastapi import FastAPI, Request, BackgroundTasks, status
from github import Github, Auth
from dotenv import load_dotenv

# Import your core pipeline components from Steps 3 and 4!
from parser import parse_diff_to_graph
from diagram_generator import generate_mermaid_chart

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

app = FastAPI(title="DiffGraph Webhook Runner")

def process_pr_and_comment(pr_number: int, repo_full_name: str, diff_url: str):
    """
    Heavy lifting function executed as a background task. 
    Prevents the server from freezing or timing out GitHub's webhook.
    """
    try:
        print(f"🧠 [Background] Analyzing PR #{pr_number} for {repo_full_name}...")
        
        # 1. Fetch raw diff from the incoming webhook target URL
        diff_response = requests.get(diff_url)
        if diff_response.status_code != 200:
            print(f"❌ Failed to download diff from {diff_url}")
            return
        
        # Limit token consumption for swift local execution chunk processing
        raw_diff = diff_response.text[:1000]
        
        # 2. Extract structural nodes/edges JSON via your local Llama 3.2 engine
        graph_json = parse_diff_to_graph(raw_diff)
        if not graph_json:
            print("❌ Parsing failed. Local LLM output invalid format.")
            return
            
        # 3. Translate JSON to stylized Mermaid text blocks
        mermaid_syntax = generate_mermaid_chart(graph_json)
        
        # 4. Authenticate and comment directly onto the active GitHub PR thread
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        repo = g.get_repo(repo_full_name)
        pull_request = repo.get_pull(pr_number)
        
        comment_body = f"""### 📊 DiffGraph Architecture Review

This dependency visualization has been automatically generated using local Llama 3.2 code analysis:

```mermaid
{mermaid_syntax}
```

*Processed completely offline via DiffGraph Dev Engine.*"""
        
        # Push the markdown block live to GitHub
        pull_request.create_issue_comment(comment_body)
        print(f"✅ Success! Diagram review posted to PR #{pr_number}.")

    except Exception as e:
        print(f"❌ Background processor encountered an error: {e}")


@app.post("/webhook", status_code=status.HTTP_200_OK)
async def github_webhook_listener(request: Request, background_tasks: BackgroundTasks):
    """
    Receives events directly from GitHub Webhook triggers.
    Validates the intent, queues the LLM work, and immediately returns 200 OK.
    """
    # Parse the incoming JSON body from GitHub
    payload = await request.json()
    
    # Check if this request is related to a Pull Request event
    if "pull_request" in payload:
        action = payload.get("action")
        
        # We only want to execute logic when a PR is first opened or updated (synchronize)
        if action in ["opened", "synchronize"]:
            pr_data = payload["pull_request"]
            pr_number = payload["number"]
            repo_full_name = payload["repository"]["full_name"]
            diff_url = pr_data["diff_url"]
            
            print(f"📥 Received Webhook notification: PR #{pr_number} ({action}) on {repo_full_name}")
            
            # Dispatch heavy parsing work to execution background queue
            background_tasks.add_task(
                process_pr_and_comment, 
                pr_number, 
                repo_full_name, 
                diff_url
            )
            
            return {"status": "event_queued", "message": "DiffGraph analysis started in the background."}
            
    # Ignore actions we don't care about (like closing or assigning PRs)
    return {"status": "ignored", "message": "Event action type not targeted by DiffGraph."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
