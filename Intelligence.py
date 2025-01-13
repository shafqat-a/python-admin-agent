import os
import openai
import json
from abc import ABC, abstractmethod
import google.generativeai as genai

class LLMProvider(ABC):
    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        pass



class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key is None:
                raise ValueError("API key not found. Please provide it as an argument or set the GOOGLE_API_KEY environment variable.")
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

    def generate_content(self, prompt: str) -> str:
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"An error occurred: {e}")
            if "currently in 'experimental'" in str(e).lower():
                print("It appears you might not have access to the experimental Gemini 1.5 Flash model.")
                print("Please check your Google AI Studio account settings or contact support for access.")
            return None



class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
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