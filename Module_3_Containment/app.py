from flask import Flask

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>SENTINEL-01 Terminal</title>
    <style>
        body { background-color: #0b0f19; color: #00ffcc; font-family: 'Courier New', Courier, monospace; margin: 0; padding: 20px; }
        #terminal { height: 90vh; overflow-y: auto; }
        .prompt { color: #ff3366; }
        .input-line { display: flex; }
        input { background: transparent; border: none; color: #00ffcc; font-family: 'Courier New', Courier, monospace; font-size: 16px; width: 100%; outline: none; margin-left: 10px; }
        .output { white-space: pre-wrap; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div id="terminal">
        <div>==========================================</div>
        <div>      SENTINEL-01 INCIDENT RESPONSE      </div>
        <div>==========================================</div>
        <div>Type 'help' for a list of available commands.</div>
        <div id="output-container"></div>
        <div class="input-line">
            <span class="prompt">root@sentinel-01:~#</span>
            <input type="text" id="cmd" autocomplete="off" autofocus>
        </div>
    </div>

    <script>
        const input = document.getElementById('cmd');
        const outputContainer = document.getElementById('output-container');
        
        // Game State
        let fw_allow_mission = false;
        let fw_block_c2 = false;
        let process_killed = false;
        let file_deleted = false;

        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const cmd = input.value.trim();
                input.value = '';
                printOutput(`<span class="prompt">root@sentinel-01:~#</span> ${cmd}`);
                processCommand(cmd);
                window.scrollTo(0, document.body.scrollHeight);
            }
        });

        function printOutput(text) {
            const div = document.createElement('div');
            div.className = 'output';
            div.innerHTML = text;
            outputContainer.appendChild(div);
        }

        function processCommand(cmd) {
            if (cmd === '') return;
            
            const parts = cmd.split(' ').filter(Boolean);
            const base = parts[0] === 'sudo' ? parts[1] : parts[0];
            const fullCmd = parts[0] === 'sudo' ? parts.slice(1).join(' ') : cmd;

            if (base === 'help') {
                printOutput("Available commands: lsof, iptables, kill, rm, status, clear");
            } 
            else if (base === 'clear') {
                outputContainer.innerHTML = '';
            }
            else if (base === 'status') {
                printOutput("--- FIREWALL CHEATSHEET ---<br>Allow IP: iptables -A OUTPUT -d &lt;IP&gt; -j ACCEPT<br>Block IP: iptables -A OUTPUT -d &lt;IP&gt; -j DROP<br><br>--- VERIFICATION SCRIPTS ---<br>Run './test_network.sh' to verify containment.<br>Run './test_health.sh' to verify eradication.");
            }
            else if (base === 'lsof') {
                let out = "COMMAND     PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME\\n";
                out += "mission_d  1044 root    3u  IPv4  12345      0t0  UDP 10.0.0.50:514\\n";
                if (!process_killed) {
                    out += "systemd-u  3105 root    3u  IPv4  67890      0t0  UDP 192.168.100.55:4444";
                }
                printOutput(out);
            }
            else if (base === 'iptables') {
                if (fullCmd.includes('-d 10.0.0.50') && fullCmd.includes('ACCEPT')) {
                    fw_allow_mission = true;
                    printOutput("Rule added.");
                } else if (fullCmd.includes('-d 192.168.100.55') && fullCmd.includes('DROP')) {
                    fw_block_c2 = true;
                    printOutput("Rule added.");
                } else if (fullCmd.includes('-L')) {
                    printOutput(`Chain OUTPUT (policy ACCEPT)\\ntarget     prot opt source               destination\\n${fw_allow_mission ? 'ACCEPT     all  --  anywhere             10.0.0.50\\n' : ''}${fw_block_c2 ? 'DROP       all  --  anywhere             192.168.100.55\\n' : ''}`);
                } else {
                    printOutput("Rule added.");
                }
            }
            else if (base === 'kill') {
                if (!fullCmd.includes('-9')) {
                    printOutput("bash: kill: signal not strong enough. Try -9");
                } else if (fullCmd.includes('3105')) {
                    process_killed = true;
                    printOutput("[1]+  Killed                  systemd-update");
                } else if (fullCmd.includes('1044')) {
                    printOutput("CRITICAL ERROR: Cannot kill mission daemon!");
                } else {
                    printOutput("bash: kill: no such process");
                }
            }
            else if (base === 'rm') {
                if (fullCmd.includes('/dev/shm/.cache/systemd-update') || fullCmd.includes('systemd-update')) {
                    file_deleted = true;
                    printOutput("File removed.");
                } else {
                    printOutput("rm: cannot remove: No such file or directory");
                }
            }
            else if (fullCmd === './test_network.sh') {
                if (fw_allow_mission && fw_block_c2) {
                    printOutput("[+] Network Secured. FLAG_PART_1: viceroy{f1r3w4ll_");
                } else {
                    printOutput("[-] Threat not fully contained or missing explicit ALLOW rule for mission controller (10.0.0.50).");
                }
            }
            else if (fullCmd === './test_health.sh') {
                if (process_killed && file_deleted) {
                    printOutput("[+] Threat Eradicated. FLAG_PART_2: d3f3nd3d}");
                } else {
                    printOutput("[-] System health degraded. Ensure malicious process is killed and file is removed.");
                }
            }
            else {
                printOutput(`bash: ${base}: command not found`);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_PAGE

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)