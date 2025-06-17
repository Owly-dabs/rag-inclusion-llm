from prefect import flow, task
import pandas as pd
from pathlib import Path
import json

# Local imports (these modules you will define)
from utils.logger import logger
from github_api.fetch_commits import get_commits_from_pr
from github_api.fetch_diffs import get_code_regions
from github_api.fetch_readme import get_readme_head
from utils.topic_mapping import map_topic_number_to_name
from prompt.assemble import build_prompt
from llm.call_openai import generate_llm_explanation
from models.datatypes import CommitInfo, CodeRegion, PromptRow

LOGGING_LEVEL = "DEBUG" # Comment this line for default usage
logger.setLevel(LOGGING_LEVEL)

DATA_SAMPLE = "sample_issues2" # Sample data identifier

DATA_PATH = Path(f"data/{DATA_SAMPLE}.feather")  # Feather format
MAPTOPIC_PATH = Path("data/maptopics.csv")
OUTPUT_PATH = Path(f"outputs/{DATA_SAMPLE}/explanations.jsonl")

FIXED_INSTRUCTIONS = "Explain what code changes need to be made, and why."

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
    return pd.read_csv(MAPTOPIC_PATH).set_index("topicno1").to_dict()["topic_name"]


@task
def save_response(repo, issue_no, topic_name, explanation):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "a") as f:
        f.write(json.dumps({
            "repo": repo,
            "issue_no": issue_no,
            "topic": topic_name,
            "explanation": explanation
        }) + "\n")


@flow
def explanation_flow():
    rows = load_data()
    topic_map = load_topic_map()

    for row in rows:
        try:
            topic_name = f"{row.bertopic}: {map_topic_number_to_name(row.bertopic, topic_map)}"
            commits: list[CommitInfo] = get_commits_from_pr(row.repo, row.issue_no)
            code_regions: list[CodeRegion] = get_code_regions(row.repo, commits)
            logger.debug(f"Processing {row.repo}#{row.issue_no} for topic '{topic_name}' with {len(code_regions)} code regions.")
            readme = get_readme_head(row.repo)

            region_outputs = []
            for region in code_regions:
                prompt_json = build_prompt(
                    topic_name=topic_name,
                    summary=row.summary,
                    code_region=region,  # single region
                    extra={"readme": readme},
                    instructions=FIXED_INSTRUCTIONS
                )
                explanation = generate_llm_explanation(prompt_json)
                region_outputs.append({"code": region.code, "explanation": explanation})

            save_response(row.repo, row.issue_no, topic_name, region_outputs)

        except Exception as e:
            print(f"Error processing {row.repo}#{row.issue_no}: {e}")


if __name__ == "__main__":
    explanation_flow()
