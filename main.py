from utils import cisco,huaweiOLT, bdcom
import os
import json
from colorama import Fore, Style
import csv
from datetime import datetime

Offline_Devices = []
NoPowerPort = []
OpticalPower = []

def checkDeviceStatus(hostname):
    """
    Check the device status based on the hostname.
    :param hostname: The hostname of the device.
    :return: True if the device is reachable, False otherwise.
    """
    try:
        response = os.system(f"ping -n 5 {hostname} > nul 2>&1")
        
        return response == 0
    except Exception as e:
        print(f"Error checking device status: {e}")
        return False

def main():
    devices_folder = os.path.join(os.path.dirname(__file__), 'devices')
    global Offline_Devices  # Declare that we are using the global variable 'Offline_Devices'
    global NoPowerPort  # Declare that we are using the global variable 'NoPowerPort'
    global OpticalPower  # Declare that we are using the global variable 'OpticalPower'

    for filename in os.listdir(devices_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(devices_folder, filename)
            with open(file_path, 'r') as file:
                device_data = json.load(file)
                Device_status = checkDeviceStatus(device_data["hostname"])
                if not Device_status:
                    print(f"{Fore.RED}Device {device_data['hostname']} is unreachable.{Style.RESET_ALL}")
                    Offline_Devices.append(device_data["hostname"])
                if device_data["vendor"].lower() == "bdcom":
                    tn = bdcom.TelnetSession(
                        device_data["hostname"],
                        device_data["username"],
                        device_data["password"]
                    )
                    if tn:
                        print("-"*55)
                        print(f"{Fore.YELLOW}Device: {device_data['name']}")
                        print(f"IP: {device_data['hostname']}{Style.RESET_ALL}")
                        print("-"*55)
                        # Print table header
                        print(f"{'PORT':<10} {'NAME':<25} {'OPTICAL POWER':<20}")
                        print("-" * 55)
                        for port in device_data["ports"]:
                            optical_power = bdcom.checkOpticalPower(port, tn)
                            portname = device_data["ports"][port]
                            deviceName = device_data["name"]
                            ip = device_data["hostname"]
                            OpticalPower.append([{"name":deviceName, "IP": ip, "port": port,"Desc":portname, "OpticalRx":optical_power}])
                            if optical_power:
                                if "N/A" not in optical_power:
                                    print(f"{Fore.GREEN}{port:<10} | {portname:<50} | {optical_power}{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.RED}{port:<10} | {portname:<50} | {optical_power}{Style.RESET_ALL}")
                        print("-"*55)
                if device_data["vendor"].lower() == "huaweiolt":
                    tn = huaweiOLT.TelnetSession(
                        device_data["hostname"],
                        device_data["username"],
                        device_data["password"]
                    )
                    if tn:
                        print("-"*55)
                        print(f"{Fore.YELLOW}Device: {device_data['name']}")
                        print(f"IP: {device_data['hostname']}{Style.RESET_ALL}")
                        print("-"*55)
                        # Print table header
                        print(f"{'PORT':<10} {'NAME':<25} {'OPTICAL POWER':<20}")
                        print("-" * 55)
                        for port in device_data["ports"]:
                            optical_power = huaweiOLT.checkOpticalPower(port, tn)
                            portname = device_data["ports"][port]
                            deviceName = device_data["name"]
                            ip = device_data["hostname"]
                            OpticalPower.append([{"name":deviceName, "IP": ip, "port": port,"Desc":portname, "OpticalRx":optical_power}])
                            if optical_power:
                                if "N/A" not in optical_power:
                                    
                                    print(f"{Fore.GREEN}{port:<10} | {portname:<50} | {optical_power:<8}{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.RED}{port:<10} | {portname:<50} | {optical_power:<8}{Style.RESET_ALL}")
                        print("-"*55)
                if device_data["vendor"].lower() == "cisco":
                    ssh_client = cisco.establish_ssh_session(
                        device_data["hostname"],
                        device_data["ssh_port"],
                        device_data["username"],
                        device_data["password"]
                    )
                    if ssh_client:
                        print("-"*55)
                        print(f"{Fore.YELLOW}Device: {device_data['name']}")
                        print(f"IP: {device_data['hostname']}{Style.RESET_ALL}")
                        print("-"*55)
                        # Print table header
                        print(f"{'PORT':<10} {'NAME':<25} {'OPTICAL POWER':<20}")
                        print("-" * 55)
                        for port in device_data["ports"]:
                            optical_power = cisco.checkOpticalPower(port, ssh_client)
                            portname = device_data["ports"][port]
                            deviceName = device_data["name"]
                            ip = device_data["hostname"]
                            OpticalPower.append([{"name":deviceName, "IP": ip, "port": port,"Desc":portname, "OpticalRx":optical_power}])
                            if optical_power:
                                # print(f"{Fore.GREEN}{port}:{device_data["ports"][port]}: {optical_power}{Style.RESET_ALL}")
                                if "N/A" not in optical_power:
                                    print(f"{Fore.GREEN}{port:<10} | {device_data['ports'][port]} | {optical_power}{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.RED}{port:<10} | {device_data['ports'][port]} | {optical_power}{Style.RESET_ALL}")
                        print("-"*55)
    if not Offline_Devices:
        print("The Offline list is empty.")
    else:
        # If Offline_Devices is not empty, create a CSV file with the details
        # Ensure the 'csv/offline' directory exists
        csv_folder = os.path.join(os.path.dirname(__file__), 'csv', 'offline')
        os.makedirs(csv_folder, exist_ok=True)

        # Create the CSV file with the current date and time as the filename
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_file_path = os.path.join(csv_folder, f"{current_time}.csv")

        # Write the Offline_Devices details to the CSV file
        with open(csv_file_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Hostname", "Status"])  # Write the header
            for device in Offline_Devices:
                csv_writer.writerow([device, "Offline"])

        print(f"Offline devices list has been saved to {csv_file_path}")
    
    if OpticalPower:
        # Ensure the 'csv/opticalpower' directory exists
        optical_csv_folder = os.path.join(os.path.dirname(__file__), 'csv', 'opticalpower')
        os.makedirs(optical_csv_folder, exist_ok=True)

        # Create the CSV file with the current date and time as the filename
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        optical_csv_file_path = os.path.join(optical_csv_folder, f"{current_time}.csv")

        # Write the OpticalPower details to the CSV file
        with open(optical_csv_file_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Device Name", "IP", "Port", "Description", "Optical Rx"])  # Write the header
            for device_data in OpticalPower:
                for data in device_data:
                    csv_writer.writerow([data["name"], data["IP"], data["port"], data["Desc"], data["OpticalRx"]])

        print(f"Optical power data has been saved to {optical_csv_file_path}")
                
if __name__ == "__main__":
    main()