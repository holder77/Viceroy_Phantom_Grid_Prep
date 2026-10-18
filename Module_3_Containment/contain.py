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
        # Whitelist of allowed Linux commands
        self.allowed_cmds = ['lsof', 'netstat', 'ps', 'top', 'ss', 'iptables', 'ufw', 'rm', 'ls', 'cd', 'pwd', 'clear', 'cat', 'grep', 'pgrep']
        self.setup_env()

    def setup_env(self):
        print("[*] Initializing SENTINEL-01 Live Environment...")
        
        # 1. Stage the Malware and Decoy SVSS Files
        self.cache_dir = '/dev/shm/.cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.payload = f'{self.cache_dir}/systemd-update'
        with open(self.payload, 'w') as f:
            f.write('#!/bin/bash\nwhile true; do nc -u 192.168.100.55 4444 2>/dev/null; sleep 2; done\n')
        os.chmod(self.payload, 0o755)

        with open(f'{self.cache_dir}/svss_telemetry.log', 'w') as f:
            f.write('SVSS Satellite Uplink active. VE and TI metrics nominal.\n')
        with open(f'{self.cache_dir}/ground_calibration.bin', 'w') as f:
            f.write('010101010101010101\n')

        # 2. Spawn Mission Daemons and Malware
        self.p_good1 = subprocess.Popen(['bash', '-c', 'exec -a cuas_sensor_daemon nc -u 10.0.0.50 514 >/dev/null 2>&1'])
        self.p_good2 = subprocess.Popen(['bash', '-c', 'exec -a svss_uplink nc -u 10.0.0.200 443 >/dev/null 2>&1'])
        self.p_good3 = subprocess.Popen(['bash', '-c', 'exec -a svss_ground_relay nc -u 10.0.0.100 8080 >/dev/null 2>&1'])
        self.p_bad = subprocess.Popen(['bash', '-c', f'exec -a systemd-update {self.payload} >/dev/null 2>&1'])
        time.sleep(1)

    def cleanup(self):
        print("\n[*] Terminating simulated network connections...")
        for p in [self.p_good1, self.p_good2, self.p_good3, self.p_bad]:
            try:
                p.kill()
            except:
                pass
        
        subprocess.run("pkill -f systemd-update >/dev/null 2>&1", shell=True)
        
        if os.path.exists(self.payload):
            os.remove(self.payload)
            
        subprocess.run("sudo iptables -D OUTPUT -d 192.168.100.55 -j DROP >/dev/null 2>&1", shell=True)
        subprocess.run("sudo iptables -D OUTPUT -d 10.0.0.50 -j ACCEPT >/dev/null 2>&1", shell=True)

    def do_EOF(self, arg):
        """Catches the End-of-File signal to prevent infinite loops."""
        self.cleanup()
        return True

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
            pass 
            
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
        if line.strip() in ['1', '2', '3', '4']:
            getattr(self, f"do_{line.strip()}")("")
            return

        cmd_parts = line.strip().split()
        if not cmd_parts:
            return

        base_cmd = cmd_parts[0]
        if base_cmd == 'sudo' and len(cmd_parts) > 1:
            base_cmd = cmd_parts[1]

        # 1. Firewall Manipulations (Protecting SVSS infrastructure)
        if base_cmd in ['iptables', 'ufw']:
            protected_ips = ['10.0.0.50', '10.0.0.100', '10.0.0.200']
            if 'DROP' in cmd_parts or 'REJECT' in cmd_parts or 'deny' in cmd_parts:
                for ip in protected_ips:
                    if ip in line:
                        print(f"[-] CRITICAL ERROR: Action blocked! You cannot sever the connection to friendly mission asset {ip}.")
                        return

        # 2. Process Termination Restrictions
        if base_cmd == 'kill':
            if '-9' not in cmd_parts:
                print("[-] Action not allowed: That signal isn't strong enough to terminate the rogue service. Try the -9 flag instead.")
                return
            
            target_pid = cmd_parts[-1]
            try:
                cmd_line = subprocess.check_output(f"ps -p {target_pid} -o command=", shell=True, text=True).strip()
                if 'cuas_sensor_daemon' in cmd_line or 'svss_' in cmd_line:
                    print(f"[-] CRITICAL ERROR: Process {target_pid} is a critical mission daemon! Action blocked to preserve uptime.")
                    return
            except subprocess.CalledProcessError:
                pass
            
            subprocess.run(line, shell=True)
            return

        # 3. File Deletion Restrictions
        if base_cmd == 'rm':
            if 'telemetry' in line or 'calibration' in line:
                print("[-] CRITICAL ERROR: Action blocked! You are attempting to delete critical SVSS mission data.")
                return

        # 4. Standard Allowed Commands
        if base_cmd in self.allowed_cmds:
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