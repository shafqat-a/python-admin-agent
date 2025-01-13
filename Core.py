import dataclasses
import json
from typing import Any

import SystemAccess
from Entities import Plan, StepCommand, PlanStep
from Intelligence import GeminiProvider


def prepare_prompt_from_primary(primary_prompt: str) -> str:
    return f"""
           You are a helpful 20 year experienced linux system administrator.

           The user has provided the following task:
           '{primary_prompt}'

           Generate a detailed plan to accomplish this task. For each step in the plan:
           1. Provide a concise description.
           2. List the specific shell commands to execute to achieve the step.
           3. Remember you are connected via ssh, do not use interactive command the require input - like vim, nano, etc.
           rather you can use echo "text" > to output to a file or >> to append to a file or use other commands to replace 
           lines in a file. But cannot type in interactively

           Format the output as a JSON list of steps. Each step should be a JSON object with the following structure:
           {{
               "prompt": "The exact prompt that was given to you",
               "prompt_clarification": "What you(LLM) understood from the prompt",
               "response": "Response text from LLM if you have anything to say",
               "plan_steps" :[
                   {{
                       "step_number": 1,
                       "is_done": "false"
                       "description": "Description of the step",
                       "commands_to_exec": [{{"command":"command 1", "description":"doing command 1 ..."}},{{"command":"command 2", "description":"doing the work of ..."}} , ...]
                   }}
               ]
           }}

           Only output the json object as shown above. Do not include any other text in the output or do not put it in json array.

           """
    pass


def remove_first_line_from_string(json_string: str) -> str:
    print("Removing first line from string" + json_string)
    ret_string = json_string.split('\n', 1)[1]
    print("Returning:" + ret_string)
    return ret_string


def extract_first_element_in_jsonstring_array(json_array: str) -> str:
    print("Extracting first element in json array:" + json_array)
    json_obj = json.loads(json_array)[0]
    print("Extracted first element in json array:")
    print(json_obj)
    return json_obj


def load_plan_from_string(json_string: str) -> Plan:
    """
    Load JSON data from a string and convert it into a Plan object.
    """
    data = json.loads(json_string)  # Convert JSON string to a Python dictionary

    # Build PlanStep objects with StepCommand objects
    steps = []
    for step_data in data["plan_steps"]:
        commands = [StepCommand(command=cmd["command"], description=cmd["description"], command_output="") for cmd in
                    step_data["commands_to_exec"]]
        step_data_copy = step_data.copy()
        step_data_copy["commands_to_exec"] = commands
        step = PlanStep(**step_data_copy)
        steps.append(step)

    # Create and return a Plan object
    return Plan(
        prompt=data["prompt"],
        prompt_clarification=data["prompt_clarification"],
        response=data["response"],
        plan_steps=steps
    )


def plan_to_json_string(plan: Plan) -> str:
    """
    Convert an InstallationPlan object into a JSON string.
    """
    # Convert the data class (and nested classes) into a dictionary
    plan_dict = asdict(plan)
    # Dump the dictionary as a JSON string
    return json.dumps(plan_dict, indent=2, ensure_ascii=False)


def process_steps(plan: Plan, provider: GeminiProvider):
    ssh_client = SystemAccess.open_ssh_connection(SSH_SERVER, SSH_USERNAME, SSH_KEY_PATH)
    for step in plan.plan_steps:
        if (step.is_done == False):
            all_output = ""
            for command in step.commands_to_exec:
                print(f"Executing command: {command.command}")
                command_output = execute_command(ssh_client, command.command, SUDO_PASSWORD)
                print(command_output)
                command.command_output = command_output
                sleep(1)

            step_prompt = prepare_prompt_for_step(plan, step, provider)
            print(step_prompt)
            step_response = provider.generate_content(step_prompt)
            print(step_response)
    close_ssh_connection(ssh_client)


def prepare_prompt_for_step(plan: Plan, step: PlanStep, provider: GeminiProvider) -> str:
    steps_string = get_steps_as_string(plan)
    json_steps = plan_to_json_string(plan)
    command_output_string = ""
    for cmd in step.commands_to_exec:
        command_output_string += f"{cmd.command}:\r\n=================================\r\n{cmd.command_output}\r\n"
    return f"""
You are a helpful 20 year experienced linux system administrator.

The user has provided the following task: '{plan.prompt}'

Based on the task, you have generated a detailed plan to accomplish this task. That looks like this
'{steps_string}'

Now we are going to proceed with step {step.step_number} which is: '{step.description}'. The commands
were executed and their output are as follows:
{command_output_string}

Based on the execution and output of the commands of the plan the following json stores the status of the steps.
JSON
----
{json_steps}
-
If you think the step is completed the return true in JSON reply else return false and what command to correct and
complete the step. Please strictly use the JSON format shown below to reply.

REPLY_JSON
----------
{{
    "success": False,
    "corrective_action": "command to correct and complete the step based on output of the commands",
}}

"""
    pass


def get_steps_as_string(steps_plan: Plan) -> str:
    string_var = ""
    for step in steps_plan.plan_steps:
        step_no = step.step_number
        string_var += f"{step_no}. {step.description}"
        if getattr(step, 'is_done', None) == "true":
            string_var += " ... [completed]"
        else:
            string_var += ""
        string_var += "\r\n"
    return string_var


def print_dataclass(obj: Any, indent: int = 0):
    if not dataclasses.is_dataclass(obj):
        raise ValueError("print_dataclass should be called with a dataclass instance")

    indent_str = ' ' * indent
    for field in dataclasses.fields(obj):
        value = getattr(obj, field.name)
        if dataclasses.is_dataclass(value):
            print(f"{indent_str}{field.name}:")
            print_dataclass(value, indent + 2)
        elif isinstance(value, list):
            print(f"{indent_str}{field.name}:")
            for item in value:
                if dataclasses.is_dataclass(item):
                    print_dataclass(item, indent + 2)
                else:
                    print(f"{indent_str}  - {item}")
        else:
            print(f"{indent_str}{field.name}: {value}")

