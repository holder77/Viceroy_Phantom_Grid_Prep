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
        .output { white-space: pre-wrap; margin-bottom: 10px; line-height: 1.2; }
    </style>
</head>
<body>
    <div id="terminal">
        <div class="output">==========================================
      SENTINEL-01 INCIDENT RESPONSE       
==========================================
 1: Print current firewall table
 2: Scan system network for flag
 3: Scan system health for flag

* You are in a restricted terminal environment.
* Enter a number (1-3) to execute system checks, or type native Linux commands.
* Permitted actions: lsof, iptables, kill, rm, ls, clear, help
==========================================</div>
        <div id="output-container"></div>
        <div class="input-line">
            <span class="prompt">root@sentinel-01:~#</span>
            <input type="text" id="cmd" autocomplete="off" autofocus>
        </div>
    </div>

    <script>
        const input = document.getElementById('cmd');
        const outputContainer = document.getElementById('output-container');
        
        // Game State Variables
        let fw_allow_c2 = true; // Attacker added this rogue rule
        let fw_block_c2 = false; // Team must add this
        let fw_allow_mission = false; // Team must add this
        
        let systemd_alive = true; // Bad process
        let payload_exists = true; // Bad file

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
            
            // Normalize command
            let cleanCmd = cmd.replace(/^sudo\s+/, '').trim();
            const parts = cleanCmd.split(' ').filter(Boolean);
            const base = parts[0];

            if (base === 'help') {
                printOutput("Available commands: lsof, iptables, kill, rm, ls, clear<br>Options: 1 (Firewall), 2 (Check Network), 3 (Check Health)");
            } 
            else if (base === 'clear') {
                outputContainer.innerHTML = '';
            }
            else if (base === '1') {
                let out = "Chain OUTPUT (policy ACCEPT)\\n";
                out += "num  target     prot opt source               destination\\n";
                let num = 1;
                out += `${num++}    ACCEPT     all  --  anywhere             10.0.0.200\\n`; // Decoy good rule
                if (fw_allow_c2) out += `${num++}    ACCEPT     all  --  anywhere             192.168.100.55\\n`; // Rogue rule
                if (fw_allow_mission) out += `${num++}    ACCEPT     all  --  anywhere             10.0.0.50\\n`;
                if (fw_block_c2) out += `${num++}    DROP       all  --  anywhere             192.168.100.55\\n`;
                printOutput(out);
            }
            else if (base === '2') {
                printOutput("[*] Analyzing firewall rules...");
                if (!fw_allow_c2 && fw_block_c2 && fw_allow_mission) {
                    printOutput("[+] Network Secured. FLAG_PART_1: viceroy{f1r3w4ll_");
                } else if (fw_allow_c2) {
                    printOutput("[-] Rogue ACCEPT rule for C2 server still exists. Remove it.");
                } else if (!fw_block_c2) {
                    printOutput("[-] C2 Server (192.168.100.55) is not blocked (DROP).");
                } else {
                    printOutput("[-] Missing explicit ALLOW rule for mission controller (10.0.0.50).");
                }
            }
            else if (base === '3') {
                printOutput("[*] Scanning endpoint health...");
                if (systemd_alive || payload_exists) {
                    if (systemd_alive) printOutput("[-] Malware process is still running in memory! Use 'kill -9 &lt;PID&gt;'.");
                    if (payload_exists) printOutput("[-] Malware file still exists on disk! Delete it using 'rm'.");
                } else {
                    printOutput("[+] Threat Eradicated. FLAG_PART_2: d3f3nd3d}");
                }
            }
            else if (base === 'lsof') {
                let out = "COMMAND     PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME\\n";
                out += "mission_d  1044 root    3u  IPv4  12345      0t0  UDP 10.0.0.50:514\\n";
                out += "ntp_sync   2201 root    3u  IPv4  22345      0t0  UDP 8.8.8.8:123\\n";
                out += "svss_rel   2944 root    3u  IPv4  32345      0t0  UDP 10.0.0.100:8080\\n";
                if (systemd_alive) {
                    out += "systemd-u  3105 root    3u  IPv4  67890      0t0  UDP 192.168.100.55:4444";
                }
                printOutput(out);
            }
            else if (base === 'ls') {
                let out = "total 24\\n";
                out += "drwxr-xr-x 2 root root 4096 Oct 18 10:24 .\\n";
                out += "drwxr-xr-x 3 root root 4096 Oct 18 10:24 ..\\n";
                out += "-rw-r--r-- 1 root root 2048 Oct 18 10:24 ground_calibration.bin\\n";
                out += "-rw-r--r-- 1 root root 4096 Oct 18 10:24 svss_telemetry.log\\n";
                if (payload_exists) {
                    out += "-rwxr-xr-x 1 root root 8192 Oct 18 10:25 systemd-update\\n";
                }
                printOutput(out);
            }
            else if (base === 'iptables') {
                if (cleanCmd.includes('-A OUTPUT') && cleanCmd.includes('10.0.0.50') && cleanCmd.includes('ACCEPT')) {
                    fw_allow_mission = true;
                    printOutput("Rule added.");
                } 
                else if (cleanCmd.includes('-A OUTPUT') && cleanCmd.includes('192.168.100.55') && cleanCmd.includes('DROP')) {
                    fw_block_c2 = true;
                    printOutput("Rule added.");
                } 
                else if (cleanCmd.includes('-D OUTPUT') && (cleanCmd.includes('192.168.100.55') || cleanCmd.includes(' 2'))) {
                    fw_allow_c2 = false;
                    printOutput("Rule deleted.");
                } 
                else {
                    printOutput("Rule accepted.");
                }
            }
            else if (base === 'kill') {
                if (!cleanCmd.includes('-9')) {
                    printOutput("bash: kill: signal not strong enough. Try -9");
                } else if (cleanCmd.includes('3105')) {
                    systemd_alive = false;
                    printOutput("[1]+  Killed                  systemd-update");
                } else if (cleanCmd.includes('1044') || cleanCmd.includes('2201') || cleanCmd.includes('2944')) {
                    printOutput("CRITICAL ERROR: Action blocked! You cannot kill a legitimate mission daemon.");
                } else {
                    printOutput("bash: kill: no such process");
                }
            }
            else if (base === 'rm') {
                if (cleanCmd.includes('systemd-update')) {
                    payload_exists = false;
                    printOutput("File removed.");
                } else if (cleanCmd.includes('telemetry') || cleanCmd.includes('calibration')) {
                    printOutput("CRITICAL ERROR: Action blocked! You are attempting to delete critical SVSS mission data.");
                } else {
                    printOutput("rm: cannot remove: No such file or directory");
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