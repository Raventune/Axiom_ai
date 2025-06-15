from llama_cpp import Llama
from collections import deque

class ChatAgent:
    def __init__(self, model_path, max_history=20, max_tokens=2048):
        self.model = Llama(model_path=model_path, n_ctx=max_tokens, n_threads=8)
        self.max_tokens = max_tokens

    def chat(self, combined_prompt):
        # Optionally truncate combined_prompt if too long (based on token or word count)
        # You can add truncation here if needed
        
        output = self.model(combined_prompt, max_tokens=150)
        response = output['choices'][0]['text'].strip()

        # Extract the latest user input from combined_prompt to add to memory
        # This is optional and depends on how you want to log
        # For example, grab the last line starting with "User:"
        last_user_line = None
        for line in reversed(combined_prompt.splitlines()):
            if line.startswith("User:"):
                last_user_line = line[len("User:"):].strip()
                break

        return response