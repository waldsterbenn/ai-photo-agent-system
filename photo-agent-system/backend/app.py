from flask import Flask, jsonify, request, make_response
from flask_cors import CORS  # add this import
import requests
import json
from image_tools import ImageTool

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
    return response.json()


@app.route('/processtask', methods=['POST'])
def process_task():
    data = request.get_json()
    taskId = data.get('taskId')
    if not taskId:
        return jsonify({'error': 'No task provided'}), 400

    result = submit_task(data)
    return jsonify({'taskId': taskId, 'status': 'success', 'result': result})


""" Endpoint to get list of existing ImageDescriptions """


@app.route('/image-descriptions', methods=['GET'])
def get_image_descriptions():
    """
    Fetches all image descriptions from the json_db.
    """
    response = requests.get(f"{json_db_url}/image-descriptions")
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch image descriptions"}), 500
    return jsonify(response.json()), 200


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

    # Post the complete ImageDescription to json_db
    create_resp = requests.post(
        f"{json_db_url}/image-descriptions", json=description_data)
    if create_resp.status_code not in (200, 201):
        return jsonify({"error": "Image description creation failed", "details": create_resp.text}), 500

    return jsonify(create_resp.json()), 201


@app.route('/update-image-description', methods=['PUT'])
def update_image_description():
    if request.is_json:
        data = request.get_json()
        description_data = data.get("description")
    else:
        return jsonify({"error": "Request must be JSON"}), 400

    if not description_data:
        return jsonify({"error": "No image description data provided"}), 400

    image_id = description_data.get("id")
    if not image_id:
        return jsonify({"error": "No image id provided in payload"}), 400

    update_resp = requests.put(
        f"{json_db_url}/image-descriptions/{image_id}",
        json=description_data
    )
    if update_resp.status_code not in (200, 201):
        return jsonify({"error": "Image description update failed", "details": update_resp.text}), 500

    return jsonify(update_resp.json()), update_resp.status_code

# Endpoint to delete a list of ImageDescriptions by their IDs


@app.route('/delete-image-descriptions', methods=['DELETE'])
def delete_image_descriptions():
    """
    Expects a JSON body with a list of IDs to delete.
    """
    data = request.get_json()
    ids = data.get("ids")
    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    # Send the delete request to the json_db
    for image_id in ids:
        id = image_id["id"]
        delete_resp = requests.delete(
            f"{json_db_url}/image-descriptions/{id}")
        if delete_resp.status_code != 200:
            return jsonify({"error": "Image description deletion failed", "details": delete_resp.text}), 500

    return jsonify(delete_resp.json()), 200


@app.route('/compress-image', methods=['POST'])
def compress_image_endpoint():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    try:
        image_file = request.files['image']
        target_size_mb = float(request.form.get('targetSizeMB', 2.0))

        # Read image data
        image_data = image_file.read()

        image_tool = ImageTool()
        # Extract metadata from original image
        metadata = image_tool.extract_image_metadata(image_data)

        # Compress image
        compressed_data = image_tool.compress_image_to_target_size(
            image_data, target_size_mb)

        # Calculate sizes
        original_size_mb = len(image_data) / (1024 * 1024)
        compressed_size_mb = len(compressed_data) / (1024 * 1024)

        # Create response with metadata
        response = make_response(compressed_data)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set('Content-Disposition',
                             f'attachment; filename=compressed.jpg')
        response.headers.set('X-Image-Metadata', json.dumps(metadata))
        response.headers.set('X-Original-Size', f"{original_size_mb:.2f}")
        response.headers.set('X-Compressed-Size', f"{compressed_size_mb:.2f}")

        response.headers.set('Access-Control-Expose-Headers',
                             'X-Image-Metadata, X-Original-Size, X-Compressed-Size')

        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500
