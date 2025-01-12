from asyncio import sleep
from dataclasses import asdict
import dataclasses
from typing import Any

from GeminiProvider import GeminiProvider
import paramiko
from PlanStep import PlanStep
from Plan import Plan
from StepCommand import StepCommand
import json
from dotenv import load_dotenv
import os


import json

# Load environment variables from the .env file in the parent directory
path_to_load_dotenv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
print (f"Loading environment variables from: {path_to_load_dotenv_file}")
load_dotenv(dotenv_path=path_to_load_dotenv_file)


SSH_SERVER = "192.168.0.197"
SSH_USERNAME = "shafqat"
SSH_KEY_PATH = "C:\\Users\\shafq\\.ssh\\id_rsa"
SUDO_PASSWORD = os.getenv("SUDO_PASSWORD")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

example_steps = """
{
    "prompt": "Install nginx if already not installed.",
    "prompt_clarification": "Install the Nginx web server if it's not already installed on the system.",
    "response": "Here is a plan to install Nginx web server if already not installed on the system:",
    "plan_steps": [
        {
            "step_number": 1,
            "is_done": false,
            "description": "Check if Nginx is already installed",
            "commands_to_exec": [
                {
                    "command": "which nginx",
                    "description": "Check if the nginx command is available in the system path."
                }
            ]
        },
        {
            "step_number": 2,
            "is_done": false,
            "description": "Install Nginx if not already installed",
            "commands_to_exec": [
                {
                    "command": "sudo apt-get update",
                    "description": "Update the package list."
                },
                {
                    "command": "sudo apt-get install nginx -y",
                    "description": "Install Nginx."
                }
            ]
        }
    ]
}
"""

example_steps2 = """{
  "prompt": "Install nginx if already not installed.",
  "prompt_clarification": "Install the Nginx web server if it's not already installed on the system.",
  "response": "Here is a plan to install Nginx web server if already not installed on the system:",
  "plan_steps": [
    {
      "step_number": 1,
      "is_done": false,
      "description": "Check if Nginx is already installed",
      "commands_to_exec": [
        {
          "command": "which nginx",
          "command_output": "/usr/sbin/nginx",
          "description": "Check if the nginx command is available in the system path."
        }
      ]
    },
    {
      "step_number": 2,
      "is_done": false,
      "description": "Install Nginx if not already installed",
      "commands_to_exec": [
        {
          "command": "sudo apt-get update",
          "command_output": "Hit:1 https://repo.steampowered.com/steam stable InRelease\nHit:2 https://brave-browser-apt-beta.s3.brave.com stable InRelease\nHit:3 https://brave-browser-apt-release.s3.brave.com stable InRelease\nHit:4 https://repo.nordvpn.com//deb/nordvpn/debian stable InRelease\nIgn:5 https://releases.warp.dev/linux/deb stable InRelease\nHit:6 https://releases.warp.dev/linux/deb stable Release\nHit:7 https://downloads.1password.com/linux/debian/amd64 stable InRelease\nHit:8 http://apt.pop-os.org/proprietary jammy InRelease\nHit:10 https://www.synaptics.com/sites/default/files/Ubuntu stable InRelease\nGet:11 https://download.wavebox.app/stable/linux/deb amd64/ InRelease [1,775 B]\nHit:12 http://apt.pop-os.org/release jammy InRelease\nHit:13 https://repository.mullvad.net/deb/stable jammy InRelease\nHit:14 http://apt.pop-os.org/ubuntu jammy InRelease\nHit:15 http://apt.pop-os.org/ubuntu jammy-security InRelease\nHit:16 http://apt.pop-os.org/ubuntu jammy-updates InRelease\nHit:17 http://apt.pop-os.org/ubuntu jammy-backports InRelease\nFetched 1,775 B in 4s (482 B/s)\nReading package lists...",
          "description": "Update the package list."
        },
        {
          "command": "sudo apt-get install nginx -y",
          "command_output": "Reading package lists...\nBuilding dependency tree...\nReading state information...\nnginx is already the newest version (1.18.0-6ubuntu14.5).\nThe following packages were automatically installed and are no longer required:\n  libsamplerate0:i386 libwpe-1.0-1 libwpebackend-fdo-1.0-1\n  nvidia-firmware-550-550.54.14\nUse 'sudo apt autoremove' to remove them.\n0 upgraded, 0 newly installed, 0 to remove and 472 not upgraded.",
          "description": "Install Nginx."
        }
      ]
    }
  ]
}"""

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

