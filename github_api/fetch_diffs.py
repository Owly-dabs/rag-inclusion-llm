import re
from github import Github, Repository, Commit
import os
from dotenv import load_dotenv
from github_api.fetch_commits import get_commit_objects
from models.datatypes import CommitInfo, CodeRegion
from utils.file_filters import is_test_file
from utils.logger import logger

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)

def _get_file_content(repo: Repository.Repository, commit: Commit.Commit, parent: Commit.Commit | None = None) -> dict[str, str]:
    file_versions = {}
    if not parent: parent = commit
    for file in commit.files:
        try:
            contents = repo.get_contents(file.filename, ref=parent.sha)
            file_versions[file.filename] = contents.decoded_content.decode()
        except Exception:
            continue
    return file_versions

def _get_file_content_before_commit(repo: Repository.Repository, commit: Commit.Commit) -> dict[str, str]:
    parent = commit.parents[0] if commit.parents else None
    if not parent:
        return {}

    file_versions = _get_file_content(repo, commit, parent)
    # file_versions = {}
    # for file in commit.files:
    #     try:
    #         contents = repo.get_contents(file.filename, ref=parent.sha)
    #         file_versions[file.filename] = contents.decoded_content.decode()
    #     except Exception:
    #         continue

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

def _extract_matched_code_regions(pre_code: str, post_code: str, patch: str, context_lines: int = 3) -> list[tuple[str, str]]:
    pre_lines = pre_code.splitlines()
    post_lines = post_code.splitlines()
    pairs = []

    # Matches both pre and post start lines from unified diff header
    for match in re.finditer(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))?", patch):
        start_pre = int(match.group(1)) - 1
        len_pre = int(match.group(2)) if match.group(2) else 1
        start_post = int(match.group(3)) - 1
        len_post = int(match.group(4)) if match.group(4) else 1

        lower_pre = max(0, start_pre - context_lines)
        upper_pre = min(len(pre_lines), start_pre + len_pre + context_lines)
        region_pre = "\n".join(pre_lines[lower_pre:upper_pre])

        lower_post = max(0, start_post - context_lines)
        upper_post = min(len(post_lines), start_post + len_post + context_lines)
        region_post = "\n".join(post_lines[lower_post:upper_post])

        pairs.append((region_pre, region_post))

    return pairs



# def get_code_regions(repo_full_name: str, commits: list[CommitInfo], context_lines: int = 3) -> list[CodeRegion]:
#     repo = g.get_repo(repo_full_name)
#     commit_objs = get_commit_objects(repo, commits)
#     # logger.debug(f"Fetching code regions for {len(commit_objs)} commits in {repo_full_name}")
#     code_regions: list[CodeRegion] = []

#     for commit in commit_objs:
#         pre_change_files = _get_file_content_before_commit(repo, commit)

#         for file in commit.files:
#             if is_test_file(file.filename):
#                 continue
#             if file.patch and file.filename in pre_change_files:
#                 pre_code = pre_change_files[file.filename]
#                 regions = _extract_code_regions_around_patch(pre_code, file.patch, context_lines)

#                 for region in regions:
#                     code_regions.append(CodeRegion(
#                         filename=file.filename,
#                         code=region,
#                     ))


#     return code_regions

def get_code_regions(repo_full_name: str, commits: list[CommitInfo], context_lines: int = 3) -> list[tuple[CodeRegion, CodeRegion]]:
    repo = g.get_repo(repo_full_name)
    commit_objs = get_commit_objects(repo, commits)
    region_pairs: list[tuple[CodeRegion, CodeRegion]] = []

    for commit in commit_objs:
        pre_change_files = _get_file_content_before_commit(repo, commit)
        post_change_files = _get_file_content(repo, commit)

        for file in commit.files:
            if is_test_file(file.filename):
                continue
            if file.patch and file.filename in pre_change_files and file.filename in post_change_files:
                pre_code = pre_change_files[file.filename]
                post_code = post_change_files[file.filename]

                matched_regions = _extract_matched_code_regions(pre_code, post_code, file.patch, context_lines)

                for region_pre, region_post in matched_regions:
                    region_pairs.append((
                        CodeRegion(filename=file.filename, code=region_pre),
                        CodeRegion(filename=file.filename, code=region_post)
                    ))

    return region_pairs

def get_code_regions_from_pr(repo_full_name: str, issue_no: int, context_lines: int = 3) -> list[tuple[CodeRegion, CodeRegion]]:
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(issue_no)
    region_pairs = []

    for file in pr.get_files():
        if file.status == "removed":
            continue  # No post-PR content

        try:
            pre_code = repo.get_contents(file.filename, ref=pr.base.sha).decoded_content.decode()
            post_code = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()
        except Exception:
            continue

        if file.patch and not is_test_file(file.filename):
            matched_regions = _extract_matched_code_regions(pre_code, post_code, file.patch, context_lines)
            for pre, post in matched_regions:
                region_pairs.append((
                    CodeRegion(filename=file.filename, code=pre),
                    CodeRegion(filename=file.filename, code=post)
                ))

    return region_pairs

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