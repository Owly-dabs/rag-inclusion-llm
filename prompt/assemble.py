from models.datatypes import CodeRegion
import json


def build_explanation_prompt(
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
        code_region [CodeRegion]: Code context before changes.
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


def build_reflection_prompt(original_explanation: str, code_region: str, post_commit_code: str) -> list[dict]:
    return [
            {"role": "system", "content": "You are a code reviewer helping improve AI explanations."},
            {"role": "user", "content": f"The code region before the change:\n{code_region}"},
            {"role": "assistant", "content": original_explanation},
            {"role": "user", "content": (
                f"The actual code after the commit:\n{post_commit_code}\n\n"
                "Compare your previous suggestion with the actual change. Answer the following:\n"
                "1. What was missing or incorrect in your original suggestion?\n"
                "2. What additional information would have helped you make a more accurate suggestion?\n"
                "3. Categorize the missing context (e.g., intent, architectural, tests, surrounding code, etc.)"
            )}
        ]
    