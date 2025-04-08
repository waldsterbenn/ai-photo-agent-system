# import ptvsd
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tinydb import TinyDB, Query
from pydantic import ValidationError
from image_description_model import ImageDescriptionModel
from user_model import UserModel

app = Flask(__name__)
CORS(app)

# Ensure uploads directory exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize TinyDB (data stored in db.json)
db = TinyDB("db.json")
img_table = db.table("image_descriptions")
user_table = db.table("users")


# Helper function to assign an auto-incremented id
def get_next_id(table) -> int:
    items = table.all()
    if not items:
        return 1
    return max(item["id"] for item in items if "id" in item) + 1

# File upload endpoint


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    # Create a URI (this can be a static path or URL as needed for your environment)
    file_uri = f"/{UPLOAD_FOLDER}/{file.filename}"
    return jsonify({"file_uri": file_uri}), 200

# Serve uploaded files


@app.route("/files/<path:filename>", methods=["GET"])
def get_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# CRUD endpoints for ImageDescriptions


@app.route("/image-descriptions", methods=["GET"])
def get_image_descriptions():
    return jsonify(img_table.all()), 200


@app.route("/image-descriptions", methods=["POST"])
def create_image_description():
    try:
        data = request.get_json()
        model = ImageDescriptionModel(**data)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    model.id = get_next_id(img_table)
    img_table.insert(model.dict())
    return jsonify(model.dict()), 201


@app.route("/image-descriptions/<int:item_id>", methods=["GET"])
def get_image_description(item_id):
    Item = Query()
    item = img_table.get(Item.id == item_id)
    if not item:
        return jsonify({"error": "Not found"}), 404
    return jsonify(item), 200


@app.route("/image-descriptions/<int:item_id>", methods=["PUT"])
def update_image_description(item_id):
    Item = Query()
    item = img_table.get(Item.id == item_id)
    if not item:
        return jsonify({"error": "Not found"}), 404
    try:
        data = request.get_json()
        model = ImageDescriptionModel(**data)
    except ValidationError as e:
        return jsonify(e.errors()), 400
    model.id = item_id
    img_table.update(model.dict(), Item.id == item_id)
    return jsonify(model.dict()), 200


@app.route("/image-descriptions/<int:item_id>", methods=["DELETE"])
def delete_image_description(item_id):
    Item = Query()
    if not img_table.get(Item.id == item_id):
        return jsonify({"error": "Not found"}), 404
    img_table.remove(Item.id == item_id)
    return jsonify({"message": "Deleted"}), 200

# CRUD endpoints for Users


@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(user_table.all()), 200


@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        model = UserModel(**data)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    model.id = get_next_id(user_table)
    user_table.insert(model.dict())
    return jsonify(model.dict()), 201


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    Item = Query()
    user = user_table.get(Item.id == user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify(user), 200


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    Item = Query()
    if not user_table.get(Item.id == user_id):
        return jsonify({"error": "Not found"}), 404
    try:
        data = request.get_json()
        model = UserModel(**data)
    except ValidationError as e:
        return jsonify(e.errors()), 400
    model.id = user_id
    user_table.update(model.dict(), Item.id == user_id)
    return jsonify(model.dict()), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    Item = Query()
    if not user_table.get(Item.id == user_id):
        return jsonify({"error": "Not found"}), 404
    user_table.remove(Item.id == user_id)
    return jsonify({"message": "Deleted"}), 200


if __name__ == "__main__":
    # Listen on all interfaces on port 7000
    # ptvsd.enable_attach(address=('0.0.0.0', 5678))
    app.run(debug=True, host="0.0.0.0", port=7000)
