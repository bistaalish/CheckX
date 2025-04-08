import paramiko
import re


def establish_ssh_session(hostname, port, username, password):
    """
    Establish an SSH session to the specified host.

    :param hostname: The hostname or IP address of the SSH server.
    :param port: The port number of the SSH server.
    :param username: The username for authentication.
    :param password: The password for authentication.
    :return: An active SSH client session.
    """
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=hostname, port=port, username=username, password=password,timeout=60)
        print(f"SSH connection established to {hostname}:{port}")
        return ssh_client
    except Exception as e:
        print(f"Failed to establish SSH connection: {e}")
        return None

def execute_command(ssh_client, command):
    """
    Execute a command on the SSH session and return the output.

    :param ssh_client: An active SSH client session.
    :param command: The command to execute.
    :return: The output of the command.
    """
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error executing command: {error}")
        return output
    except Exception as e:
        print(f"Failed to execute command: {e}")
        return None
def checkPortStatus(interface,ssh_client):
    """
    Check the status of the specified interface.

    :param interface: The interface to check.
    :return: The output of the command.
    """
    command = f"show interface {interface} status"
    # ssh_client = establish_ssh_session(hostname, port, username, password)
    if ssh_client:
        output = execute_command(ssh_client, command)
        # Match the part that comes after the name and before the vlan
        # Clean the output
        cleaned_lines = []
        for line in output.strip().splitlines():
            stripped = line.strip()
            if set(stripped) == {"-"}:
                continue  # skip delimiter lines
            if "Port" in stripped and "Status" in stripped:
                continue  # skip header line
            if stripped.startswith("Error: AAA authorization failed"):
                continue  # skip AAA error line
            cleaned_lines.append(line)

        # Output the cleaned data
        cleaned_output = "\n".join(cleaned_lines)
        parts = cleaned_output.split()
        status = parts[2]
        return status
    return None

def checkOpticalPower(interface,ssh_client):
    """
    Check the optical power of the specified interface.

    :param interface: The interface to check.
    :return: The output of the command.
    """
    command = f"show interface {interface} transceiver details | include Rx"
    # ssh_client = establish_ssh_session(hostname, port, username, password)
    if ssh_client:
        output = execute_command(ssh_client, command)
        matches = re.findall(r"Rx Power\s+(\S+)", output)
        return matches
    return None

        