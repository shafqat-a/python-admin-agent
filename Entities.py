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

@dataclass
class Plan:

    def __init__(self, prompt: str, prompt_clarification: str, response: str, plan_steps: List[PlanStep] = []):
        self.prompt = prompt
        self.prompt_clarification = prompt_clarification
        self.response = response
        self.plan_steps = plan_steps
        pass

    prompt: str
    prompt_clarification: str
    response: str
    plan_steps: List[PlanStep] = field(default_factory=list)