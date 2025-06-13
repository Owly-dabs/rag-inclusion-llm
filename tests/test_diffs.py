from github_api.fetch_commits import get_commits_from_pr
from github_api.fetch_diffs import get_code_regions, get_code_diffs

REPO = "PrefectHQ/prefect" 
PR_NUMBER = 18226            

def test_code_regions_from_pr():
    commits = get_commits_from_pr(REPO, PR_NUMBER)
    code_regions = get_code_regions(REPO, commits)

    print(f"\n--- Fetched {len(code_regions)} changed files ---\n")

    for region in code_regions:
        print(f"== {region.filename} ==")
        for snippet in region.regions:
            print("--- Region ---")
            print(snippet)
        print("\n")

def test_get_code_diffs():
    commits = get_commits_from_pr(REPO, PR_NUMBER)
    
    # Ensure we have commits to test against
    assert len(commits) > 0, "No commits found for the PR"

    diffs = get_code_diffs(REPO, commits)
    
    # Check if diffs are returned and are not empty
    assert isinstance(diffs, str), "Diffs should be a string"
    assert len(diffs) > 0, "No diffs returned"


if __name__ == "__main__":
    test_code_regions_from_pr()