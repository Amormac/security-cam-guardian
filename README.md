# Security Cam Guardian

Sistema de monitoreo de comandos `sudo` con reconocimiento facial y alertas por Telegram.

## Objetivo

Detectar y registrar el uso de `sudo`, tomar foto con la webcam y captura de pantalla, realizar reconocimiento facial y enviar alertas por Telegram si el usuario no es autorizado o no se detecta ningún rostro.

---

## Requisitos

- **Python 3.8+**
- **OpenCV** (`opencv-python`)
- **face_recognition**
- **PyYAML**
- **Telegram Bot API** (token y chat_id)
- **gnome-screenshot** (para Wayland/GNOME)
- **scrot** o **imagemagick** (`import`) como alternativas para X11
- **Webcam funcional**
- **Linux** (probado en Fedora 42 Workstation con GNOME y Wayland)

### Instalación de dependencias

```sh
sudo dnf install python3-opencv python3-pip gnome-screenshot scrot imagemagick
pip3 install face_recognition pyyaml
```

---

## Configuración

1. **Configura el bot de Telegram**  
   Edita `config/config.yaml`:

   ```yaml
   telegram:
     token: "TU_TOKEN"
     chat_id: "TU_CHAT_ID"
   ```

2. **Agrega rostros autorizados**  
   Coloca imágenes de los rostros permitidos en `config/known_faces/`.

3. **Crea el wrapper para sudo**  
   Crea `/usr/local/bin/sudo-guardian` con:

   ```bash
   #!/bin/bash
   python3 "/ruta/completa/a/guardian_sudo_log.py"
   exec /usr/bin/sudo "$@"
   ```
   Dale permisos de ejecución:
   ```sh
   sudo chmod +x /usr/local/bin/sudo-guardian
   ```

4. **Agrega el alias a tu shell**  
   En tu `~/.bashrc` o `~/.zshrc`:
   ```sh
   alias sudo='/usr/local/bin/sudo-guardian'
   ```
   Luego ejecuta:
   ```sh
   source ~/.bashrc
   # o
   source ~/.zshrc
   ```

---

## Uso

Cada vez que ejecutes un comando con `sudo`, el sistema:
- Toma una foto con la webcam.
- Captura la pantalla del escritorio.
- Realiza reconocimiento facial.
- Si no detecta rostro autorizado, envía alerta por Telegram con la foto y la pantalla.

---

## Notas

- El sistema **no bloquea** el uso de sudo, solo monitorea y alerta.
- Si no se detecta ningún rostro, también se envía alerta.
- Si tienes problemas con la captura de pantalla en Wayland, asegúrate de tener instalado `gnome-screenshot`.

---

## Estructura del proyecto

```
security-cam-guardian/
├── config/
│   ├── config.yaml
│   └── known_faces/
├── src/
│   ├── face_auth.py
│   ├── telegram_notifier.py
├── guardian_sudo_log.py
└── /usr/local/bin/sudo-guardian
```

---

## Créditos

Desarrollado por [Tu Nombre].  
Basado en Python, OpenCV, face_recognition y Telegram Bot API.