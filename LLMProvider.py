import os
import json
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        pass