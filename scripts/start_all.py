import subprocess
import signal
import sys
import time
from pathlib import Path
from collections import deque
from threading import Thread

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]

PRODUCER_CMD = [
    sys.executable,
    str(BASE_DIR / "src/fraud_detection/preprocess/simulate_event_stream.py"),
]

METRICS_CMD = [
    sys.executable,
    str(BASE_DIR / "src/fraud_detection/metrics_service/consumer_metrics.py"),
]

processes = []


def stream_preview(process, name, max_lines=15):
    lines = deque(maxlen=max_lines)

    for line in iter(process.stdout.readline, ""):
        if not line:
            break
        lines.append(line.rstrip())

    print(f"\n--- {name} (preview) ---")
    for l in lines:
        print(l)
    print(f"--- end {name} ---\n")


def start_process(cmd, name):
    print(f"[START] {name}")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    processes.append((name, process))

    t = Thread(
        target=stream_preview,
        args=(process, name),
        daemon=True,
    )
    t.start()

    return process


def shutdown():
    print("\n[STOP] Shutting down all services...")
    for name, process in processes:
        try:
            print(f" - stopping {name}")
            process.terminate()
        except Exception:
            pass

    time.sleep(2)

    for _, process in processes:
        try:
            if process.poll() is None:
                process.kill()
        except Exception:
            pass

    print("[STOP] All services stopped")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, lambda s, f: shutdown())
    signal.signal(signal.SIGTERM, lambda s, f: shutdown())

    print("== Starting DEV pipeline ==")

    start_process(PRODUCER_CMD, "Kafka event simulator")
    time.sleep(2)

    start_process(METRICS_CMD, "Metrics consumer")
    time.sleep(2)

    print("\n== Servicios lanzados correctamente ==")
    print("Press Ctrl+C to stop\n")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
