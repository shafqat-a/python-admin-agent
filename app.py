from asyncio import sleep
from dataclasses import dataclass, asdict
from typing import Any
from dotenv import load_dotenv
import os
import json

from Core import prepare_prompt_from_primary, load_plan_from_string, print_dataclass, get_steps_as_string, \
    process_steps, plan_to_json_string
from Intelligence import GeminiProvider

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

