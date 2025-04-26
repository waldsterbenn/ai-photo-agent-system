from flask import Flask, jsonify, request, make_response
from flask_cors import CORS  # add this import
import requests
import json
from image_tools import ImageTool
import os

app = Flask(__name__)
CORS(app)  # enable CORS for all routes


def get_agent_manager_url():
    return os.getenv("AGENT_SERVICE_URL", "http://ai_agents:6000")


def get_db_url():
    return os.getenv("DB_SERVICE_URL", "http://json_db:7000")


@app.route('/api', methods=['GET'])
def api():
    print("API endpoint called")
    return jsonify({"message": "Backend connected"})


@app.route('/agent-status', methods=['GET'])
def agentstatus():
    print(f"Pinging agent status: {get_agent_manager_url()}")
    try:
        response = requests.get(f"{get_agent_manager_url()}/status")
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": f"Agent status request failed: {str(e)}"}), 500


@app.route('/db-status', methods=['GET'])
def dbstatus():
    print(f"Pinging DB status: {get_db_url()}")
    try:
        response = requests.get(f"{get_db_url()}/status")
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": f"DB status request failed: {str(e)}"}), 500


@app.route('/processtask', methods=['POST'])
def process_task():
    jsonData = request.get_json()
    taskId = jsonData.get('taskId')
    if not taskId:
        return jsonify({'error': 'No task provided'}), 400

    try:
        response = requests.post(
            f"{get_agent_manager_url()}/task", json=jsonData)
        response.raise_for_status()
        return jsonify({'taskId': taskId, 'status': 'success', 'result': response.json()}), 200
    except Exception as e:
        print(f"Error submitting task: {e}")
        return jsonify({"error": "Failed to submit task"}), 500


""" Endpoint to get list of existing ImageDescriptions """


@app.route('/image-descriptions', methods=['GET'])
def get_image_descriptions():
    """
    Fetches all image descriptions from the json_db.
    """
    response = requests.get(f"{get_db_url()}/image-descriptions")
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
        f"{get_db_url()}/upload",
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
        f"{get_db_url()}/image-descriptions", json=description_data)
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
        f"{get_db_url()}/image-descriptions/{image_id}",
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
            f"{get_db_url()}/image-descriptions/{id}")
        if delete_resp.status_code != 200:
            return jsonify({"error": "Image description deletion failed", "details": delete_resp.text}), 500

    return jsonify(delete_resp.json()), 200


@app.route('/compress-image', methods=['POST'])
def compress_image_endpoint():
    print("Compressing image")
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    try:
        image_file = request.files['image']
        target_size_mb = float(request.form.get('targetSizeBytes', 2.0))

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
        print(
            f"Compress ratio: {original_size_mb:.2f}MB -> {compressed_size_mb:.2f}MB ({compressed_size_mb/original_size_mb*100:.2f}%)")
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
