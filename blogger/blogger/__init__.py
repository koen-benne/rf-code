import os
import yaml
import pyaudio
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Set

from summarizer import start as start_summarizer, stop as stop_summarizer

app = FastAPI()

OPPONENT = "Ajax"
SUMMARIZER_RUNNING = False
FILE_NAME_FORMAT = "feyenoord-{opponent_lower}_{date}.yaml"
OUTPUT_AUDIO = os.getenv("OUTPUT_AUDIO")
USE_EXAMPLE_AUDIO = os.getenv("USE_EXAMPLE_AUDIO")
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

websocket_clients: Set[WebSocket] = set()
outputs = []

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
    try:
        await client.send_json(output)
    except WebSocketDisconnect:
        websocket_clients.remove(client)
    except Exception as e:
        client.send_text(f"Error sending JSON: {e}")

def on_output(output):
    # add_entry(output)
    outputs.append(output)
    if websocket_clients:
        print("Sending JSON")
        for client in websocket_clients:
            # asyncio.run_coroutine_threadsafe(send_output(client, output), event_loop)
            asyncio.run(send_output(client, output))

# Respond to health check, necessary for Coolify
@app.get("/")
async def health_check():
    return {"status": "ok"}

@app.post("/start")
async def start_summarizer_endpoint():
    global SUMMARIZER_RUNNING

    audio = os.path.join(PACKAGE_DIR, "audio.mp3") if USE_EXAMPLE_AUDIO else "http://d2e9xgjjdd9cr5.cloudfront.net/icecast/rijnmond/radio-mp3"

    if not SUMMARIZER_RUNNING:
        if OUTPUT_AUDIO == "true":
            p = pyaudio.PyAudio()
            index = p.get_default_output_device_info().get('index')
            start_summarizer(OPPONENT, on_output, audio, index)
        else:
            start_summarizer(OPPONENT, on_output, audio)
        SUMMARIZER_RUNNING = True
        return {"message": "Summarizer started"}
    else:
        return {"message": "Summarizer is already running"}


@app.get("/results")
async def get_results():
    return outputs

@app.post("/stop")
async def stop_summarizer_endpoint():
    global SUMMARIZER_RUNNING
    if SUMMARIZER_RUNNING:
        stop_summarizer()
        SUMMARIZER_RUNNING = False
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

