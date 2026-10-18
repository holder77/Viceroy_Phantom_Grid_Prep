#!/usr/bin/env python3
import cmd
import subprocess
import os
import time

class SentinelConsole(cmd.Cmd):
    prompt = '(sentinel-01) > '
    intro = """
==========================================
      SENTINEL-01 INCIDENT RESPONSE       
==========================================
 1: Print current firewall table
 2: Scan system network for flag
 3: Scan system health for flag
 4: Cleanup and terminate

* You are in a restricted terminal environment.
* Enter a number (1-4) to execute system checks, or type native Linux commands.
* Permitted actions: process enumeration, termination, file deletion, and firewall manipulation.
==========================================
"""

    def __init__(self):
        super().__init__()
        # The whitelist of allowed Linux commands
        self.allowed_cmds = ['lsof', 'netstat', 'ps', 'top', 'ss', 'iptables', 'ufw', 'rm', 'ls', 'cd', 'pwd', 'clear', 'cat', 'grep', 'pgrep']
        self.setup_env()

    def setup_env(self):
        print("[*] Initializing SENTINEL-01 Live Environment...")
        
        # 1. Stage the Fake Malware
        os.makedirs('/dev/shm/.cache', exist_ok=True)
        self.payload = '/dev/shm/.cache/systemd-update'
        with open(self.payload, 'w') as f:
            f.write('#!/bin/bash\nwhile true; do nc -u 192.168.100.55 4444 2>/dev/null; sleep 2; done\n')
        os.chmod(self.payload, 0o755)

        # 2. Spawn processes in the background
        self.p_good = subprocess.Popen(['bash', '-c', 'exec -a cuas_sensor_daemon nc -u 10.0.0.50 514 >/dev/null 2>&1'])
        self.p_decoy = subprocess.Popen(['bash', '-c', 'exec -a ntp_sync nc -u 8.8.8.8 123 >/dev/null 2>&1'])
        self.p_bad = subprocess.Popen(['bash', '-c', f'exec -a systemd-update {self.payload} >/dev/null 2>&1'])
        time.sleep(1) # Give the sockets a second to open

    def cleanup(self):
        print("\n[*] Terminating simulated network connections...")
        for p in [self.p_good, self.p_decoy, self.p_bad]:
            try:
                p.kill()
            except:
                pass
        
        # Kill any lingering malware processes
        subprocess.run("pkill -f systemd-update >/dev/null 2>&1", shell=True)
        
        # Delete the malware file
        if os.path.exists(self.payload):
            os.remove(self.payload)
            
        # Flush the specific iptables rules to clean up the environment for the next try
        subprocess.run("sudo iptables -D OUTPUT -d 192.168.100.55 -j DROP >/dev/null 2>&1", shell=True)
        subprocess.run("sudo iptables -D OUTPUT -d 10.0.0.50 -j ACCEPT >/dev/null 2>&1", shell=True)

    def do_1(self, arg):
        """Print current firewall table"""
        print("\n[+] Active iptables OUTPUT Rules:")
        print("-" * 42)
        subprocess.run("sudo iptables -L OUTPUT -v -n --line-numbers", shell=True)
        print()

    def do_2(self, arg):
        """Scan system network for flag"""
        print("\n[*] Analyzing firewall rules...")
        try:
            rules = subprocess.check_output("sudo iptables-save", shell=True, text=True)
            if "192.168.100.55" in rules and ("DROP" in rules or "REJECT" in rules):
                if "10.0.0.50" in rules and "ACCEPT" in rules:
                    print("[+] Network Secured. FLAG_PART_1: viceroy{f1r3w4ll_")
                else:
                    print("[-] Threat blocked, but missing explicit ALLOW rule for mission controller (10.0.0.50).")
            else:
                print("[-] C2 Server (192.168.100.55) is not blocked.")
        except Exception:
            print("[-] Error reading iptables.")
        print()

    def do_3(self, arg):
        """Scan system health for flag"""
        print("\n[*] Scanning endpoint health...")
        err = False
        try:
            subprocess.check_output("pgrep -f systemd-update", shell=True)
            print("[-] Malware process is still running in memory! Remember to terminate the PID.")
            err = True
        except subprocess.CalledProcessError:
            pass # Process not found, which is good
            
        if os.path.exists(self.payload):
            print("[-] Process killed, but the malware file still exists on disk! Find the path and delete it.")
            err = True

        if not err:
            print("[+] Threat Eradicated. FLAG_PART_2: d3f3nd3d}\n")
        print()

    def do_4(self, arg):
        """Cleanup and terminate"""
        self.cleanup()
        print("[+] Environment restored. Keep up the good fight.")
        return True

    def default(self, line):
        """Intercepts all other commands typed into the console"""
        # Allow them to just type 1, 2, 3, or 4 without the 'do_' prefix
        if line.strip() in ['1', '2', '3', '4']:
            getattr(self, f"do_{line.strip()}")("")
            return

        cmd_parts = line.strip().split()
        if not cmd_parts:
            return

        base_cmd = cmd_parts[0]
        
        # If they use sudo, strip it and check the actual command
        if base_cmd == 'sudo' and len(cmd_parts) > 1:
            base_cmd = cmd_parts[1]

        # The Sec+ PBQ Kill Constraint
        if base_cmd == 'kill':
            if '-9' not in cmd_parts:
                print("[-] Action not allowed: That signal isn't strong enough to terminate the rogue service. Try the -9 flag instead.")
            else:
                subprocess.run(line, shell=True)
            return

        # General whitelist enforcer
        if base_cmd in self.allowed_cmds:
            # Handle native directory changes so they actually work in Python
            if base_cmd == 'cd':
                try:
                    os.chdir(cmd_parts[1] if len(cmd_parts) > 1 else os.path.expanduser('~'))
                except Exception as e:
                    print(f"cd: {e}")
            else:
                subprocess.run(line, shell=True)
        else:
            print(f"[-] Action not allowed: '{base_cmd}' is restricted by SENTINEL-01 policy.")

if __name__ == '__main__':
    console = SentinelConsole()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        print("\n[*] Caught interrupt. Cleaning up...")
        console.cleanup()