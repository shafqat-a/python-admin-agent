from dataclasses import dataclass, field
from typing import List
from StepCommand import StepCommand

@dataclass
class PlanStep:

    def __init__(self, step_number: int, is_done: bool, description: str, commands_to_exec: List[StepCommand] = []):
        self.step_number = step_number
        self.is_done = is_done
        self.description = description
        self.commands_to_exec = commands_to_exec
        pass

    step_number: int
    is_done: bool
    description: str
    commands_to_exec: List[StepCommand] = field(default_factory=list)