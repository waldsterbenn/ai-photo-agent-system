# import ptvsd
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tinydb import TinyDB, Query
from pydantic import ValidationError
from image_description_model import ImageDescriptionModel
from user_model import UserModel

print("Starting server...")
app = Flask(__name__)
CORS(app)
print("CORS enabled")

print("Setting up directories...")
BASE_FOLDER = os.path.dirname(os.path.join(os.getcwd(), "app"))
DATA_FOLDER = os.path.join(BASE_FOLDER, "data")

UPLOAD_FOLDER = os.path.join(DATA_FOLDER, "image_uploads")
print(f"Creating Upload folder: {UPLOAD_FOLDER}")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("creating database")
# Initialize TinyDB (data stored in db.json)
DB_PATH = os.path.join(DATA_FOLDER, "db.json")
db = TinyDB(DB_PATH)
img_table = db.table("image_descriptions")
user_table = db.table("users")

print("Setup complete")


# Helper function to assign an auto-incremented id


def get_next_id(table) -> int:
    items = table.all()
    if not items:
        return 1
    return max(item["id"] for item in items if "id" in item) + 1


@app.route("/status", methods=["GET"])
def status():
    return jsonify("json_db connected"), 200


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
    descriptions = img_table.all()
    for item in descriptions:
        # Convert image_uri to a full path or URL if needed
        if "image_uri" in item:
            item["image_uri"] = f"/{UPLOAD_FOLDER}/{item['image_uri']}"
    return jsonify(descriptions), 200


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
    table_item = img_table.get(Item.id == item_id)
    if not table_item:
        return jsonify({"error": f"Item with id={item_id}Not found"}), 404
    filePath = table_item["image_uri"]
    if os.path.exists(filePath):
        os.remove(filePath)

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


# if __name__ == "__main__":
#     print("Starting server...")
#     print("Starting server...")
#     # Listen on all interfaces on port 7000
#     app.run(debug=True, host="0.0.0.0", port=7000)
