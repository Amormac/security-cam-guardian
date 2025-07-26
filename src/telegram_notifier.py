import requests
import logging

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_alert(self, message, image_path=None):
        try:
            if image_path:
                with open(image_path, "rb") as photo:
                    requests.post(
                        f"{self.base_url}/sendPhoto",
                        files={"photo": photo},
                        data={"chat_id": self.chat_id, "caption": message}
                    )
            else:
                requests.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": self.chat_id, "text": message}
                )
        except Exception as e:
            logging.error(f"Error enviando alerta: {e}")