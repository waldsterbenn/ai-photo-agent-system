from agent_manager import AgentManager
from flask import Flask, request, jsonify
from datastructures.image_carrier import ImageCarrier
from duplication_detection import DuplicationDetection

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({"message": "AI Agents service running"})


@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({'status': 'success', 'result': "OK"})


"""You can submit a task the manager will handle it"""


@app.route('/task', methods=['POST'])
def submit_task():
    data = request.get_json()
    taskPrompt = data.get('taskPrompt')
    criteria = data.get('criteria')
    images = data.get('images')

    # Convert JSON array to a list of ImageCarrier objects
    image_carriers = [ImageCarrier(**item) for item in images]
    print(f"Received {len(image_carriers)} images")
    manager = AgentManager()
    plan = manager.plan_task(taskPrompt, criteria, image_carriers)
    result = manager.execute_task()
    return jsonify(result)


@app.route('/duplicate-detection', methods=['POST'])
def dublicate_detection():
    data = request.get_json()
    detector = DuplicationDetection()
    duplicates = detector.detect_duplicate_descriptions(
        data['imageDescriptions'])
    return jsonify(duplicates), 200
