import httpx
def generate_text():
    payload = {
        "prompt": "Tell me a short joke"
    }
    response = httpx.post("http://localhost:8000/generate", json=payload)

if __name__ == "__main__":
    generate_text()   