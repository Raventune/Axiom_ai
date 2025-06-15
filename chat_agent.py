from llama_cpp import Llama
from collections import deque

class ChatAgent:
    def __init__(self, model_path, memory_agent=None, max_history=20, max_tokens=2048):
        self.model = Llama(model_path=model_path, n_ctx=max_tokens, n_threads=8)
        self.short_term_memory = deque(maxlen=max_history*2)  # store user + AI exchanges
        self.memory_agent = memory_agent
        self.max_tokens = max_tokens

    def build_prompt(self, emotion_context, user_input):
        # Compose history string from short-term memory (chat log)
        history = "\n".join(self.short_term_memory)

        # Build full prompt with emotion context, chat history, current input
        prompt = f"{emotion_context}\n{history}\nUser: {user_input}\nAI:"

        # Optionally truncate prompt if too long — simple approach: cut oldest messages
        # For more advanced, could do token counting or summary
        while len(prompt.split()) > self.max_tokens - 200:  # leave room for response
            # Remove the oldest two entries (one user + one AI)
            if len(self.short_term_memory) >= 2:
                self.short_term_memory.popleft()
                self.short_term_memory.popleft()
                history = "\n".join(self.short_term_memory)
                prompt = f"{emotion_context}\n{history}\nUser: {user_input}\nAI:"
            else:
                break

        return prompt

    def chat(self, emotion_context, user_input):
        prompt = self.build_prompt(emotion_context, user_input)
        output = self.model(prompt, max_tokens=150, stop=["User:", "AI:"])
        response = output['choices'][0]['text'].strip()

        # Append current exchange to short-term memory
        self.short_term_memory.append(f"User: {user_input}")
        self.short_term_memory.append(f"AI: {response}")

        if self.memory_agent:
            self.memory_agent.store_memory(data=prompt + "\n" + response, data_type="dialogue")

        return response