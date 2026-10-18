from flask import Flask

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>SENTINEL-01 Terminal</title>
    <style>
        body { 
            background-color: #0b0f19; 
            color: #00ffcc; 
            font-family: 'Courier New', Courier, monospace; 
            margin: 0; 
            padding: 20px; 
            overflow: hidden; 
        }
        #terminal { 
            height: 95vh; 
            overflow-y: auto; 
            padding-bottom: 20px;
        }
        .prompt { color: #ff3366; }
        .input-line { display: flex; margin-top: 10px; }
        input { 
            background: transparent; 
            border: none; 
            color: #00ffcc; 
            font-family: 'Courier New', Courier, monospace; 
            font-size: 16px; 
            width: 100%; 
            outline: none; 
            margin-left: 10px; 
        }
        .output { white-space: pre-wrap; margin-bottom: 5px; line-height: 1.3; }
        #intro-screen {
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 80vh;
            line-height: 1.5;
            font-size: 16px;
        }
        .copy-btn {
            background: #00ffcc;
            color: #000;
            border: none;
            padding: 5px 15px;
            cursor: pointer;
            margin-top: 10px;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            font-size: 14px;
            text-transform: uppercase;
        }
        .copy-btn:hover { background: #fff; box-shadow: 0 0 10px #fff; }
    </style>
</head>
<body>
    <div id="terminal">
        <!-- The Intro Screen -->
        <div id="intro-screen">
            <div>==========================================</div>
            <div>      SENTINEL-01 INCIDENT RESPONSE       </div>
            <div>==========================================</div><br>
            <div>You have successfully gained access to the terminal of SENTINEL-01 (as done in module 2: Identify every access point).</div><br>
            <div>Now you need to perform phase 3 of incident response: Contain, Eradicate, and Recovery.</div><br>
            <div><strong>TASKS:</strong></div>
            <div>- Identify and remove the rogue firewall rule.</div>
            <div>- Block the malicious C2 IP address.</div>
            <div>- Terminate the malicious process in memory.</div>
            <div>- Delete the malware payload from the disk.</div>
            <div>- Add a firewall rule to allow Mission Control (1.1.1.1).</div>
            <div>- Ping Mission Control (1.1.1.1) to verify recovery and receive your flag.</div><br>
            <div><em>(Type '?' at any time for a list of available commands).</em></div><br><br>
            <div class="prompt" style="animation: blink 1s step-end infinite;">PRESS ANY KEY TO CONTINUE...</div>
        </div>

        <!-- The Main Terminal (Hidden Initially) -->
        <div id="terminal-screen" style="display:none;">
            <div id="output-container"></div>
            <div class="input-line">
                <span class="prompt">root@sentinel-01:~#</span>
                <input type="text" id="cmd" autocomplete="off">
            </div>
        </div>
    </div>

    <script>
        const input = document.getElementById('cmd');
        const outputContainer = document.getElementById('output-container');
        const terminal = document.getElementById('terminal');
        const introScreen = document.getElementById('intro-screen');
        const terminalScreen = document.getElementById('terminal-screen');
        
        let introActive = true;
        
        // Game State Variables
        let fw_allow_c2 = true;   // Rogue rule (Needs deletion)
        let fw_block_c2 = false;  // Needs DROP rule
        let fw_allow_new = false; // Needs ACCEPT rule for 1.1.1.1
        let systemd_alive = true; // Needs kill -9
        let payload_exists = true; // Needs rm

        // Listen for the initial keypress to clear the intro
        document.addEventListener('keydown', function(e) {
            if (introActive) {
                introActive = false;
                introScreen.style.display = 'none';
                terminalScreen.style.display = 'block';
                input.focus();
                e.preventDefault(); // Prevent the key from typing into the input box
            }
        });

        // Auto-focus input field if user clicks anywhere on the terminal
        document.body.addEventListener('click', function() {
            if (!introActive) input.focus();
        });

        // Handle Terminal Commands
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const cmd = input.value.trim();
                input.value = '';
                printOutput(`<span class="prompt">root@sentinel-01:~#</span> ${cmd}`);
                processCommand(cmd);
            }
        });

        function printOutput(text) {
            const div = document.createElement('div');
            div.className = 'output';
            div.innerHTML = text;
            outputContainer.appendChild(div);
            terminal.scrollTop = terminal.scrollHeight;
        }

        // Global Copy Function for the Button
        window.copyFlag = function(btnElement, flagText) {
            navigator.clipboard.writeText(flagText).then(function() {
                btnElement.innerText = "COPIED TO CLIPBOARD!";
                btnElement.style.background = "#fff";
            }).catch(function(err) {
                btnElement.innerText = "COPY FAILED (MANUAL HIGHLIGHT REQUIRED)";
            });
        };

        function processCommand(cmd) {
            if (cmd === '') return;
            
            let cleanCmd = cmd.replace(/^sudo\s+/, '').trim();
            const parts = cleanCmd.split(' ').filter(Boolean);
            const base = parts[0];

            if (base === '?') {
                printOutput(`Available Commands:
  ?           - Show this help menu
  ufw status  - Print current firewall table
  ping        - Send ICMP ECHO_REQUEST to network hosts
  lsof        - List open files/connections
  ls          - List directory contents
  kill        - Terminate a process
  rm          - Remove files
  iptables    - Manage firewall rules
  clear       - Clear terminal screen`);
            } 
            else if (base === 'clear') {
                outputContainer.innerHTML = '';
            }
            else if (base === 'ufw' && parts[1] === 'status') {
                let out = "Chain OUTPUT (policy ACCEPT)\\n";
                out += "num  target     prot opt source               destination\\n";
                let num = 1;
                out += `${num++}    ACCEPT     all  --  anywhere             10.0.0.50\\n`;
                out += `${num++}    ACCEPT     all  --  anywhere             10.0.0.100\\n`;
                out += `${num++}    ACCEPT     all  --  anywhere             10.0.0.200\\n`;
                if (fw_allow_c2) out += `${num++}    ACCEPT     all  --  anywhere             192.168.100.55\\n`;
                if (fw_allow_new) out += `${num++}    ACCEPT     all  --  anywhere             1.1.1.1\\n`;
                if (fw_block_c2) out += `${num++}    DROP       all  --  anywhere             192.168.100.55\\n`;
                
                out += "\\n--- FIREWALL CHEATSHEET ---\\n";
                out += "Add Allow Rule: iptables -A OUTPUT -d &lt;IP&gt; -j ACCEPT\\n";
                out += "Add Block Rule: iptables -A OUTPUT -d &lt;IP&gt; -j DROP\\n";
                out += "Delete Rule:    iptables -D OUTPUT &lt;LINE_NUMBER&gt;";
                printOutput(out);
            }
            else if (base === 'ping') {
                if (parts[1] === '1.1.1.1' || (parts[1] === '-c' && parts[3] === '1.1.1.1') || parts[2] === '1.1.1.1') {
                    if (!fw_allow_new) {
                        printOutput("PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.\\n\\n--- 1.1.1.1 ping statistics ---\\n1 packets transmitted, 0 received, 100% packet loss, time 0ms\\n[-] Network unreachable. Ensure your firewall permits outbound traffic to this IP.");
                    } else {
                        // Check if ALL conditions are met
                        if (!fw_allow_c2 && fw_block_c2 && !systemd_alive && !payload_exists) {
                            let out = "PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.\\n64 bytes from 1.1.1.1: icmp_seq=1 ttl=56 time=12.4 ms\\n\\n--- 1.1.1.1 ping statistics ---\\n1 packets transmitted, 1 received, 0% packet loss, time 12ms\\n";
                            out += "\\n[+] CONNECTION ESTABLISHED. Mission Control acknowledges containment and eradication.\\n";
                            
                            const flag = "viceroy{c0nt41n3d_4nd_3r4d1c4t3d}";
                            out += `[+] RECOVERY SUCCESSFUL. FLAG: <strong>${flag}</strong>\\n`;
                            out += `<button class="copy-btn" onclick="copyFlag(this, '${flag}')">COPY FLAG TO CLIPBOARD</button>`;
                            printOutput(out);
                        } else {
                            let out = "PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.\\n64 bytes from 1.1.1.1: icmp_seq=1 ttl=56 time=12.4 ms\\n\\n--- 1.1.1.1 ping statistics ---\\n1 packets transmitted, 1 received, 0% packet loss, time 12ms\\n";
                            out += "\\n[-] Mission Control connection established, but system health/security checks FAILED.\\n";
                            
                            if (fw_allow_c2) out += "    * Rogue firewall rule for C2 server still exists.\\n";
                            if (!fw_block_c2) out += "    * C2 Server (192.168.100.55) is not blocked.\\n";
                            if (systemd_alive) out += "    * Malware process is still running in memory.\\n";
                            if (payload_exists) out += "    * Malware payload still exists on disk.\\n";
                            
                            out += "[-] Eradicate all threats and secure the firewall before requesting the flag.";
                            printOutput(out);
                        }
                    }
                } else {
                    printOutput(`ping: ${parts[1] || 'missing host'}: Name or service not known`);
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
                if (cleanCmd.includes('-A OUTPUT') && cleanCmd.includes('-d 1.1.1.1') && cleanCmd.includes('-j ACCEPT')) {
                    fw_allow_new = true;
                    printOutput("Rule added.");
                } 
                else if (cleanCmd.includes('-A OUTPUT') && cleanCmd.includes('-d 192.168.100.55') && cleanCmd.includes('-j DROP')) {
                    fw_block_c2 = true;
                    printOutput("Rule added.");
                } 
                else if (cleanCmd.includes('-D OUTPUT')) {
                    let numIndex = parts.indexOf('OUTPUT') + 1;
                    let lineNum = parseInt(parts[numIndex]);
                    
                    let activeRules = ['r1', 'r2', 'r3']; 
                    if (fw_allow_c2) activeRules.push('bad_allow');
                    if (fw_allow_new) activeRules.push('new_good');
                    if (fw_block_c2) activeRules.push('bad_drop');
                    
                    if (lineNum > 0 && lineNum <= activeRules.length) {
                        let target = activeRules[lineNum - 1];
                        if (target === 'bad_allow') {
                            fw_allow_c2 = false;
                            printOutput("Rule deleted.");
                        } else if (target === 'new_good') {
                            fw_allow_new = false;
                            printOutput("Rule deleted.");
                        } else if (target === 'bad_drop') {
                            fw_block_c2 = false;
                            printOutput("Rule deleted.");
                        } else {
                            printOutput("[-] CRITICAL ERROR: Action blocked! You cannot delete a mission-critical rule.");
                        }
                    } else {
                        printOutput("iptables: Index of deletion too big.");
                    }
                } 
                else {
                    printOutput("[-] Action blocked or rule not required for this exercise.");
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
            else if (base === 'ufw') {
                printOutput("Usage: ufw status");
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