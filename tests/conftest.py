import os
import subprocess
import time
import urllib.request
import pytest


@pytest.fixture(scope="session")
def flet_server():
    """Starts the example.py Flet application on port 8552 for UI testing."""
    port = "8552"
    url = f"http://127.0.0.1:{port}"

    # Setup environment
    env = os.environ.copy()
    env["FLET_PORT"] = port
    env["PYTHONUNBUFFERED"] = "1"

    print(f"\n[FIXTURE] Starting Flet server on {url}...")
    proc = subprocess.Popen(
        ["poetry", "run", "python", "-u", "src/design_system/example/example.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Poll server until ready
    start_time = time.time()
    success = False
    while time.time() - start_time < 10:
        try:
            urllib.request.urlopen(url, timeout=1)
            success = True
            break
        except Exception:
            time.sleep(0.5)

    if not success:
        proc.terminate()
        stdout, stderr = proc.communicate()
        raise RuntimeError(f"Flet server failed to start on port {port}.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")

    print("[FIXTURE] Flet server is ready!")
    yield url

    print("\n[FIXTURE] Terminating Flet server...")
    proc.terminate()
    try:
        proc.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
    print("[FIXTURE] Flet server terminated.")
