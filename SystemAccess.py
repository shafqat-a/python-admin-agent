import paramiko


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
