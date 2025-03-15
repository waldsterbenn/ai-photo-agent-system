from agent_manager import AgentManager
from flask import Flask, request, jsonify
from datastructures.image_carrier import ImageCarrier

app = Flask(__name__)
manager = AgentManager()


@app.route('/')
def index():
    return jsonify({"message": "AI Agents service running"})


"""You can submit a task the manager will handle it"""


@app.route('/task', methods=['POST'])
def submit_task():
    data = request.get_json()

    # Convert JSON array to a list of ImageCarrier objects
    image_carriers = [ImageCarrier(**item) for item in data]

    plan = manager.plan_task(
        f"Plan how to analyse {len(image_carriers)} images. You have image agents to at your disposal.")
    result = manager.execute_task(plan, image_carriers)
    return jsonify({'status': 'success', 'result': result})


@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({'status': 'success', 'result': "OK"})

    # result = manager.execute_task(
    #     "What is the status of the system? What time is it?").json()

    # return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
