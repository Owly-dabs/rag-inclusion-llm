import re
from github import Github, Repository, Commit
import os
from dotenv import load_dotenv
from github_api.fetch_commits import get_commit_objects
from models.datatypes import CommitInfo, CodeRegion
from utils.file_filters import is_test_file

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)


def _get_file_content_before_commit(repo: Repository.Repository, commit: Commit.Commit) -> dict[str, str]:
    parent = commit.parents[0] if commit.parents else None
    if not parent:
        return {}

    file_versions = {}
    for file in commit.files:
        try:
            contents = repo.get_contents(file.filename, ref=parent.sha)
            file_versions[file.filename] = contents.decoded_content.decode()
        except Exception:
            continue

    return file_versions


def _extract_code_regions_around_patch(pre_change_code: str, patch: str, context_lines: int = 3) -> list[str]:
    code_lines = pre_change_code.splitlines()
    code_blocks = []

    for match in re.finditer(r"@@ -(\d+)(?:,(\d+))?", patch):
        start_line = int(match.group(1)) - 1
        length = int(match.group(2)) if match.group(2) else 1

        lower = max(0, start_line - context_lines)
        upper = min(len(code_lines), start_line + length + context_lines)

        snippet = "\n".join(code_lines[lower:upper])
        code_blocks.append(snippet)

    return code_blocks


def get_code_regions(repo_full_name: str, commits: list[CommitInfo], context_lines: int = 3) -> list[CodeRegion]:
    repo = g.get_repo(repo_full_name)
    commit_objs = get_commit_objects(repo, commits)
    code_regions: list[CodeRegion] = []

    for commit in commit_objs:
        pre_change_files = _get_file_content_before_commit(repo, commit)

        for file in commit.files:
            if is_test_file(file.filename):
                continue
            if file.patch and file.filename in pre_change_files:
                pre_code = pre_change_files[file.filename]
                regions = _extract_code_regions_around_patch(pre_code, file.patch, context_lines)

                for region in regions:
                    code_regions.append(CodeRegion(
                        filename=file.filename,
                        code=region
                    ))

    return code_regions


def get_code_diffs(repo_full_name: str, commits: list) -> str:
    """
    Fetches and concatenates code diffs (patches) for a list of commit SHAs.
    Returns a single string of unified diffs.
    """
    repo = g.get_repo(repo_full_name)
    all_diffs = []

    for commit_info in commits:
        sha = commit_info["sha"]
        commit = repo.get_commit(sha=sha)
        for file in commit.files:
            if file.patch:  # Only include files with diff info
                all_diffs.append(f"File: {file.filename}\n{file.patch}\n")

    return "\n".join(all_diffs)