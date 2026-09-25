#!/usr/bin/env python3
"""
DAKSH Unified Startup & Validation Script
Starts all 5 authoritative document screening services and the central DAKSH backend.
Performs real HTTP readiness and dependency checks.
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
import urllib.request
import urllib.error
import json

ROOT_DIR = Path(__file__).resolve().parent.parent

SERVICES = [
    {
        "id": "aadhaar",
        "name": "Aadhaar service",
        "port": 8001,
        "cwd": ROOT_DIR / "modules" / "aadhaar" / "backend",
        "cmd": [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"],
        "health_url": "http://127.0.0.1:8001/api/health",
        "requires_tesseract": False,
    },
    {
        "id": "passport",
        "name": "Passport service",
        "port": 8002,
        "cwd": ROOT_DIR / "modules" / "passport" / "backend",
        "cmd": [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8002"],
        "health_url": "http://127.0.0.1:8002/api/health",
        "requires_tesseract": False,
    },
    {
        "id": "visa",
        "name": "Visa service",
        "port": 5000,
        "cwd": ROOT_DIR / "modules" / "visa" / "backend",
        "cmd": [sys.executable, "app.py"],
        "health_url": "http://127.0.0.1:5000/api/health",
        "requires_tesseract": True,
    },
    {
        "id": "dl",
        "name": "Driving Licence service",
        "port": 8004,
        "cwd": ROOT_DIR / "modules" / "driving-licence" / "backend",
        "cmd": [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8004"],
        "health_url": "http://127.0.0.1:8004/api/health",
        "requires_tesseract": True,
    },
    {
        "id": "pan",
        "name": "PAN service",
        "port": 8005,
        "cwd": ROOT_DIR / "modules" / "pan" / "backend",
        "cmd": [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8005"],
        "health_url": "http://127.0.0.1:8005/api/health",
        "requires_tesseract": True,
    },

    {
        "id": "daksh-backend",
        "name": "DAKSH backend",
        "port": 8000,
        "cwd": ROOT_DIR / "daksh-backend",
        "cmd": [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        "health_url": "http://127.0.0.1:8000/api/health",
        "requires_tesseract": False,
    },
]


def check_tesseract() -> tuple[bool, str]:
    tesseract_env = os.environ.get("TESSERACT_CMD")
    if tesseract_env and os.path.exists(tesseract_env):
        return True, tesseract_env
    default_win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(default_win_path):
        return True, default_win_path
    which_path = shutil.which("tesseract")
    if which_path:
        return True, which_path
    return False, f"Tesseract executable not found at '{default_win_path}' or in PATH"


def is_service_ready(url: str, timeout: float = 1.0) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DAKSH-Startup-Check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def start_services(wait_seconds: int = 15):
    has_tesseract, tesseract_msg = check_tesseract()
    print("==================================================")
    print("       DAKSH SYSTEM STARTUP & VALIDATION         ")
    print("==================================================")
    print(f"Tesseract Status: {'AVAILABLE (' + tesseract_msg + ')' if has_tesseract else 'NOT INSTALLED — ' + tesseract_msg}")
    print("--------------------------------------------------")

    processes = []

    for svc in SERVICES:
        url = svc["health_url"]
        port = svc["port"]
        name = svc["name"]

        # Check if already running
        if is_service_ready(url):
            print(f"[OK] {name} already running on port {port}")
            continue

        if not svc["cwd"].exists():
            print(f"[FAIL] {name} directory missing: {svc['cwd']}")
            continue

        env = os.environ.copy()
        env["PYTHONPATH"] = str(svc["cwd"])
        if has_tesseract:
            env["TESSERACT_CMD"] = tesseract_msg

        print(f"Launching {name} on port {port}...")
        try:
            proc = subprocess.Popen(
                svc["cmd"],
                cwd=str(svc["cwd"]),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            processes.append((svc, proc))
        except Exception as exc:
            print(f"[FAIL] {name} failed to launch: {exc}")

    # Wait for services to become ready
    print("\nWaiting for services to report HTTP readiness...")
    start_time = time.time()
    ready_status = {}

    while time.time() - start_time < wait_seconds:
        all_done = True
        for svc in SERVICES:
            sid = svc["id"]
            if ready_status.get(sid) is True:
                continue
            if is_service_ready(svc["health_url"]):
                ready_status[sid] = True
            else:
                all_done = False
        if all_done:
            break
        time.sleep(0.5)

    print("\n--------------------------------------------------")
    print("            FINAL SERVICE STATUS REPORT           ")
    print("--------------------------------------------------")
    for svc in SERVICES:
        sid = svc["id"]
        name = svc["name"]
        port = svc["port"]

        if ready_status.get(sid):
            print(f"[OK] {name} started on port {port}")
        else:
            if svc["requires_tesseract"] and not has_tesseract:
                print(f"[NOT READY] {name} — Tesseract unavailable")
            else:
                print(f"[FAIL] {name} — service did not become ready on port {port}")

    print("==================================================")
    return processes


if __name__ == "__main__":
    procs = start_services(wait_seconds=12)
    if "--check-only" not in sys.argv:
        print("\nAll services running. Keeping process active...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping services...")
            for _, proc in procs:
                try:
                    proc.terminate()
                except Exception:
                    pass

