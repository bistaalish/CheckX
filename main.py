from utils import cisco
import os
import json
from colorama import Fore, Style


def main():
    devices_folder = os.path.join(os.path.dirname(__file__), 'devices')

    for filename in os.listdir(devices_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(devices_folder, filename)
            with open(file_path, 'r') as file:
                device_data = json.load(file)
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
                            if optical_power:
                                # print(f"{Fore.GREEN}{port}:{device_data["ports"][port]}: {optical_power}{Style.RESET_ALL}")
                                if "N/A" not in optical_power:
                                    print(f"{Fore.GREEN}{port:<10} | {device_data['ports'][port]} | {optical_power}{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.RED}{port:<10} | {device_data['ports'][port]} | {optical_power}{Style.RESET_ALL}")
                        print("-"*55)

if __name__ == "__main__":
    main()