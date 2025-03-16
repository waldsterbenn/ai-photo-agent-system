from flask import Flask, jsonify, request
from flask_cors import CORS  # add this import
import requests

app = Flask(__name__)
CORS(app)  # enable CORS for all routes

agent_manager_url = "http://ai_agents:6000"


def submit_task(jsonData):
    """Submit a task to the agent server."""
    try:
        response = requests.post(
            f"{agent_manager_url}/task", json=jsonData)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@app.route('/api', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Python backend!"})


@app.route('/status', methods=['GET'])
def status():
    response = requests.get(f"{agent_manager_url}/status")
    response.raise_for_status()
    return response.json()


@app.route('/processtask', methods=['POST'])
def process_task():
    data = request.get_json()
    taskId = data.get('taskId')
    if not taskId:
        return jsonify({'error': 'No task provided'}), 400

    result = submit_task(data)
    return jsonify({'taskId': taskId, 'status': 'success', 'result': result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
