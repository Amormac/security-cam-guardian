import os
import face_recognition
from pathlib import Path
import cv2
import numpy as np

class FaceAuth:
    def __init__(self, known_faces_dir):
        self.known_encodings = []
        self.known_faces_dir = Path(known_faces_dir)
        
        if not self.known_faces_dir.exists():
            raise FileNotFoundError(
                f"ERROR: Directorio de rostros conocidos no encontrado en: {self.known_faces_dir}\n"
                f"Solución: Crea el directorio y añade imágenes JPG/PNG de rostros autorizados"
            )
        self.load_known_faces()

    def load_known_faces(self):
        valid_extensions = ('.jpg', '.jpeg', '.png')
        for filename in os.listdir(self.known_faces_dir):
            if filename.lower().endswith(valid_extensions):
                try:
                    image = cv2.imread(str(self.known_faces_dir / filename))
                    if image is None:
                        print(f"Advertencia: No se pudo leer {filename} (formato o ruta inválida)")
                        continue
                    # Para registro, NO preprocesar, usar imagen original
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    encodings = face_recognition.face_encodings(rgb_image)
                    if encodings:
                        self.known_encodings.append(encodings[0])
                        print(f"Rostro cargado: {filename}")
                    else:
                        print(f"Advertencia: No se detectó rostro en {filename}")
                except Exception as e:
                    print(f"Advertencia: No se pudo procesar {filename}: {str(e)}")

    def verify_face(self, frame, debug=False):
        """Verifica rostros con preprocesamiento"""
        if not self.known_encodings:
            raise ValueError("No hay rostros conocidos cargados")
        processed = self.preprocess_image(frame)
        rgb_frame = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if debug:
            print(f"Rostros detectados en frame: {len(face_encodings)}")
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_encodings, encoding, tolerance=0.55)  # Más permisivo
            if debug:
                print(f"Coincidencias: {matches}")
            if any(matches):
                return True
        return False

    def is_camera_covered(self, frame, threshold):
        """Detecta si la cámara está tapada basándose en el brillo promedio"""
        if frame is None:
            return True
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = cv2.mean(gray)[0]
        return avg_brightness < threshold

    def preprocess_image(self, image):
        """Mejora el contraste y normaliza la iluminación"""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        limg = cv2.merge([clahe.apply(l), a, b])
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    def add_known_face(self, frame):
        """Añade un nuevo rostro conocido desde un frame"""
        # Para registro, NO preprocesar, usar imagen original
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_frame)
        if encodings:
            self.known_encodings.append(encodings[0])
            return True
        return False

# Utilidad para evitar ejecución infinita en pruebas
if __name__ == "__main__":
    import time
    fa = FaceAuth("../config/known_faces")
    cap = cv2.VideoCapture(0)
    print("Presiona 'q' para salir.")
    count = 0
    while count < 100:  # Limita a 100 iteraciones
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar frame")
            break
        result = fa.verify_face(frame, debug=True)
        print(f"¿Autorizado?: {result}")
        count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.1)
    cap.release()
    print("Fin de prueba.")