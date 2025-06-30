from prefect import flow, task
from pathlib import Path
from flows.explanation_flow import explanation_flow
import json
from utils.logger import logger

SAMPLE_ID = "001"
EXPERIMENT_PATH = Path(f"experiments/exp_{SAMPLE_ID}") 

DATA_PATH = EXPERIMENT_PATH / "data.feather"
BASE_OUTPUT_PATH = EXPERIMENT_PATH / "base_output.jsonl"
AUGMENTED_OUTPUT_PATH = EXPERIMENT_PATH / "augmented_output.jsonl"
EXTRA_DATA_PATH = EXPERIMENT_PATH / "extra.txt"

@task
def get_extra_info(file_path: str) -> dict:
    """
    Load extra information from a .json or .txt file to pass into LLM prompts.

    Args:
        file_path (str): Path to the file (absolute or relative)

    Returns:
        dict: A dictionary of extra context
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Extra info file not found: {file_path}")

    if path.suffix == ".json":
        with open(path, "r") as f:
            return json.load(f)
    elif path.suffix == ".txt":
        with open(path, "r") as f:
            return {"notes": f.read()}
    else:
        raise ValueError("Unsupported file type. Use .json or .txt")

@flow
def experiment_flow():
    base_output = BASE_OUTPUT_PATH 
    extra_output = AUGMENTED_OUTPUT_PATH

    # Run baseline (README only)
    explanation_flow(
        data_path=DATA_PATH,
        output_path=base_output)
    
    extra_info = get_extra_info(EXTRA_DATA_PATH) 

    # Run with README + extra notes
    explanation_flow(
        data_path=DATA_PATH,
        output_path=extra_output,
        extra_info=extra_info
    )

if __name__ == "__main__":
    experiment_flow()
    logger.info(f"Experiment completed. Outputs saved to {BASE_OUTPUT_PATH} and {AUGMENTED_OUTPUT_PATH}.")