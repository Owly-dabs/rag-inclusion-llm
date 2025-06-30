from prefect import flow, task
import pandas as pd
from pathlib import Path
import json
from dataclasses import asdict

# Local imports (these modules you will define)
from utils.logger import logger
from github_api.fetch_commits import get_commits_from_pr
from github_api.fetch_diffs import get_code_regions, get_code_regions_from_pr, CodeRegionLimitException
from github_api.fetch_readme import get_readme_head
from utils.topic_mapping import map_topic_number_to_name
from prompt.assemble import build_explanation_prompt
from llm.explanation_llm import generate_llm_explanation
from models.datatypes import CommitInfo, CodeRegion, PromptRow, PromptResponse

LOGGING_LEVEL = "DEBUG" # Comment this line for default usage
logger.setLevel(LOGGING_LEVEL or "INFO")

DATA_SAMPLE = "sample_issues2" # Sample data identifier

DATA_PATH = Path(f"data/{DATA_SAMPLE}.feather")  # Feather format
MAPTOPIC_PATH = Path("data/maptopics.csv")
OUTPUT_PATH = Path(f"outputs/{DATA_SAMPLE}/explanations.jsonl")

# FIXED INSTRUCTIONS = '''

# FIXED_INSTRUCTIONS = "Explain what code changes need to be made, and why."
FIXED_INSTRUCTIONS = '''
Given the topic and summary of the issue, analyze the provided code region and explain both why a change is necessary and what changes should be made to address or improve it. Be specific to the code shown, but acknowledge if the fix likely involves updates in other parts of the codebase. Justify your recommendations clearly and concisely, referencing relevant patterns or best practices where appropriate. Use the following format:

Additionally, refer to the "extra_info" section provided for any additional context that may assist your explanation and recommendations.

## Explanation of the issue:
<What is the issue and why a change is needed (1 paragraph)>

### Suggested code changes:
<Describe what changes should be made to fix or improve the code>

### Supplementary notes (if any):
<Any references to best practices, broader architectural concerns, etc.>
'''

@task
def load_data(data_path: Path = DATA_PATH) -> list[PromptRow]:
    df = pd.read_feather(data_path)

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
def save_response(response: PromptResponse, output_path: Path = OUTPUT_PATH):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "a") as f:
        f.write(json.dumps(asdict(response)) + "\n")


@flow
def explanation_flow(data_path: Path = DATA_PATH, output_path: Path = OUTPUT_PATH, extra_info: dict | None = None):
    rows = load_data(data_path)
    topic_map = load_topic_map()

    for row in rows:
        try:
            topic_name = f"{row.bertopic}: {map_topic_number_to_name(row.bertopic, topic_map)}"
            # commits: list[CommitInfo] = get_commits_from_pr(row.repo, row.issue_no)
            try:
                code_regions: list[tuple[CodeRegion,CodeRegion]] = get_code_regions_from_pr(row.repo, row.issue_no)
            except CodeRegionLimitException as cre_error:
                logger.info(f"{cre_error} for {row.repo}#{row.issue_no}. Skipping this issue.")
                continue
            except Exception as pr_error:
                logger.debug(f"No PR found for {row.repo}#{row.issue_no}. Skipping this issue. Info: {pr_error}")
                continue  # Skip this issue and move to the next one
            
            logger.info(f"Processing {row.repo}#{row.issue_no} for topic '{topic_name}' with {len(code_regions)} code regions.")
            
            extra = {"readme": get_readme_head(row.repo)}

            if extra_info:
                extra.update(extra_info)

            region_outputs = []
            for pre_region, _ in code_regions:
                prompt_json = build_explanation_prompt(
                    topic_name=topic_name,
                    summary=row.summary,
                    code_region=pre_region,  # single region
                    extra=extra,
                    instructions=FIXED_INSTRUCTIONS
                )
                explanation = generate_llm_explanation(prompt_json)
                region_outputs.append(CodeRegion(
                    filename=pre_region.filename,
                    code=pre_region.code,
                    explanation=explanation
                ))
                # region_outputs.append({"code": pre_region.code, "explanation": explanation})

            response = PromptResponse(repo=row.repo,issue_no=row.issue_no,topic=topic_name,code_regions=region_outputs)
            
            save_response(response, output_path)

        except Exception as e:
            logger.error(f"Error processing {row.repo}#{row.issue_no}: {e}")


if __name__ == "__main__":
    explanation_flow()
