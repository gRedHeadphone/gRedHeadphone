import requests
import os
import re

def fetch_github_data(username, token, type):
    """Fetches data from the GitHub API."""
    url = f"https://api.github.com/search/issues?q=author:{username}+is:{type}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_github_commits(username, token):
    """Fetches commits from the GitHub API."""
    url = f"https://api.github.com/search/commits?q=author:{username}&sort=committer-date&order=desc"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.cloak-preview+json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def generate_readme_content(issues, pull_requests, commits):
    """Generates the README content."""
    content = "## ⚡️ Recent Activity\n\n"

    content += "### 🐛 Recent Issues ([view all](https://github.com/search?q=author%3AgRedHeadphone+&type=issues))\n"
    if issues and issues.get("items"):
        for issue in issues["items"][:5]:
            repo_name = "/".join(issue['html_url'].split('/')[3:5])
            repo_url = f"https://github.com/{repo_name}"
            content += f"- Created Issue [#{issue['number']} {issue['title']}]({issue['html_url']}) in [{repo_name}]({repo_url})\n"
    else:
        content += "- No recent issues\n"

    content += "\n### 🚀 Recent Pull Requests ([view all](https://github.com/search?q=author%3AgRedHeadphone+&type=pullrequests))\n"
    if pull_requests and pull_requests.get("items"):
        for pr in pull_requests["items"][:5]:
            repo_name = "/".join(pr['html_url'].split('/')[3:5])
            repo_url = f"https://github.com/{repo_name}"
            status = "Merged" if pr.get('pull_request', {}).get('merged_at') else "Opened"
            content += f"- {status} PR [#{pr['number']} {pr['title']}]({pr['html_url']}) in [{repo_name}]({repo_url})\n"
    else:
        content += "- No recent pull requests\n"

    content += "\n### 📝 Recent Commits ([view all](https://github.com/search?q=author%3AgRedHeadphone&type=commits&s=committer-date&o=desc))\n"
    if commits and commits.get("items"):
        for commit in commits["items"][:5]:
            repo_name = commit['repository']['full_name']
            repo_url = commit['repository']['html_url']
            commit_message = commit['commit']['message'].split('\n')[0]
            commit_message = re.sub(r'^\[.*?\]\s*', '', commit_message)
            if len(commit_message) > 50:
                commit_message = commit_message[:47] + '...'
            content += f"- Committed [{commit_message}]({commit['html_url']}) to [{repo_name}]({repo_url})\n"
    else:
        content += "- No recent commits\n"

    return content

def main():
    """Main function."""
    username = os.environ.get("GITHUB_ACTOR")
    token = os.environ.get("GITHUB_TOKEN")

    if not username or not token:
        print("GITHUB_ACTOR or GITHUB_TOKEN environment variables not set.")
        return

    try:
        issues = fetch_github_data(username, token, "issue")
        pull_requests = fetch_github_data(username, token, "pr")
        commits = fetch_github_commits(username, token)
        content = generate_readme_content(issues, pull_requests, commits)
        with open("README.md", "w") as f:
            f.write(content)
        print("README.md updated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub: {e}")

if __name__ == "__main__":
    main()