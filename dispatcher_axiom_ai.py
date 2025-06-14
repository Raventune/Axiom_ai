import json
import os
import time
from datetime import datetime
from memory_agent import MemoryAgent
from chat_agent import ChatAgent  # import your new chat agent class
from thinking import TinyLlamaSummarizer, InnerMonologueAgent  # New: separate summarizer and monologue

class AxiomDispatcher:
    def __init__(
        self,
        seed_path="axiom_seed.json",
        monologue_seed_path="monologue_seed.json",
        memory_path="axiom_memory.json",
        max_inner_cycles=5,
        inner_cycle_timeout=15
    ):
        self.seed_prompt = self.load_seed_as_prompt(seed_path)
        self.monologue_seed_prompt = self.load_seed_as_prompt(monologue_seed_path)

        self.memory_path = memory_path
        self.memory_log = self.load_memory()
        self.memory_agent = MemoryAgent()

        # Use raw string for Windows path or replace \ with /
        self.chat_agent = ChatAgent(
            model_path=r"C:\Users\Raven\Desktop\python projects\axiom_ai\models\openhermes\openhermes-2.5-mistral-7b.Q4_K_S.gguf",
            memory_agent=self.memory_agent
        )

        self.summarizer = TinyLlamaSummarizer(
            model_path=r"models\tinyllama\tinyllama-1.1b-chat-v0.4.q2_k.gguf"
        )
        self.inner_monologue_agent = InnerMonologueAgent(
            model_path=r"models\tinyllama\tinyllama-1.1b-chat-v0.4.q2_k.gguf"
        )

        self.inner_monologue_active = False
        self.inner_monologue_seed_sent = False
        self.max_inner_cycles = max_inner_cycles
        self.inner_cycle_timeout = inner_cycle_timeout

    def load_seed_as_prompt(self, seed_path):
        try:
            with open(seed_path, "r") as f:
                seed = json.load(f)
        except FileNotFoundError:
            print(f"Seed file {seed_path} not found. Using default context.")
            return "SYSTEM: You are an AI being developed as part of the Axiom AGI project."

        prompt = "SYSTEM: This is your seed context.\n\n"
        for section, content in seed.items():
            prompt += f"## {section.upper()} ##\n"
            if isinstance(content, dict):
                for k, v in content.items():
                    prompt += f"- {k}: {v}\n"
            elif isinstance(content, list):
                for item in content:
                    prompt += f"- {item}\n"
            else:
                prompt += f"{content}\n"
            prompt += "\n"
        return prompt

    def load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r") as f:
                return json.load(f)
        return []

    def save_memory(self):
        with open(self.memory_path, "w") as f:
            json.dump(self.memory_log, f, indent=2)

    def fetch_recent_personality_snippets(self, limit=5, time_window=3600):
        memories = self.memory_agent.get_memories(data_type="text_file", time_window=time_window)
        snippets = []
        for mem in sorted(memories, key=lambda m: m.timestamp, reverse=True)[:limit]:
            try:
                with open(os.path.join(self.memory_agent.storage_dir, mem.data), "r", encoding="utf-8") as f:
                    content = f.read()
                    snippets.append(f"[{datetime.fromtimestamp(mem.timestamp)}] {content.strip()}")
            except Exception:
                continue
        return "\n".join(snippets)

    def run_inner_monologue(self, initial_dialogue_response):
        thoughts = self.inner_monologue_agent.think(initial_dialogue_response)
        self.memory_agent.store_memory(thoughts, data_type="inner_monologue")
        return thoughts

    def summarize_recent_memories(self):
        recent = self.memory_agent.get_memories(time_window=300)  # last 5 minutes
        combined = "\n".join([m.data for m in recent if m.data_type == "text"])
        if combined:
            summary = self.summarizer.summarize(combined)
            if summary:
                self.memory_agent.store_memory(summary, data_type="summary")

    def query(self, user_input, trigger_inner_monologue=False):
        memory_snippets = "\n".join([f"[{m['timestamp']}] {m['role'].capitalize()}: {m['content']}" for m in self.memory_log[-5:]])
        personality_snippets = self.fetch_recent_personality_snippets()

        combined_prompt = (
            self.seed_prompt
            + "\n\nSHORT-TERM MEMORY:\n"
            + memory_snippets
            + "\n\nLONG-TERM MEMORY SNIPPETS:\n"
            + personality_snippets
            + "\n\nUser: " + user_input
        )

        try:
            dialogue_response = self.chat_agent.chat(user_input)
        except Exception as e:
            return f"Error in local ChatAgent chat: {e}"

        self.memory_log.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": user_input
        })
        self.memory_log.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": dialogue_response
        })
        self.save_memory()

        log_entry = f"User: {user_input}\nAI: {dialogue_response}"
        self.memory_agent.save_text_log(log_entry)

        if trigger_inner_monologue:
            self.inner_monologue_active = True
            inner_response = self.run_inner_monologue(dialogue_response)
            self.inner_monologue_active = False
            self.memory_log.append({
                "timestamp": datetime.now().isoformat(),
                "role": "inner_monologue",
                "content": inner_response
            })
            self.save_memory()
            return inner_response

        self.summarize_recent_memories()
        return dialogue_response


if __name__ == "__main__":
    dispatcher = AxiomDispatcher()

    print("Axiom AI Dispatcher with Local ChatAgent Ready.")
    print("Type 'exit' or 'quit' to stop. To trigger inner monologue, prefix input with '!'.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break

        trigger_inner = user_input.startswith("!")
        if trigger_inner:
            user_input = user_input[1:].strip()

        response = dispatcher.query(user_input, trigger_inner_monologue=trigger_inner)
        print("Axiom AI:", response)
