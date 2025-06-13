from prefect import flow, task
import pandas as pd
from pathlib import Path
import json

# Local imports (these modules you will define)
from github_api.fetch_commits import get_commits_from_pr
from github_api.fetch_diffs import get_code_regions
from github_api.fetch_readme import get_readme_head
from utils.topic_mapping import map_topic_number_to_name
from prompt.assemble import build_prompt
from llm.call_openai import generate_llm_explanation
from models.datatypes import CommitInfo, CodeRegion, PromptRow

DATA_SAMPLE = "01010" # Sample data identifier

DATA_PATH = Path(f"data/{DATA_SAMPLE}.feather")  # Feather format
MAPTOPIC_PATH = Path("data/maptopics.csv")
OUTPUT_PATH = Path(f"outputs/{DATA_SAMPLE}/explanations.jsonl")

@task
def load_data() -> list[PromptRow]:
    df = pd.read_feather(DATA_PATH)

    # Filter for rows where 'bertopic' is not -1, which means topic has been successfully classified
    # Filter for rows where 'chunk' is 0, which is where the summary of the issue is given
    df = df[(df["bertopic"] != -1) & (df["chunk"] == 0)]

    # Only have relevant columns
    df = df[["repo", "issue_no", "summary", "bertopic"]]

    # replace underscores in repo names with slashes
    df['repo'] = df['repo'].str.replace('_', '/', regex=False)
    
    rows = [
        PromptRow(
            repo=row.repo,
            issue_no=int(row.issue_no),
            summary=row.summary,
            bertopic=int(row.bertopic)
        )
        for row in df.itertuples()
    ]
    return rows


@task
def load_topic_map():
    return pd.read_csv(MAPTOPIC_PATH).set_index("topicno2").to_dict()["topic_name"]


@task
def save_response(repo, issue_no, explanation):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "a") as f:
        f.write(json.dumps({
            "repo": repo,
            "issue_no": issue_no,
            "explanation": explanation
        }) + "\n")


@flow
def explanation_flow():
    rows = load_data()
    topic_map = load_topic_map()

    for row in rows:
        try:
            topic_name = map_topic_number_to_name(row.bertopic, topic_map)
            # Fetch commits from PR
            commits: list[CommitInfo] = get_commits_from_pr(row.repo, row.issue_no)
            # Get code regions (diffs + pre-change content)
            code_regions: list[CodeRegion] = get_code_regions(row.repo, commits)
            # Get README head (after title)
            readme = get_readme_head(row.repo)

            prompt_json = build_prompt(
                topic_name=topic_name,
                summary=row.summary,
                code_regions=code_regions,
                extra={"readme": readme},
                instructions="Explain what code changes need to be made, and why."
            )
            explanation = generate_llm_explanation(prompt_json)
            save_response(row.repo, row.issue_no, explanation)
        except Exception as e:
            print(f"Error processing {row.repo}#{row.issue_no}: {e}")


if __name__ == "__main__":
    explanation_flow()
