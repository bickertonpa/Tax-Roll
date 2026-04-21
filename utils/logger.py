from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def set_log_file(log_file_path):
    global LOG_FILE
    LOG_FILE = Path(log_file_path)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
def log_result(level, method, message="", **kwargs):
    global LOG_FILE
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Clean message
    message = _clean_message(message)


    # Format key=value pairs (skip None)``
    kv = " ".join(f"{k}={v}" for k, v in kwargs.items() if v is not None)

    # Base prefix
    log_line = f"[{timestamp}][{level}][{method.upper()}]"

    # Add key-value pairs if present
    if kv:
        log_line += f" {kv}"

    # Add message only if not None or empty
    if message:
        log_line += f" | Message: {message}"

    print(log_line)

    if LOG_FILE is not None:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
                f.flush()

def _clean_message(msg):
    if msg is None:
        return None
    return str(msg).replace("\n", " ").replace("\r", " ").strip()