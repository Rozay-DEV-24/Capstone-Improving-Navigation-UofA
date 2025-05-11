import subprocess
import webbrowser
import time

print("Starting FastAPI backend...")
backend_process = subprocess.Popen(
    ["uvicorn", "fastapi_chatbot_backend:app", "--reload"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# === Step 2: Wait a few seconds for backend to spin up ===
time.sleep(3)

# === Step 3: Open homepage in default browser through FastAPI server ===
webbrowser.open("http://127.0.0.1:8000")

print("🚀 UA Nav Access launched.")
