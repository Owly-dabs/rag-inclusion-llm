from github_api.fetch_readme import get_readme_head

if __name__ == "__main__":
    repo = "microsoft/CNTK"  # Example repository
    print(get_readme_head(repo))