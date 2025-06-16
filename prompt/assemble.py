from models.datatypes import CodeRegion
import json


def build_prompt(
    topic_name: str,
    summary: str,
    code_region: CodeRegion,
    extra: dict,
    instructions: str
) -> str:
    """
    Assemble a prompt for the LLM to explain code changes.

    Args:
        topic_name (str): Mapped topic from BERTopic.
        summary (str): The summary of the issue or PR.
        code_regions (list[CodeRegion]): Code context before changes.
        extra (dict): Optional metadata like commits, README, etc.
        instructions (str): Instruction string for the LLM.

    Returns:
        str: Formatted prompt string to send to the LLM.
    """

    prompt_dict = {
        "topic": topic_name,
        "summary": summary,
        "code_context": code_region.code,
        "readme": extra.get("readme", ""),
        "instructions": instructions
    }

    # You can return raw string or json.dumps(prompt_dict, indent=2)
    return json.dumps(prompt_dict, indent=2)
