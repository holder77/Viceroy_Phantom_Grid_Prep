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

# Create the interactive launcher script with ASCII Art
cat << 'EOF' > ~/Desktop/tmux-ops.sh
#!/bin/bash
clear
echo -e "\e[1;30m+-------+-------+\e[0m"
echo -e "\e[1;30m|\e[0m       \e[1;30m|\e[0m       \e[1;30m|  \e[1;32m _\e[0m"
echo -e "\e[1;30m|\e[0m       \e[1;30m+-------+  \e[1;32m| |_ _ __ ___  _   ___  __\e[0m"
echo -e "\e[1;30m|\e[0m       \e[1;30m|\e[0m       \e[1;30m|  \e[1;32m| __| '_ \` _ \\| | | \\ \\/ /\e[0m"
echo -e "\e[1;30m+-------+-------+  \e[1;32m| |_| | | | | | |_| |>  <\e[0m"
echo -e "\e[1;32m=================   \\__|_| |_| |_|\\__,_/_/\\_\\\e[0m"
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
echo ""
echo -e "\e[1;37m[1] Main Expeditionary Force (Create new 'ops' session)\e[0m"
echo -e "\e[1;37m[2] Forward Observer (Attach to existing 'ops' session)\e[0m"
echo ""
read -p "Select Deployment Role (1 or 2): " role

if [ "$role" == "1" ]; then
    echo -e "\e[1;32mSpinning up Main Command Post...\e[0m"
    sleep 1
    tmux new -s ops
elif [ "$role" == "2" ]; then
    echo -e "\e[1;32mLinking to Command Post...\e[0m"
    sleep 1
    tmux attach -t ops
else
    echo -e "\e[1;31mMission Aborted.\e[0m"
    sleep 2
fi
EOF

chmod +x ~/Desktop/tmux-ops.sh

# Create the clickable Desktop Shortcut
cat << 'EOF' > ~/Desktop/Tactical-Tmux.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Tactical Tmux
Comment=Launch Shared Tmux Session
Exec=bash -c "$HOME/Desktop/tmux-ops.sh"
Icon=utilities-terminal
Terminal=true
StartupNotify=true
EOF

chmod +x ~/Desktop/Tactical-Tmux.desktop

echo "[+] Deployment complete! Tactical Tmux is ready on the Desktop."