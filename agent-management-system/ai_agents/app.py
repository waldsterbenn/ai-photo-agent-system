from agent_manager import AgentManager
from flask import Flask, request, jsonify
from datastructures.image_carrier import ImageCarrier

app = Flask(__name__)
manager = AgentManager()


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

    plan = manager.plan_task(taskPrompt, criteria, image_carriers)
    result = manager.execute_task()
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
