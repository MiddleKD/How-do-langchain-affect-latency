from pyinstrument import Profiler
import httpx

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

payload = {
    "model": MODEL_NAME,
    "prompt": "Tell me a short joke",
    "stream": False
}

payload2 = {
    "model": MODEL_NAME,
    "prompt": "Tell me a short joke",
    "stream": False
}

def run():
    with httpx.Client() as client:
        response = client.post(OLLAMA_API_URL, json=payload, timeout=60)
    print(response.json().get("response", ""))
    with httpx.Client() as client:
        response = client.post(OLLAMA_API_URL, json=payload2, timeout=60)
    print(response.json().get("response", ""))

if __name__ == "__main__":
    profiler = Profiler()
    profiler.start()
    run()
    profiler.stop()
    with open("pure-profile.html", "w") as f:
        f.write(profiler.output_html())