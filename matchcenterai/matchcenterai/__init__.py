import os
import yaml
import pyaudio
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Set

from blogger import test
from summarizer import start as start_summarizer, stop as stop_summarizer

app = FastAPI()

OPPONENT = "Ajax"
FILE_NAME_FORMAT = "feyenoord-{opponent_lower}_{date}.yaml"
OUTPUT_AUDIO = os.getenv("OUTPUT_AUDIO")
USE_EXAMPLE_AUDIO = os.getenv("USE_EXAMPLE_AUDIO")
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

summarizer_running = False
websocket_clients: Set[WebSocket] = set()
summaries = []
logs = []

app = FastAPI()

# List of allowed origins (for development, use "*" to allow all origins, but restrict in production)
origins = [
    "http://localhost",
    "http://localhost:3333",
    # "http://yourdomain.com",  # Add your allowed origins
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/status")
def read_status():
    return {"status": "ok"}

# Run the server with: uvicorn filename:app --reload

def log(message):
    print("LOGGED: " + message)
    logs.append(message)

def load_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            if data is None:
                return []
            return data
    except FileNotFoundError:
        return []


def add_entry(entry):
    file_name = FILE_NAME_FORMAT.format(
        opponent_lower=OPPONENT.lower(),
        date=datetime.now().strftime('%Y-%m-%d')
    )
    data = load_yaml(file_name)

    data.append(entry)

    with open(file_name, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)


async def send_output(client: WebSocket, output: dict):
    # Check to make sure, as client can be remove while iterating
    if client in websocket_clients:
        try:
            await client.send_json(output)
        except WebSocketDisconnect:
            websocket_clients.remove(client)
        except Exception as e:
            client.send_text(f"Error sending JSON: {e}")

def on_output(output: str):
    # add_entry(output)
    summaries.append(output)
    log("Received output")
    if websocket_clients:
        # Copy websocket_clients to avoid RuntimeError: Set changed size during iteration
        for client in list(websocket_clients):
            asyncio.run(send_output(client, output))

def on_stop(message: str):
    global summarizer_running

    summarizer_running = False
    log("Summarizer stopped with error: " + message)
    for client in websocket_clients:
        client.send_text(message)
        client.close()
        websocket_clients.remove(client)

# Respond to health check, necessary for Coolify
@app.get("/")
async def health_check():
    return {"status": "ok"}

# Check if summarizer is running
@app.get("/checkrunning")
async def check_running():
    return {"status": "running" if summarizer_running else "stopped"}

# Get logs
@app.get("/logs")
async def get_logs():
    # Get the last 50 logs
    return logs[-50:]

@app.post("/start")
async def start_summarizer_endpoint():
    global summarizer_running
    test()

    audio = os.path.join(PACKAGE_DIR, "audio.mp3") if USE_EXAMPLE_AUDIO else "http://d2e9xgjjdd9cr5.cloudfront.net/icecast/rijnmond/radio-mp3"

    if not summarizer_running:
        if OUTPUT_AUDIO == "true":
            p = pyaudio.PyAudio()
            index = p.get_default_output_device_info().get('index')
            start_summarizer(OPPONENT, on_output, on_stop, audio, index)
        else:
            start_summarizer(OPPONENT, on_output, on_stop, audio)
        summarizer_running = True
        log("Summarizer started")
        return {"message": "Summarizer started"}
    else:
        return {"message": "Summarizer is already running"}


@app.get("/summaries")
async def get_summaries():
    return summaries

@app.post("/stop")
async def stop_summarizer_endpoint():
    global summarizer_running
    if summarizer_running:
        stop_summarizer()
        summarizer_running = False
        log("Summarizer stopped")
    else:
        return {"message": "Summarizer is not running"}


@app.websocket("/updates")
async def updates_websocket(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # Adjust the sleep time as needed
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)
    finally:
        websocket_clients.remove(websocket)

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")

