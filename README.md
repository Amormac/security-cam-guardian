# Security Cam Guardian

Sistema de vigilancia con reconocimiento facial y alertas por Telegram.

## Instalación
1. Ejecutar `./install.sh`
2. Configurar `config/config.yaml` con tu token de Telegram y chat ID.

## Uso
- Servicio: `sudo systemctl start security-cam-guardian`
- Logs: `tail -f /var/log/security-cam-guardian.log`