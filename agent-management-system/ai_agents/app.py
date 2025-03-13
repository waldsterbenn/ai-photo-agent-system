from agent_manager import AgentManager
from flask import Flask, request, jsonify

app = Flask(__name__)
manager = AgentManager()


@app.route('/')
def index():
    return jsonify({"message": "AI Agents service running"})


"""You can submit a task the manager will handle it"""


@app.route('/task', methods=['POST'])
def submit_task():
    data = request.get_json()
    task = data.get('task')
    if not task:
        return jsonify({'error': 'No task provided'}), 400

    result = manager.execute_task(task)
    return jsonify({'status': 'success', 'result': result})


@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({'status': 'running'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
