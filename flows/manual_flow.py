from prefect import flow, task
from dataclasses import asdict
import pandas as pd
from pathlib import Path
import json
from utils.logger import logger
from models.datatypes import ManualPromptRow, PromptResponse, CodeRegion
from prompt.assemble import build_explanation_prompt
from github_api.fetch_readme import get_readme_head
from llm.explanation_llm import generate_llm_explanation

SAMPLE_ID = "002"
EXPERIMENT_PATH = Path(f"experiments/exp_{SAMPLE_ID}") 

DATA_PATH = EXPERIMENT_PATH / "data.csv"
BASE_OUTPUT_PATH = EXPERIMENT_PATH / "base_output.jsonl"
AUGMENTED_OUTPUT_PATH = EXPERIMENT_PATH / "augmented_output.jsonl"

FIXED_INSTRUCTIONS = '''
Given the topic and summary of the issue, analyze the provided code region and explain both why a change is necessary and what changes should be made to address or improve it. Be specific to the code shown, but acknowledge if the fix likely involves updates in other parts of the codebase. Justify your recommendations clearly and concisely, referencing relevant patterns or best practices where appropriate. Use the following format:

Additionally, refer to the "extra_info" section provided for any additional context that may assist your explanation and recommendations.

## Explanation of the issue:
<What is the issue and why a change is needed (1 paragraph)>

### Suggested code change:
```python
<Fixed code>
```
<Short description of code change>

### Supplementary notes (if any):
<Any references to best practices, broader architectural concerns, etc.>
'''

@task
def load_data_csv(data_path: Path) -> list[ManualPromptRow]:
    df = pd.read_csv(data_path)
    
    # Only have relevant columns
    df = df[["url", "summary", "topic", "code", "extra", "answer"]]
    
    rows = [
        ManualPromptRow(
            url=row.url,
            summary=row.summary,
            topic=row.topic,
            code=row.code,
            extra=row.extra,
            answer=row.answer
        ) for row in df.itertuples()
    ]

    return rows

@task
def save_response(response: PromptResponse, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "a") as f:
        f.write(json.dumps(asdict(response)) + "\n")

def get_repo_issue_from_url(url: str) -> tuple[str, int]:
    parts = url.split('/')
    repo = f"{parts[3]}/{parts[4]}"
    issue_no = int(parts[-1])
    return repo, issue_no

@flow
def manual_explanation_flow(data_path: Path, output_path: Path, include_extra: bool = False):
    rows = load_data_csv(data_path)

    for row in rows:
        try:
            logger.info(f"Processing {row.url} for topic '{row.topic}'")
            
            repo, issue_no = get_repo_issue_from_url(row.url)
            extra = {"context": row.extra} if include_extra else {}
             
            # Build the prompt using the manual data
            prompt_json = build_explanation_prompt(
                topic_name=row.topic,
                summary=row.summary,
                code_region=CodeRegion(filename=row.url, code=row.code),
                extra=extra,
                instructions=FIXED_INSTRUCTIONS
            )

            explanation = generate_llm_explanation(prompt_json)
            code_regions = [CodeRegion(
                filename=row.url,
                code=row.code,
                explanation=explanation,
                answer=row.answer
                )]
            
            response = PromptResponse(repo=repo,issue_no=issue_no,topic=row.topic,code_regions=code_regions)

            save_response(response, output_path)

        except Exception as e:
            logger.error(f"Error processing {row.url}: {e}")
            
@flow
def manual_experiment_flow():
    
    manual_explanation_flow(
        data_path=DATA_PATH,
        output_path=BASE_OUTPUT_PATH,
        include_extra=False
        )
    
    manual_explanation_flow(
        data_path=DATA_PATH,
        output_path=AUGMENTED_OUTPUT_PATH,
        include_extra=True
    )
    
if __name__ == "__main__":
    manual_experiment_flow()
    logger.info(f"Experiment completed. Outputs saved to {BASE_OUTPUT_PATH} and {AUGMENTED_OUTPUT_PATH}.")