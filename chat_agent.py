from llama_cpp import Llama
from collections import deque

class ChatAgent:
    def __init__(self, model_path, memory_agent=None):
        self.model = Llama(model_path=model_path, n_ctx=2048, n_threads=8)
        self.short_term_memory = deque(maxlen=20)  # Initialize short-term memory queue
        self.memory_agent = memory_agent  # Optional: pass a memory agent, or None

    def build_prompt(self, user_input):
        # Add current user input to short-term memory
        self.short_term_memory.append(f"User: {user_input}")
        
        # Build prompt from recent chat history + current input for AI response
        prompt_context = "\n".join(self.short_term_memory) + "\nAI:"
        return prompt_context

    def chat(self, user_input):
        prompt = self.build_prompt(user_input)
        output = self.model(prompt, max_tokens=150, stop=["User:", "AI:"])
        response = output['choices'][0]['text'].strip()
        self.short_term_memory.append(f"AI: {response}")
        
        # Save dialogue snippet (prompt + response) to long-term memory if memory_agent is provided
        if self.memory_agent:
            self.memory_agent.store_memory(data=prompt + "\n" + response, data_type="dialogue")

        return response
