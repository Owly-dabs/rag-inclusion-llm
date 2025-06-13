from github import Github
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)


def get_readme_head(repo_full_name: str, max_lines: int = 50) -> str:
    """
    Fetch up to `max_lines` lines of README content starting after the first H1 title.
    """
    try:
        repo = g.get_repo(repo_full_name)
        readme = repo.get_readme()
        content = readme.decoded_content.decode()
        lines = content.splitlines()

        # Find the first H1 title (`# Title`)
        start_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("# "):
                start_index = i + 1
                break

        return "\n".join(lines[start_index:start_index + max_lines])

    except Exception as e:
        print(f"[WARN] Failed to fetch README for {repo_full_name}: {e}")
        return ""