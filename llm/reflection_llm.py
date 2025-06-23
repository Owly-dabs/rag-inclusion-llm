import os
from openai import OpenAI
from dotenv import load_dotenv

from utils.logger import logger

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def generate_llm_reflection(messages: list[dict], model: str = "gpt-4o", temperature: float = 0.2) -> str:
    """
    Use OpenAI's ChatCompletion API with structured message input.

    Args:
        messages (list[dict]): A list of messages in Chat format (with roles: user/assistant/system).
        model (str): Model to use.
        temperature (float): Sampling temperature.

    Returns:
        str: The response content from the assistant.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return ""
