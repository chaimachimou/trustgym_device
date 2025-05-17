from flask import Flask, jsonify, request
import subprocess
import threading
import os

app = Flask(__name__)

# List of available scripts (these should match your actual script names)
available_scripts = [
    "tst.py",
    "add_per_341.py",
    "del_per_341.py",
    "add_fp_341.py",
    "event_341.py",
    "face.py"
    "trf.py"
    "search_person.py"
    "add_prv_341.py"
]


# Function to run the Python script
def run_program(script_name):
    try:
        # Check if the script is in the list of available scripts
        if script_name not in available_scripts:
            return f"Error: Script '{script_name}' is not available!"
        
        # Ensure the script exists in the current directory (or adjust the path as needed)
        if not os.path.exists(script_name):
            return f"Error: Script '{script_name}' does not exist!"

        # Run the script using subprocess
        subprocess.run(['python', script_name], check=True)
        print(f"Script '{script_name}' executed successfully.")
    except subprocess.CalledProcessError as e:
        return f"Error running '{script_name}': {e}"

@app.route('/')
def home():
    return jsonify({"available_scripts": available_scripts})  # Modified this line

# Endpoint to trigger a single script by name
@app.route('/run-script', methods=['POST'])
def run_script_endpoint():
    data = request.get_json()
    script_name = data.get('script_name')

    if not script_name:
        return jsonify({"error": "No script name provided!"}), 400

    # Check if the script name is valid
    if script_name not in available_scripts:
        return jsonify({"error": f"Script '{script_name}' not found in available scripts!"}), 404

    # Run the specified script in a background thread
    thread = threading.Thread(target=run_program, args=(script_name,))
    thread.start()

    return jsonify({"message": f"Script '{script_name}' is running in the background!"})

# Endpoint to trigger multiple scripts 
@app.route('/run-multiple-scripts', methods=['POST'])
def run_multiple_scripts_endpoint():
    data = request.get_json()
    script_names = data.get('script_names')

    if not script_names or not isinstance(script_names, list):
        return jsonify({"error": "Please provide a list of script names!"}), 400

    # Check if all provided scripts are valid
    invalid_scripts = [script for script in script_names if script not in available_scripts]
    if invalid_scripts:
        return jsonify({"error": f"Invalid scripts: {', '.join(invalid_scripts)}"}), 404

    # Run each script in a separate background thread 
    threads = []
    for script_name in script_names:
        thread = threading.Thread(target=run_program, args=(script_name,))
        thread.start()
        threads.append(thread)

    # Optionally, wait for all threads to finish
    for thread in threads:
        thread.join()

    return jsonify({"message": "All valid scripts are running in the background!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
