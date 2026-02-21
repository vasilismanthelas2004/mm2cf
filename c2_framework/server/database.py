import sqlite3
import datetime

DB_NAME = 'c2_server.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS agents (agent_id TEXT PRIMARY KEY, ip_address TEXT, hostname TEXT, last_seen TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT, command TEXT, status TEXT DEFAULT 'pending', output TEXT, FOREIGN KEY(agent_id) REFERENCES agents(agent_id))''')
    conn.commit()
    conn.close()

def register_or_update_agent(agent_id, ip_address, hostname):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    cursor.execute('''
        INSERT INTO agents (agent_id, ip_address, hostname, last_seen) VALUES (?, ?, ?, ?)
        ON CONFLICT(agent_id) DO UPDATE SET ip_address=excluded.ip_address, last_seen=excluded.last_seen
    ''', (agent_id, ip_address, hostname, now))
    conn.commit()
    conn.close()

def queue_task(agent_id, command):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (agent_id, command) VALUES (?, ?)', (agent_id, command))
    conn.commit()
    conn.close()

def get_pending_task(agent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, command FROM tasks WHERE agent_id = ? AND status = 'pending' ORDER BY task_id ASC LIMIT 1", (agent_id,))
    task = cursor.fetchone()
    if task:
        cursor.execute("UPDATE tasks SET status = 'sent' WHERE task_id = ?", (task['task_id'],))
        conn.commit()
        conn.close()
        return dict(task)
    conn.close()
    return None

def submit_task_result(task_id, output):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'completed', output = ? WHERE task_id = ?", (output, task_id))
    conn.commit()
    conn.close()

def get_all_agents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents")
    agents = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return agents

def get_agent_results(agent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, command, status, output FROM tasks WHERE agent_id = ? ORDER BY task_id DESC LIMIT 10", (agent_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results