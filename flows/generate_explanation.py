from prefect import flow, task
import pandas as pd
from pathlib import Path
import json
from dataclasses import asdict

# Local imports (these modules you will define)
from utils.logger import logger
from github_api.fetch_commits import get_commits_from_pr
from github_api.fetch_diffs import get_code_regions
from github_api.fetch_readme import get_readme_head
from utils.topic_mapping import map_topic_number_to_name
from prompt.assemble import build_prompt
from llm.call_openai import generate_llm_explanation
from models.datatypes import CommitInfo, CodeRegion, PromptRow, PromptResponse

LOGGING_LEVEL = "DEBUG" # Comment this line for default usage
logger.setLevel(LOGGING_LEVEL or "INFO")

DATA_SAMPLE = "sample_issues2" # Sample data identifier

DATA_PATH = Path(f"data/{DATA_SAMPLE}.feather")  # Feather format
MAPTOPIC_PATH = Path("data/maptopics.csv")
OUTPUT_PATH = Path(f"outputs/{DATA_SAMPLE}/explanations_newprompt.jsonl")

# FIXED_INSTRUCTIONS = "Explain what code changes need to be made, and why."
FIXED_INSTRUCTIONS = '''
Given the topic and summary of the issue, analyze the provided code region and explain both why a change is necessary and what changes should be made to address or improve it. Be specific to the code shown, but acknowledge if the fix likely involves updates in other parts of the codebase. Justify your recommendations clearly and concisely, referencing relevant patterns or best practices where appropriate. Use the following format:

## Explanation of the issue:
<What is the issue and why a change is needed (1 paragraph)>

### Suggested code changes:
<Describe what changes should be made to fix or improve the code>

### Supplementary notes (if any):
<Any references to best practices, broader architectural concerns, etc.>
'''

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
def save_response(response: PromptResponse):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "a") as f:
        f.write(json.dumps(asdict(response)) + "\n")


@flow
def explanation_flow():
    rows = load_data()
    topic_map = load_topic_map()

    for row in rows:
        try:
            topic_name = f"{row.bertopic}: {map_topic_number_to_name(row.bertopic, topic_map)}"
            commits: list[CommitInfo] = get_commits_from_pr(row.repo, row.issue_no)
            code_regions: list[CodeRegion] = get_code_regions(row.repo, commits)
            logger.info(f"Processing {row.repo}#{row.issue_no} for topic '{topic_name}' with {len(code_regions)} code regions.")
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

            response = PromptResponse(repo=row.repo,issue_no=row.issue_no,topic=topic_name,code_regions=region_outputs)
            save_response(response)

        except Exception as e:
            print(f"Error processing {row.repo}#{row.issue_no}: {e}")


if __name__ == "__main__":
    explanation_flow()
