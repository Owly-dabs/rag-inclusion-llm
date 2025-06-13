from github_api.fetch_commits import get_commits_from_pr

if __name__ == "__main__":
    repo = "PrefectHQ/prefect"
    pr_number = 3549
    commits = get_commits_from_pr(repo, pr_number)
    
    for c in commits:
        print(f"{c['sha']}: {c['message']}")