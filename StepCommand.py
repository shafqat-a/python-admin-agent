from dataclasses import dataclass, field
from typing import List

@dataclass
class StepCommand:

    def __init__(self, command: str, command_output: str, description: str = None):
        self.command = command
        self.command_output = command_output
        self.description = description
        pass

    command: str
    command_output: str
    description: str = None
