from flask import Flask, request, jsonify
from flasgger import Swagger
import subprocess
import os

app = Flask(__name__)
swagger = Swagger(app)

# List of available scripts
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

@app.route('/')
def home():
    return jsonify({"available_scripts": available_scripts})

@app.route('/run-script', methods=['POST'])
def run_script_endpoint():
    """
    Run a single script and return its output.
    ---
    parameters:
      - in: body
        name: script_name
        required: true
        schema:
          type: object
          required:
            - script_name
          properties:
            script_name:
              type: string
              example: tst.py
    responses:
      200:
        description: Script executed
        schema:
          type: object
          properties:
            message:
              type: string
            stdout:
              type: string
            stderr:
              type: string
      400:
        description: Missing or invalid script name
      404:
        description: Script not found
    """
    data = request.get_json()
    script_name = data.get('script_name')

    if not script_name:
        return jsonify({"error": "No script name provided!"}), 400

    if script_name not in available_scripts:
        return jsonify({"error": f"Script '{script_name}' not found in available scripts!"}), 404

    if not os.path.exists(script_name):
        return jsonify({"error": f"Script file '{script_name}' does not exist on disk!"}), 404

    try:
        result = subprocess.run(
            ['python', script_name],
            capture_output=True,
            text=True,
            check=False
        )

        return jsonify({
            "message": f"Script '{script_name}' executed.",
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/run-multiple-scripts', methods=['POST'])
def run_multiple_scripts_endpoint():
    """
    Run multiple scripts and return their outputs.
    ---
    parameters:
      - in: body
        name: script_names
        required: true
        schema:
          type: object
          required:
            - script_names
          properties:
            script_names:
              type: array
              items:
                type: string
              example: ["tst.py", "adding.py"]
    responses:
      200:
        description: Multiple scripts executed
        schema:
          type: object
          properties:
            results:
              type: array
              items:
                type: object
                properties:
                  script_name:
                    type: string
                  stdout:
                    type: string
                  stderr:
                    type: string
      400:
        description: Bad request
      404:
        description: One or more scripts not found
    """
    data = request.get_json()
    script_names = data.get('script_names')

    if not script_names or not isinstance(script_names, list):
        return jsonify({"error": "Please provide a list of script names!"}), 400

    invalid_scripts = [s for s in script_names if s not in available_scripts]
    if invalid_scripts:
        return jsonify({"error": f"Invalid scripts: {', '.join(invalid_scripts)}"}), 404

    results = []

    for script_name in script_names:
        if not os.path.exists(script_name):
            results.append({
                "script_name": script_name,
                "stdout": "",
                "stderr": f"Script file '{script_name}' not found."
            })
            continue

        result = subprocess.run(
            ['python', script_name],
            capture_output=True,
            text=True,
            check=False
        )
        results.append({
            "script_name": script_name,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
 
    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