def extract_first_element_in_jsonstring_array (json_array: str) -> str:
     print("Extracting first element in json array:" + json_array)
     json_obj  = json.loads(json_array)[0]
     print("Extracted first element in json array:" )
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
        commands = [StepCommand(command=cmd["command"], description=cmd["description"], command_output="") for cmd in step_data["commands_to_exec"]]
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


def open_ssh_connection(address, username, ssh_key_path):
    """
    Opens an SSH connection to the specified address using the provided username and SSH key.

    :param address: The IP address or hostname of the remote server.
    :param username: The username to use for the SSH connection.
    :param ssh_key_path: The path to the SSH private key file.
    :return: An SSH client object.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(ssh_key_path)

        # Connect to the remote server
        ssh.connect(address, username=username, pkey=private_key)
        print(f"SSH connection established to {address} as {username}.")
        return ssh
    except Exception as e:
        print(f"Failed to establish SSH connection: {e}")
        return None


def execute_command(ssh, command, sudo_password=None)-> str:
    """
    Executes a command on the remote server using the established SSH connection.
    If the command requires sudo, it automatically provides the sudo password using the `echo "password" | sudo -S` scheme.

    :param ssh: The SSH client object.
    :param command: The command to execute on the remote server.
    :param sudo_password: The sudo password (if required).
    :return: The output of the command.
    """
    try:
        # Check if the command requires sudo
        if command.strip().startswith("sudo"):
            if not sudo_password:
                raise ValueError("Sudo password is required for sudo commands.")

            # Modify the command to use `echo "password" | sudo -S`
            modified_command = f"echo '{sudo_password}' | sudo -S {command[len('sudo '):]}"
        else:
            # Use the original command if it doesn't require sudo
            modified_command = command

        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(modified_command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        if error:
            print(f"Error: {error}")
        return output.strip()
    except Exception as e:
        print(f"Failed to execute command: {e}")
        return None


def close_ssh_connection(ssh):
    """
    Closes the SSH connection.

    :param ssh: The SSH client object.
    """
    if ssh:
        ssh.close()
        print("SSH connection closed.")

def process_steps(plan: Plan, provider :GeminiProvider):

    ssh_client = open_ssh_connection(SSH_SERVER, SSH_USERNAME, SSH_KEY_PATH)
    for step in plan.plan_steps:
        if (step.is_done == False):
            all_output = ""
            for command in step.commands_to_exec:
                print(f"Executing command: {command.command}")
                command_output  = execute_command(ssh_client, command.command, SUDO_PASSWORD)
                print(command_output)
                command.command_output = command_output
                sleep(1)

            step_prompt = prepare_prompt_for_step(plan, step, provider)
            print(step_prompt)
            step_response = provider.generate_content(step_prompt)
            print(step_response)
    close_ssh_connection(ssh_client)


def prepare_prompt_for_step(plan : Plan, step : PlanStep, provider : GeminiProvider) -> str:

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




def get_steps_as_string(steps_plan : Plan) -> str:
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


def run_test():


    primary_prompt = "Install nginx if already not installed."
    secondary_prompt = prepare_prompt_from_primary(primary_prompt)

    print("Generating plan to complete the task ... ")
    #Choose the provider
    provider = GeminiProvider(api_key=GOOGLE_API_KEY)  # or OpenAIProvider(api_key="your_openai_api_key_here")
    #generated_text = provider.generate_content(secondary_prompt)
    #print(generated_text)
    generated_text = example_steps

    main_plan =  load_plan_from_string( generated_text)
    print_dataclass(main_plan,4)

    print("Generated plan:" + get_steps_as_string(main_plan))

    process_steps(main_plan, provider)

    planstring = plan_to_json_string(main_plan)
    print(planstring)



if __name__ == "__main__":

    run_test()
    exit(0)


    sshs_client = open_ssh_connection(SSH_SERVER, SSH_USERNAME,SSH_KEY_PATH)
    command_output = execute_command(sshs_client,"sudo ls /",SUDO_PASSWORD )
    print (command_output)
    close_ssh_connection(sshs_client)

