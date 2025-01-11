from asyncio import sleep
from dataclasses import asdict

import google.generativeai as genai
import os
import json
from GeminiProvider import GeminiProvider
import paramiko
import os
from PlanStep import PlanStep
from Plan import Plan
import json


example_steps: str = """
 {
    "prompt": "Install nginx if already not installed.",
    "prompt_clarification": "The user wants to install nginx if it is not already installed on the system.",
    "response": "Here is a detailed plan to accomplish this task:",
    "plan_steps": [
      {
        "step_number": 1,
        "is_done": "false",
        "description": "Check if nginx is already installed.",
        "commands_to_exec": [
          "command -v nginx"
        ]
      },
      {
        "step_number": 2,
        "is_done": "false",
        "description": "If nginx is not installed, install it.",
        "commands_to_exec": [
          "apt-get update",
          "apt-get install nginx -y"
        ]
      },
      {
        "step_number": 3,
        "is_done": "false",
        "description": "Start nginx service and check status",
        "commands_to_exec": [
          "systemctl start nginx",
          "systemctl status nginx"
        ]
      }
    ]
  }
"""

GOOGLE_API_KEY = ""
SSH_SERVER = "192.168.0.197"
SSH_USERNAME = "shafqat"
SSH_KEY_PATH = "C:\\Users\\shafq\\.ssh\\id_rsa"
SUDO_PASSWORD = ""


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
                       "commands_to_exec": ["command1", "command2", ...]
                   }}
               ]
           }}

           """
    pass

def load_plan_from_string(json_string: str) -> Plan:
    """
    Load JSON data from a string and convert it into an InstallationPlan object.
    """
    data = json.loads(json_string)  # Convert JSON string to a Python dictionary

    # Build PlanStep objects
    steps = [PlanStep(**step_data) for step_data in data["plan_steps"]]

    # Create and return an InstallationPlan object
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


def execute_command(ssh, command, sudo_password=None):
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
        return output
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

def process_steps(stepsJson: str):

    ssh_client = open_ssh_connection(SSH_SERVER, SSH_USERNAME, SSH_KEY_PATH)
    print("Plan complete. Here are the steps to complete the task:")
    print(stepsJson)
    plan = load_plan_from_string(stepsJson)
    for step in plan.plan_steps:
        if (step.is_done == False):
            all_output = ""
            for command in step.commands_to_exec:
                output = execute_command(ssh_client, command, SUDO_PASSWORD)
                all_output += output
                print(f"Output: {output}")
                sleep(1)



def prepare_prompt_for_step(plan : Plan) -> str:
    data = json.loads(example_steps)
    primary_prompt = data['prompt']
    steps_string = get_steps_as_string(p)

    return f"""
           You are a helpful 20 year experienced linux system administrator.

           The user has provided the following task:
           '{primary_prompt}'

           Based on the task, you have generated a detailed plan to accomplish this task. That looks like this
           '{tasks}'

           All the steps that have been done are marked "is_done": "true"



           """
    pass




def get_steps_as_string(steps_plan : Plan) -> str:

    string_var = ""
    for step in steps_plan.plan_steps:
        string_var += f"Description: {step.description}"
        if step['is_done'] == "true":
            string_var += " ... already done"
        else :
            string_var += ""
        steps_plan+= "\r\n"
    return string_var
    pass


def run_test():


    primary_prompt = "Install nginx if already not installed."
    secondary_prompt = prepare_prompt_from_primary(primary_prompt)

    print("Generating plan to complete the task ... ")
    # Choose the provider
    #provider = GeminiProvider(api_key=GOOGLE_API_KEY)  # or OpenAIProvider(api_key="your_openai_api_key_here")
    #generated_text = provider.generate_content(secondary_prompt)

    action_plan = example_steps
    process_steps(action_plan)



if __name__ == "__main__":

    #run_test()
    #exit(0);


    ssh_client = open_ssh_connection(SSH_SERVER, SSH_USERNAME,SSH_KEY_PATH)
    output = execute_command(ssh_client,"sudo ls /",SUDO_PASSWORD )
    print (output)
    close_ssh_connection(ssh_client)

