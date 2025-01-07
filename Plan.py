from dataclasses import dataclass, field
from typing import List
from PlanStep import PlanStep

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