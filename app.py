from asyncio import sleep

import google.generativeai as genai
import os
import json
from GeminiProvider import GeminiProvider
import paramiko
import os

example_steps: str = """
  {
    "prompt": "Install nginx if already not installed. Also point www.google.com content to /abc/",
    "prompt_clarification": "The task is to install nginx if not already installed and configure it to serve the content of www.google.com from the /abc/ directory on the server.",
    "response": "Sure, here is a detailed plan to accomplish this task:",
    "plan_steps": [
      {
        "step_number": 1,
        "is_done": false,
        "description": "Check if nginx is already installed.",
        "commands_to_exec": [
          "which nginx"
        ]
      },
      {
        "step_number": 2,
        "is_done": false,
        "description": "If nginx is not installed, install it.",
        "commands_to_exec": [
          "sudo apt-get update",
          "sudo apt-get install nginx"
        ]
      },
      {
        "step_number": 3,
        "is_done": false,
        "description": "Create a new server block for www.google.com.",
        "commands_to_exec": [
          "sudo touch /etc/nginx/sites-available/www.google.com"
        ]
      },
      {
        "step_number": 4,
        "is_done": false,
        "description": "Add the following content to the new server block file.",
        "commands_to_exec": [
          "sudo echo 'server { \\n \\tlisten 80; \\n \\tlisten [::]:80; \\n \\t server_name www.google.com; \\n \\t root /abc/; \\n \\t location / { \\n \\t \\t try_files $uri $uri/ =404; \\n \\t } \\n}' > /etc/nginx/sites-available/www.google.com"
        ]
      },
      {
        "step_number": 5,
        "is_done": false,
        "description": "Enable the new server block.",
        "commands_to_exec": [
          "sudo ln -s /etc/nginx/sites-available/www.google.com /etc/nginx/sites-enabled/www.google.com"
        ]
      },
      {
        "step_number": 6,
        "is_done": false,
        "description": "Restart nginx.",
        "commands_to_exec": [
          "sudo systemctl restart nginx"
        ]
      },
      {
        "step_number": 7,
        "is_done": false,
        "description": "Test the new configuration.",
        "commands_to_exec": [
          "curl http://www.google.com"
        ]
      }
    ]
  }
"""

GEMINI_API_KEY = ""
SSH_SERVER = "localhost"
SSH_USERNAME = "shafqat"
SSH_KEY_PATH = "/Users/shafqat/.ssh/id_rsa"
SUDO_PASSWORD = "whoareu"


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


def prepare_prompt_for_step(stepsJson: str) -> str:
    data = json.loads(example_steps)
    primary_prompt = data['prompt']

    return f"""
           You are a helpful 20 year experienced linux system administrator.

           The user has provided the following task:
           '{primary_prompt}'

           Based on the task, you have generated a json defining the steps to complete the task that looks like this:
           '{stepsJson}'

           All the steps that have been done are marked "is_done": "true"



           """
    pass




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

    print("Plan complete. Here are the steps to complete the task:")
    print(stepsJson)
    data = json.loads(stepsJson)

    for step in data['plan_steps']:
        description = step['description']
        commands = step['commands_to_exec']

        print(f"Description: {description}")
        print("Commands:")
        for command in commands:
            print(f"  - {command}")
        print("---")
    pass

def print_steps(stepsJson: str):

    pass


def run_test():


    primary_prompt = "Install nginx if already not installed. Also point www.google.com content to /abc/"
    secondary_prompt = prepare_prompt_from_primary(primary_prompt)

    print("Generating plan to complete the task ... ")
    # Choose the provider
    #provider = GeminiProvider(api_key=GEMINI_API_KEY)  # or OpenAIProvider(api_key="your_openai_api_key_here")
    #generated_text = provider.generate_content(secondary_prompt)
    process_steps(example_steps)



if __name__ == "__main__":

    run_test()
    exit(0);

    data = json.loads(example_steps)
    for step in data['plan_steps']:
        description = step['description']
        commands = step['commands_to_exec']

        print(f"Description: {description}")
        print("Commands:")
        for command in commands:
            print(f"  - {command}")
        print("---")

exit(0)

ssh_client = open_ssh_connection(SSH_SERVER, SSH_USERNAME,SSH_KEY_PATH)
output = execute_command(ssh_client,"sudo ls /",SUDO_PASSWORD )
print (output)
close_ssh_connection(ssh_client)

