import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger=get_logger(__name__)

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "9999"))


def _is_port_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False

def run_backend():
    try:
        logger.info("starting backend service..")
        if not _is_port_free(BACKEND_HOST, BACKEND_PORT):
            raise CustomException(
                f"Port {BACKEND_PORT} is already in use on {BACKEND_HOST}. Stop the existing process or set BACKEND_PORT to a free port."
            )

        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.backend.api:app",
                "--host",
                BACKEND_HOST,
                "--port",
                str(BACKEND_PORT),
            ],
            check=True,
            cwd=str(REPO_ROOT),
        )
    except Exception as e:
        logger.exception("Problem with backend service")
        raise CustomException("Failed to start backend", e)
    
def run_frontend():
    try:
        logger.info("Starting Frontend service")
        ui_file = REPO_ROOT / "app" / "frontend" / "ui.py"
        if not ui_file.exists():
            raise CustomException(f"Streamlit UI file not found: {ui_file}")

        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(ui_file)],
            check=True,
            cwd=str(REPO_ROOT),
        )
    except Exception as e:
        logger.exception("Problem with frontend service")
        raise CustomException("Failed to start frontend", e)
    
if __name__=="__main__":
    try:
        threading.Thread(target=run_backend).start()
        time.sleep(2)
        run_frontend()
    
    except CustomException as e:
        logger.exception(f"CustomException occured : {str(e)}")


    
