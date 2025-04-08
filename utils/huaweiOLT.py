import telnetlib
import time
import re


def TelnetSession(hostname,username,password):
    try:
        port = 23
        tn = telnetlib.Telnet(hostname, port,timeout=60)
        tn.read_until(b">>User name:", timeout=5).decode('ascii').strip()
        tn.write(username.encode('ascii') + b"\n")
        tn.read_until(b">>User password:", timeout=5)
        tn.write(password.encode('ascii') + b"\n")
        # time.sleep(1)
        output = tn.read_until(b">>", timeout=5).decode('ascii').strip()
        if "Username or password invalid." in output:
            raise ValueError("Invalid Username or password")
        
        pattern = r'\bReenter times have reached the upper limit\.'
        if re.search(pattern, output):
            raise Exception("User already logged in")
        else:
            tn.write(b"enable\n")
            tn.write(b"config\n")
            return tn
    except Exception as e:
        print(f"Failed to connect to {hostname}: {str(e)}")
        return None

def checkOpticalPower(interface,tn):
    """
    Check the optical power of the specified interface.
    :param interface: The interface to check.
    :return: The output of the command.
    """
    fs, p = interface.rsplit("/",1)
    Interfacecommand = "interface " + fs + "\n"
    DDMCommand = "display port ddm-info " + p + "\n"
    tn.write(Interfacecommand.encode('ascii') + b"\n")
    tn.write(DDMCommand.encode('ascii') + b"\n")
    tn.write(b"quit\n")
    time.sleep(1)
    output = tn.read_until(b">>", timeout=5).decode('ascii').strip()
    if "Failure: The optic module of port is absence, can not do such operation." in output:
        return "N/A"
    match = re.search(r'RX power\(dBm\)\s+:\s+(-?\d+\.\d+)', output)
    if match:
        rx_power = float(match.group(1))
        if rx_power <= -40:
            rx_power = "N/A"
            return [rx_power]
        return [str(rx_power)]
    else:
        return None


def checkOpticalState(interface,tn):
    """
    Check the optical state of the specified interface.
    :param interface: The interface to check.
    :return: The output of the command.
    """
    fs, p = interface.rsplit("/",1)
    Interfacecommand = "interface " + fs + "\n"
    OpticalStateCommand = "display port state " + p + "\n"
    tn.write(Interfacecommand.encode('ascii') + b"\n")
    tn.write(OpticalStateCommand.encode('ascii') + b"\n")
    tn.write(b"quit\n")
    time.sleep(1)
    output = tn.read_until(b">>", timeout=5).decode('ascii').strip()
    # Extract the line that contains "Ethernet port is"
    for line in output.splitlines():
        if "Ethernet port is" in line:
            status = line.strip().split()[-1]  # get the last word (online/offline)
            return status
            break
    return None