from prefect import flow, task
from pathlib import Path
import json
from dataclasses import asdict

from utils.logger import logger
from github_api.fetch_commits import get_commits_from_pr
from github_api.fetch_diffs import get_code_regions
from prompt.assemble import build_reflection_prompt
from llm.reflection_llm import generate_llm_reflection
from models.datatypes import ReflectionResponse, PromptResponse, CodeRegion, CommitInfo

REFLECTION_OUTPUT_PATH = Path("outputs/sample_issues2/reflections.jsonl")
EXPLANATION_INPUT_PATH = Path("outputs/sample_issues2/explanations_newprompt.jsonl")

@task
def load_explanations() -> list[PromptResponse]:
    responses = []
    with open(EXPLANATION_INPUT_PATH) as f:
        for line in f:
            data = json.loads(line)
            responses.append(PromptResponse(**data))
    return responses

@task
def save_reflection(response: ReflectionResponse):
    REFLECTION_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REFLECTION_OUTPUT_PATH, "a") as f:
        f.write(json.dumps(asdict(response)) + "\n")


@flow
def reflection_flow():
    explanation_responses = load_explanations()

    for response in explanation_responses:
        try:
            repo = response.repo
            issue_no = response.issue_no
            commits: list[CommitInfo] = get_commits_from_pr(repo, issue_no)
            code_regions: list[tuple[CodeRegion,CodeRegion]] = get_code_regions(repo, commits)
            topic = response.topic
            logger.info(f"Reflecting on {repo}#{issue_no}...")

            for (pre_region, post_region), region_data in zip(code_regions, response.code_regions):
                # Verify alignment
                assert pre_region.code.strip() == region_data["code"].strip(), \
                    f"Mismatch in code region alignment for {repo}#{issue_no}."

                original_explanation: str = region_data["explanation"]

                reflection_prompt = build_reflection_prompt(
                    original_explanation=original_explanation,
                    code_region=pre_region.code,
                    post_commit_code=post_region.code
                )

                reflection = generate_llm_reflection(reflection_prompt)

                save_reflection(ReflectionResponse(
                    repo=repo,
                    issue_no=issue_no,
                    topic=topic,
                    code_before=pre_region.code,
                    code_after=post_region.code,
                    original_explanation=original_explanation,
                    reflection_response=reflection
                ))

        except Exception as e:
            logger.error(f"Error processing reflection for {response.repo}#{response.issue_no}: {e}")

if __name__ == "__main__":
    reflection_flow()