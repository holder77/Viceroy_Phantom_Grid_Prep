#!/bin/bash
echo "[*] Installing Nuclei..."
sudo apt update && sudo apt install -y nuclei

echo "[*] Downloading ProjectDiscovery templates..."
nuclei -update-templates

echo "[*] Creating Nuclei Scanner desktop shortcut..."
cat << 'EOF' > ~/Desktop/Nuclei_Scanner.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Nuclei Scanner
Exec=bash -c "read -p \"Enter target URL (e.g., https://example.com): \" target; nuclei -u \$target -t http/exposures/; echo \"Scan Complete.\"; read -p \"Press Enter to close...\""
Terminal=true
EOF

chmod +x ~/Desktop/Nuclei_Scanner.desktop
echo "[+] Setup complete! Double-click 'Nuclei Scanner' on your Kali desktop to launch."