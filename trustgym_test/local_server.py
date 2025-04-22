import requests
import subprocess
import time
import os

# Server addresses
SERVERS = {
    "server_341": "http://localhost:80",
    "server_343": "http://localhost:80",
    "server_804": "http://localhost:80"
}

# Full paths to each server script
SERVER_SCRIPTS = {
    "server_341": r"C:\Users\Chaima\Desktop\server1\server\DS-K1T341CMF\server_341.py",
    "server_343": r"C:\Users\Chaima\Desktop\server1\server\DS-K1T343EFX\server_343.py",
    "server_804": r"C:\Users\Chaima\Desktop\server1\server\DS-K1T804AEF\server_804.py"
}

def check_server_is_running(url):
    try:
        requests.get(url, timeout=2)
        return True
    except requests.ConnectionError:
        return False

def start_server_script(server_key):
    script_path = SERVER_SCRIPTS[server_key]

    if not os.path.exists(script_path):
        print(f"Error: The script {script_path} does not exist.")
        return

    script_dir = os.path.dirname(script_path)

    try:
        subprocess.Popen(
            ['python', script_path],
            cwd=script_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE  # Open in a new console window
        )
        print(f"Starting {server_key} ({script_path})...")
        time.sleep(5)  # Give it time to start
    except Exception as e:
        print(f"Failed to start {server_key}: {e}")

def run_script(server_key, script_name):
    url = f"{SERVERS[server_key]}/run-script"
    payload = {"script_name": script_name}
    response = requests.post(url, json=payload)
    return response.json()

def run_multiple_scripts(server_key, script_list):
    url = f"{SERVERS[server_key]}/run-multiple-scripts"
    payload = {"script_names": script_list}
    response = requests.post(url, json=payload)
    return response.json()

def list_available_scripts(server_key):
    url = f"{SERVERS[server_key]}/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("available_scripts", [])
    except requests.ConnectionError:
        return []
    return []

def main():
    while True:
        print("\nChoose a server:")
        print("1. server_341")
        print("2. server_343")
        print("3. server_804")
        print("4. Exit")

        choice = input("Enter the number of the server you want to use: ")

        if choice == "4":
            print("Exiting...")
            break

        server_map = {
            "1": "server_341",
            "2": "server_343",
            "3": "server_804"
        }

        if choice not in server_map:
            print("Invalid choice, try again.")
            continue

        server_key = server_map[choice]

        if not check_server_is_running(SERVERS[server_key]):
            print(f"{server_key} is not running. Attempting to start it...")
            start_server_script(server_key)

            if not check_server_is_running(SERVERS[server_key]):
                print(f"Still unable to connect to {server_key}. Aborting.")
                continue

        available_scripts = list_available_scripts(server_key)
        if not available_scripts:
            print(f"No scripts available on {server_key}.")
            continue

        print(f"\nAvailable scripts on {server_key}:")
        for idx, script in enumerate(available_scripts, 1):
            print(f"{idx}. {script}")

        script_choice = input(f"Enter the number of the script to run on {server_key}: ")

        try:
            script_name = available_scripts[int(script_choice) - 1]
        except (ValueError, IndexError):
            print("Invalid script choice, try again.")
            continue

        result = run_script(server_key, script_name)
        print(f"\nResult: {result}")

if __name__ == "__main__":
    main()
