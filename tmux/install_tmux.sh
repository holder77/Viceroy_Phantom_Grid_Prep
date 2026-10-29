#!/bin/bash

echo "[*] Checking for tmux..."
if ! command -v tmux &> /dev/null; then
    echo "[*] tmux not found. Installing now..."
    sudo apt-get update -y
    sudo apt-get install tmux -y
else
    echo "[+] tmux is already installed."
fi

echo "[*] Building Tactical Tmux Command Post..."

# Grab the exact absolute path to bypass Kali XFCE desktop shortcut bugs
USER_HOME=$(eval echo ~$USER)

# Create the interactive launcher script with Pre-Deployment Briefing
cat << 'EOF' > "$USER_HOME/Desktop/tmux-ops.sh"
#!/bin/bash
clear
echo -e "\e[1;30m+-------+-------+\e[0m"
echo -e "\e[1;30m|\e[0m       \e[1;30m|\e[0m       \e[1;30m|  \e[1;32m _\e[0m"
echo -e "\e[1;30m|\e[0m       \e[1;30m+-------+  \e[1;32m| |_ _ __ ___  _   ___  __\e[0m"
echo -e "\e[1;30m|\e[0m       \e[1;30m|\e[0m       \e[1;30m|  \e[1;32m| __| '_ \` _ \\| | | \\ \\/ /\e[0m"
echo -e "\e[1;30m+-------+-------+  \e[1;32m| |_| | | | | | |_| |>  <\e[0m"
echo -e "\e[1;32m=================   \\__|_| |_| |_|\\__,_/_/\\_\\ \e[0m"
echo ""
echo -e "\e[1;33mPREFIX KEY: Ctrl + b (Press and release, then hit command)\e[0m"
echo ""
echo -e "\e[1;36m[CORE BATTLE RHYTHM]\e[0m"
echo "Split Vertical (Left/Right) : Prefix then %"
echo "Split Horizontal (Top/Bot)  : Prefix then \""
echo "Move Cursor Between Panes   : Prefix then Arrow Keys"
echo "Zoom/Fullscreen Active Pane : Prefix then z"
echo "Detach (Leave Running)      : Prefix then d"
echo -e "\e[1;32m========================================================\e[0m"
echo -e "\e[1;31m[!] PRE-DEPLOYMENT BRIEFING - READ BEFORE PROCEEDING [!]\e[0m"
echo -e "1. \e[1;37mALL OPERATORS:\e[0m You MUST be SSH'd into the shared Jump Box."
echo -e "   (If you run this locally on your own laptop, multiplayer fails)."
echo -e "2. \e[1;37mRECON:\e[0m Run this script and select [1] to establish the session."
echo -e "3. \e[1;37mMAIN FORCE:\e[0m Wait for Recon. SSH into the Jump Box, run this"
echo -e "   script, and select [2] to link your screen to Recon's feed."
echo -e "\e[1;32m========================================================\e[0m"
echo ""
echo -e "\e[1;37m[1] Recon Forward Observer (INITIAL ENTRY - Create 'ops' session)\e[0m"
echo -e "\e[1;37m[2] Main Expeditionary Force (OVERWATCH - Attach to 'ops' session)\e[0m"
echo ""
read -p "Select Deployment Role (1 or 2): " role

if [ "$role" == "1" ]; then
    echo -e "\e[1;32mEstablishing Beachhead...\e[0m"
    sleep 1
    
    tmux has-session -t ops 2>/dev/null
    if [ $? != 0 ]; then
        exec tmux new-session -s ops \; \
            split-window -h \; \
            send-keys -t 0 "clear" C-m \; \
            send-keys -t 0 "echo -e '\e[1;33m[RECON - MAIN CONSOLE]\e[0m'" C-m \; \
            send-keys -t 0 "echo -e '1. SSH into the jump box: \e[1;32mssh -p 2226 analyst@localhost\e[0m'" C-m \; \
            send-keys -t 0 "echo '2. Keep an eye on system logs or run active commands here.'" C-m \; \
            send-keys -t 1 "clear" C-m \; \
            send-keys -t 1 "echo -e '\e[1;33m[RECON - SECONDARY PANE]\e[0m'" C-m \; \
            send-keys -t 1 "echo 'Use this pane for secondary tasks (e.g., ss -tunap, vi config files).'" C-m \; \
            select-pane -t 0
    else
        exec tmux attach-session -t ops
    fi

elif [ "$role" == "2" ]; then
    echo -e "\e[1;32mLinking to Command Post...\e[0m"
    sleep 1
    
    tmux has-session -t ops 2>/dev/null
    if [ $? == 0 ]; then
        tmux send-keys -t ops "echo -e '\e[1;32m[!] MAIN EXPEDITIONARY FORCE HAS JOINED THE SESSION\e[0m'" C-m
        exec tmux attach-session -t ops
    else
        echo -e "\e[1;31mError: 'ops' session not found. Forward Observer must deploy first!\e[0m"
        read -p "Press Enter to exit..."
    fi
else
    echo -e "\e[1;31mMission Aborted.\e[0m"
    sleep 2
fi
EOF

chmod +x "$USER_HOME/Desktop/tmux-ops.sh"

# Create the clickable Desktop Shortcut using the hardcoded absolute path
cat << EOF > "$USER_HOME/Desktop/Tactical-Tmux.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Tactical Tmux
Comment=Launch Shared Tmux Session
Exec=$USER_HOME/Desktop/tmux-ops.sh
Icon=utilities-terminal
Terminal=true
StartupNotify=true
EOF

chmod +x "$USER_HOME/Desktop/Tactical-Tmux.desktop"
gio set "$USER_HOME/Desktop/Tactical-Tmux.desktop" metadata::trusted true 2>/dev/null

echo "[+] Deployment complete! Tactical Tmux is ready on the Desktop."