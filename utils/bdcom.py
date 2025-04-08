import telnetlib
import time
import re

def TelnetSession(host,username,password):
    """Telnet into the OLT and execute basic commands, extracting MAC addresses."""
    try:
        tn = telnetlib.Telnet(host)

        # Read and provide Username
        tn.read_until(b"Username: ")
        tn.write(username.encode("ascii") + b"\n")

        # Read and provide Password
        tn.read_until(b"Password: ")
        tn.write(password.encode("ascii") + b"\n")

        # Wait for prompt
        time.sleep(1)
        tn.read_until(b">", timeout=5).decode("ascii")
        # Enter enable mode
        tn.write(b"enable\n")
        if host == "100.126.255.142":
            tn.write(b"fsupport#\n")
        tn.read_until(b"#", timeout=5)

        # Enter config mode
        tn.write(b"config\n")
        tn.read_until(b"_config#", timeout=5)
        return tn

    except Exception as e:
        print(f"Error during Telnet session: {e}")

def checkOpticalPower(interface,tn):
    """
    Check the optical power of the specified interface.
    :param interface: The interface to check.
    :return: The output of the command.
    """
    command = f"show interface {interface}  | include Rx"
    tn.write(command.encode('ascii') + b"\n")
    output = tn.read_until(b"_config#", timeout=5)
    match = re.search(r'RX power:([-\d.]+) dBM', output.decode('ascii'))
    if match:
        rx_power = float(match.group(1))
        return [str(rx_power)]
    else:
        return ["N/A"]

def checkPortStatus(interface,tn):
    """
    Check the status of the specified interface.
    :param interface: The interface to check.
    :return: The output of the command.
    """
    command = f"show interface brief | include {interface}"
    tn.write(command.encode('ascii') + b"\n")
    output = tn.read_until(b"_config#", timeout=5).decode('ascii')
    lines = output.strip().splitlines()
    # Get the second line (index 1)
    interface_line = lines[1]
    # Split the line by whitespace
    parts = interface_line.split()

    # Extract the 3rd column (index 2)
    status = parts[2]
    return status
    # match = re.search(r'(\S+)\s+(\S+)', output)
    # if match:
    #     return match.group(2)
    # else:
    #     return None