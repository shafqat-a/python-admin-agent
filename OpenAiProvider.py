import os
import openai
from LLMProvider import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("API key not found. Please provide it as an argument or set the OPENAI_API_KEY environment variable.")
        self.api_key = api_key
        openai.api_key = self.api_key

    def generate_content(self, prompt: str) -> str:
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",  # or any other model you prefer
                prompt=prompt,
                max_tokens=150
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None