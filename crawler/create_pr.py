import requests
import base64
import os

# TODO: Set your GitHub token here or via environment variable
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "<YOUR_GITHUB_TOKEN>")
GITHUB_API = "https://api.github.com"

# Example usage:
# create_pr(
#   repo_url="https://github.com/yourorg/yourrepo",
#   branch="fix/compliance",
#   file_path="docs/privacy.md",
#   new_content="# Privacy Policy...",
#   rule_id="missing_privacy_policy"
# )
def create_pr(repo_url, branch, file_path, new_content, rule_id):
    owner_repo = repo_url.rstrip('/').split('/')[-2:]
    owner, repo = owner_repo
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    # 1. Get default branch SHA
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/git/refs/heads/main", headers=headers)
    r.raise_for_status()
    base_sha = r.json()['object']['sha']
    # 2. Create new branch
    r = requests.post(f"{GITHUB_API}/repos/{owner}/{repo}/git/refs", headers=headers, json={
        "ref": f"refs/heads/{branch}",
        "sha": base_sha
    })
    if r.status_code not in (201, 422):  # 422 if branch exists
        r.raise_for_status()
    # 3. Get file SHA if exists
    file_sha = None
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/contents/{file_path}", headers=headers)
    if r.status_code == 200:
        file_sha = r.json()['sha']
    # 4. Commit file
    content_b64 = base64.b64encode(new_content.encode()).decode()
    commit_data = {
        "message": f"Auto-Fix: {rule_id}",
        "content": content_b64,
        "branch": branch
    }
    if file_sha:
        commit_data["sha"] = file_sha
    r = requests.put(f"{GITHUB_API}/repos/{owner}/{repo}/contents/{file_path}", headers=headers, json=commit_data)
    r.raise_for_status()
    # 5. Create PR
    pr_data = {
        "title": f"Auto-Fix: {rule_id}",
        "head": branch,
        "base": "main",
        "body": f"Automated fix for rule: {rule_id}"
    }
    r = requests.post(f"{GITHUB_API}/repos/{owner}/{repo}/pulls", headers=headers, json=pr_data)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    # Example usage
    print("TODO: Set GITHUB_TOKEN and call create_pr() with real values.") 