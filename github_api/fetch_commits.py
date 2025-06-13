from github import Github
import os
from dotenv import load_dotenv
from models.datatypes import CommitInfo

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)


def get_commits_from_pr(repo_full_name: str, pr_number: int) -> list[CommitInfo]:
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    commits = pr.get_commits()

    return [CommitInfo(sha=c.sha, message=c.commit.message) for c in commits]


def get_commit_objects(repo, commits: list[CommitInfo]):
    return [repo.get_commit(c.sha) for c in commits]

# Unused
def get_commits_referencing_issue(repo_full_name: str, issue_number: int):
    """
    Return a list of commits that reference a given issue number in their message.
    """
    repo = g.get_repo(repo_full_name)
    issue = repo.get_issue(number=issue_number)
    issue_identifier = f"#{issue_number}"

    # Collect commits from the last 100 (adjust if needed)
    commits = repo.get_commits()
    matching_commits = []

    for commit in commits[:100]:  # GitHub API pagination by default
        if commit.commit.message and issue_identifier in commit.commit.message:
            matching_commits.append({
                "sha": commit.sha,
                "message": commit.commit.message
            })

    return matching_commits