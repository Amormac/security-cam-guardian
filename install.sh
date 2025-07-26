#!/bin/bash
echo "[+] Instalando dependencias..."
sudo apt update && sudo apt install -y python3-pip scrot
pip3 install -r requirements.txt

echo "[+] Configurando servicio..."
sudo cp systemd/security-cam-guardian.service /etc/systemd/system/
sudo systemctl enable security-cam-guardian.service
sudo systemctl start security-cam-guardian.service

echo "[+] Listo! Monitorea los logs con: tail -f /var/log/security-cam-guardian.log"