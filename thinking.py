from llama_cpp import Llama
from collections import deque
import time

class TinyLlamaSummarizer:
    def __init__(self, model_path, max_tokens=512, n_threads=8):
        self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=n_threads)
        self.max_tokens = max_tokens

    def summarize(self, text):
        if not text.strip():
            return ""
        prompt = f"Summarize the following text briefly:\n\n{text}\n\nSummary:"
        output = self.llm(prompt, max_tokens=self.max_tokens, stop=["\n"])
        summary = output['choices'][0]['text'].strip()
        return summary


class InnerMonologueAgent:
    def __init__(self, model_path, max_tokens=512, n_threads=8):
        self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=n_threads)
        self.max_tokens = max_tokens
        self.monologue_memory = deque(maxlen=20)

    def think(self, initial_input, max_cycles=5, timeout=15):
        self.monologue_memory.clear()
        self.monologue_memory.append(f"User: {initial_input}")

        cycle = 0
        start_time = time.time()
        last_response = None

        while cycle < max_cycles and (time.time() - start_time) < timeout:
            prompt = "\n".join(self.monologue_memory) + "\nAI:"
            output = self.llm(prompt, max_tokens=self.max_tokens, stop=["User:", "AI:"])
            response = output['choices'][0]['text'].strip()

            self.monologue_memory.append(f"AI: {response}")
            last_response = response
            cycle += 1

            if "FINAL DECISION" in response.upper():
                break

        return last_response