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
import subprocess


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
#
if not frames:
    sys.exit(0)  # No bloquea sudo, solo ignora

frame = frames[-1]  # Usa el último frame capturado
# ...continúa el código...
# Captura screenshot de la pantalla
try:
    screenshot_path = "/tmp/sudo_screenshot.png"
    # Detectar si estamos en Wayland
    wayland = os.environ.get("XDG_SESSION_TYPE", "") == "wayland"
    gnome_screenshot = subprocess.call(["which", "gnome-screenshot"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    if wayland and gnome_screenshot:
        # Usar D-Bus para capturar pantalla en la sesión del usuario
        user_id = os.getuid()
        dbus_address = f"unix:path=/run/user/{user_id}/bus"
        env = os.environ.copy()
        env["DBUS_SESSION_BUS_ADDRESS"] = dbus_address
        subprocess.call(["gnome-screenshot", "-f", screenshot_path], env=env)
    elif gnome_screenshot:
        subprocess.call(["gnome-screenshot", "-f", screenshot_path])
    elif subprocess.call(["which", "scrot"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        subprocess.call(["scrot", "-o", screenshot_path])
    elif subprocess.call(["which", "import"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        subprocess.call(["import", "-window", "root", screenshot_path])
    else:
        screenshot_path = None
except Exception as e:
    screenshot_path = None

# Verificar si hay rostro autorizado en el frame
import face_recognition
face_detected = face_auth.verify_face(frame)
# Convertir el frame a RGB para face_recognition
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
face_locations = face_recognition.face_locations(rgb_frame)
cv2.imwrite("/tmp/intruso_sudo.jpg", frame)
if len(face_locations) == 0:
    # No se detectó ningún rostro
    if screenshot_path and os.path.exists(screenshot_path):
        notifier.send_alert("⚠️ ¡SUDO ejecutado sin rostro detectado! (pantalla adjunta)", screenshot_path)
    else:
        notifier.send_alert("⚠️ ¡SUDO ejecutado sin rostro detectado! (no se pudo capturar pantalla)")
elif not face_detected:
    # Hay rostro pero no autorizado
    if screenshot_path and os.path.exists(screenshot_path):
        notifier.send_alert("🚨 ¡SUDO ejecutado por posible intruso! (foto y pantalla)", "/tmp/intruso_sudo.jpg")
        notifier.send_alert("🖥️ Captura de pantalla al ejecutar sudo", screenshot_path)
    else:
        notifier.send_alert("🚨 ¡SUDO ejecutado por posible intruso!", "/tmp/intruso_sudo.jpg")

