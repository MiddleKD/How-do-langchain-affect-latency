from pyinstrument import Profiler
from langchain_ollama.chat_models import ChatOllama

llm = ChatOllama(model="llama3.1")

def run(text):
    re = llm.invoke(text, stream=False)
    print(re.content)

if __name__ == "__main__":
    profiler = Profiler()
    profiler.start()
    run("Tell me a short joke")
    run("Tell me a short joke")
    profiler.stop()
    with open("langchain-profile.html", "w") as f:
        f.write(profiler.output_html())
