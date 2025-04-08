from flask import Flask, jsonify, request
from flask_cors import CORS  # add this import
import requests
import json

app = Flask(__name__)
CORS(app)  # enable CORS for all routes

agent_manager_url = "http://ai_agents:6000"
json_db_url = "http://json_db:7000"


def submit_task(jsonData):
    """Submit a task to the agent server."""

    response = requests.post(
        f"{agent_manager_url}/task", json=jsonData)
    # response.raise_for_status()
    return response.json()


@app.route('/api', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Python backend!"})


@app.route('/status', methods=['GET'])
def status():
    response = requests.get(f"{agent_manager_url}/status")
    # response.raise_for_status()
    return response.json()


@app.route('/processtask', methods=['POST'])
def process_task():
    data = request.get_json()
    taskId = data.get('taskId')
    if not taskId:
        return jsonify({'error': 'No task provided'}), 400

    result = submit_task(data)
    return jsonify({'taskId': taskId, 'status': 'success', 'result': result})


@app.route('/create-image-description', methods=['POST'])
def create_image_description():
    """
    Expects a multipart/form-data request with:
      - 'file': The file to be uploaded.
      - 'description': A JSON string containing the other ImageDescription fields.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Get ImageDescription data from the form field "description"
    description_str = request.form.get("description")
    if not description_str:
        return jsonify({"error": "No image description data provided"}), 400

    try:
        description_data = json.loads(description_str)
    except Exception as e:
        return jsonify({"error": "Invalid JSON in description field", "details": str(e)}), 400

    # Override name
    file.filename = description_data.get("filename", file.filename)

    # Upload file to the json_db container and get the file URI
    upload_resp = requests.post(
        f"{json_db_url}/upload",
        files={"file": (file.filename, file.stream, file.mimetype)},
        data={"filename": file.filename}
    )
    if upload_resp.status_code != 200:
        return jsonify({"error": "File upload failed", "details": upload_resp.text}), 500

    file_uri = upload_resp.json().get("file_uri")
    if not file_uri:
        return jsonify({"error": "No file URI returned"}), 500

    # Add the file URI and filename to the description data
    description_data["image_uri"] = file_uri
    # description_data["filename"] = file.filename

    # Post the complete ImageDescription to json_db
    create_resp = requests.post(
        f"{json_db_url}/image-descriptions", json=description_data)
    if create_resp.status_code not in (200, 201):
        return jsonify({"error": "Image description creation failed", "details": create_resp.text}), 500

    return jsonify(create_resp.json()), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
