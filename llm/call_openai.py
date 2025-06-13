import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def generate_llm_explanation(prompt: str, model: str = "gpt-4o", temperature: float = 0.2) -> str:
    """
    Send the prompt to OpenAI's ChatCompletion API and return the model's explanation.
    
    Args:
        prompt (str): The prompt string (structured JSON or text) to send to the LLM.
        model (str): The model name to use (default: "gpt-4").
        temperature (float): Sampling temperature for creativity control.

    Returns:
        str: The LLM's response content.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            #max_tokens=1024
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return ""
