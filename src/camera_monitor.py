import cv2
import time
import yaml
from face_auth import FaceAuth
from telegram_notifier import TelegramNotifier
from utils import setup_logger

# Configuración
with open("/home/ariel/Documentos/ARIEL/INTERACCIÓN HUMANO COMPUTADOR/security-cam-guardian/config/config.yaml") as f:
    config = yaml.safe_load(f)

logger = setup_logger(config["security"]["log_path"])
notifier = TelegramNotifier(config["telegram"]["token"], config["telegram"]["chat_id"])

from pathlib import Path
KNOWN_FACES_DIR = Path(__file__).parent.parent / "config" / "known_faces"
face_auth = FaceAuth(KNOWN_FACES_DIR)

def main():
    cap = cv2.VideoCapture(0)
    intruso_reportado = False
    camara_tapada_reportada = False
    esperar_frame_valido = False
    logger.info(f"Umbral de oscuridad: {config['camera']['darkness_threshold']}")
    logger.info(f"Umbral de reconocimiento: {config['camera']['recognition_brightness_threshold']}")

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Cámara no disponible")
            notifier.send_alert("⚠️ Cámara desconectada o tapada")
            time.sleep(config["camera"]["check_interval"])
            continue

        avg_brightness = cv2.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))[0]
        camara_cubierta = face_auth.is_camera_covered(frame, config["camera"]["darkness_threshold"])
        logger.info(f"Brillo promedio: {avg_brightness:.2f} | Cámara cubierta: {camara_cubierta}")

        # Detectar transición de estado de cámara tapada
        if camara_cubierta:
            if not camara_tapada_reportada:
                logger.warning("Cámara tapada")
                notifier.send_alert("🚨 Cámara tapada")
                camara_tapada_reportada = True
            intruso_reportado = False
            esperar_frame_valido = True
            time.sleep(config["camera"]["check_interval"])
            continue
        else:
            if camara_tapada_reportada:
                camara_tapada_reportada = False
                intruso_reportado = False
                esperar_frame_valido = True
                logger.info("Cámara destapada, esperando frame válido")

        # Saltar el primer frame tras destapar la cámara
        if esperar_frame_valido:
            esperar_frame_valido = False
            time.sleep(config["camera"]["check_interval"])
            continue

        # Reconocimiento facial solo si la cámara no está tapada y el frame tiene suficiente brillo
        if avg_brightness > config["camera"]["recognition_brightness_threshold"]:
            if not face_auth.verify_face(frame):
                if not intruso_reportado:
                    logger.warning("Intruso detectado")
                    cv2.imwrite("intruso.jpg", frame)
                    notifier.send_alert("🚨 ¡Intruso detectado!", "intruso.jpg")
                    intruso_reportado = True
            else:
                intruso_reportado = False
        else:
            logger.info("Frame demasiado oscuro para reconocimiento facial")
            intruso_reportado = False

        logger.info(f"Estado: cámara_tapada_reportada={camara_tapada_reportada}, intruso_reportado={intruso_reportado}, esperar_frame_valido={esperar_frame_valido}")
        time.sleep(config["camera"]["check_interval"])

if __name__ == "__main__":
    main()