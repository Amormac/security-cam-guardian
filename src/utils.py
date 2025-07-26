import logging

def setup_logger(log_path):
    try:
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)
    except PermissionError:
        print(f"⚠️ No se pudo escribir en {log_path}. Usando consola...")
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

def capture_screenshot(output_path):
    import subprocess
    subprocess.run(["scrot", output_path])