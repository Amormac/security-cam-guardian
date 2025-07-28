import sys
import os
import pathlib
# Forzar el path absoluto y cambiar el directorio de trabajo
project_path = "/home/ariel/Documentos/ARIEL/INTERACCIÓN HUMANO COMPUTADOR/security-cam-guardian"
sys.path.insert(0, project_path)
sys.path.insert(0, os.path.join(project_path, "src"))
os.chdir(project_path)
import cv2
from face_auth import FaceAuth
from telegram_notifier import TelegramNotifier
import yaml
from pathlib import Path
import time


# Cargar configuración
with open("/home/ariel/Documentos/ARIEL/INTERACCIÓN HUMANO COMPUTADOR/security-cam-guardian/config/config.yaml") as f:
    config = yaml.safe_load(f)

KNOWN_FACES_DIR = Path(__file__).parent / "config" / "known_faces"
face_auth = FaceAuth(KNOWN_FACES_DIR)
notifier = TelegramNotifier(config["telegram"]["token"], config["telegram"]["chat_id"])

cap = cv2.VideoCapture(0)
frames = []
for _ in range(20):  # Captura 20 frames (~2 segundos)
    ret, frame = cap.read()
    if ret:
        frames.append(frame)
    time.sleep(0.1)
cap.release()

if not frames:
    sys.exit(0)  # No bloquea sudo, solo ignora

frame = frames[-1]  # Usa el último frame capturado

if not face_auth.verify_face(frame):
    cv2.imwrite("/tmp/intruso_sudo.jpg", frame)
    notifier.send_alert("🚨 ¡SUDO ejecutado por posible intruso!", "/tmp/intruso_sudo.jpg")

sys.exit(0)
