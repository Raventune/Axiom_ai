import json
import os
import time
from datetime import datetime
from memory_agent import MemoryAgent
from chat_agent import ChatAgent  # import your new chat agent class
from thinking import InnerMonologueAgent  # New: separate summarizer and monologue
from perception_interface import PerceptionInterface
from emotion_agent import EmotionAgent
from resonant_ai import ResonantAgent
import atexit
import signal
import sys


TRIGGER_CHAR = "\uE000"

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
        #self.monologue_seed_prompt = self.load_seed_as_prompt(monologue_seed_path)
        self.max_tokens = 2048
        self.memory_path = memory_path
        self.memory_log = self.load_memory()
        self.memory_agent = MemoryAgent()
        self.resonant_agent = ResonantAgent()
        self.emotion_agent = EmotionAgent(memory_agent=self.memory_agent)

        # Use raw string for Windows path or replace \ with /
        self.chat_agent = ChatAgent(
            model_path=r"models\openhermes\openhermes-2.5-mistral-7b.Q4_K_S.gguf",
            max_tokens=self.max_tokens
        )


        self.inner_monologue_agent = InnerMonologueAgent(
            model_path=r"models\tinyllama\tinyllama-1.1b-chat-v0.4.q2_k.gguf"
        )

        self.inner_monologue_active = False
        self.inner_monologue_seed_sent = False
        self.max_inner_cycles = max_inner_cycles
        self.inner_cycle_timeout = inner_cycle_timeout
        self.perception = PerceptionInterface()
        self.initial_prompt_sent = False
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
    
    def process_inner_task(self, prompt, mode='monologue'):
        if mode == 'monologue':
            thoughts = self.inner_monologue_agent.think(prompt)
            self.memory_agent.store_memory(thoughts, data_type="inner_monologue")
            return thoughts
        else:
            raise ValueError(f"Unknown mode {mode} for process_inner_task")



                
    def preprocess_input(self, user_input):
        if user_input.startswith(TRIGGER_CHAR):
            return user_input[1:].strip(), True
        return user_input.strip(), False


    
    def tag_input(self, user_input):
        tags = []
        lowered = user_input.lower()

        if "remember" in lowered or "can you save" in lowered:
            tags.append("memory_request")

        if "how do you feel" in lowered or "do you feel" in lowered:
            tags.append("emotional_probe")

        if "why did you" in lowered or "why would you" in lowered:
            tags.append("reflective_prompt")

        return tags  # you should return tags here

    def process_input(self, user_input: str, trigger_inner=False) -> str:

        # Run resonance cycle
        resonant_result = self.resonant_agent.run_cycle()
        resonance_score = resonant_result.get("score", 0)
        sacred_moment = resonant_result.get("sacred_moment", False)

        # Update emotion agent
        current_emotion = self.emotion_agent.update_from_resonance(resonance_score, sacred_moment)
        emotion_vector = self.emotion_agent.emotion_vector()

        # Build emotion context string
        emotion_context = f"Emotional state: {current_emotion}. Emotion levels: {emotion_vector}"

        # Fetch recent memory snippets (last 5 messages)
        memory_snippets = "\n".join(
            [f"[{m['timestamp']}] {m['role'].capitalize()}: {m['content']}" for m in self.memory_log[-5:]]
        )

        # Fetch recent personality snippets (long-term memory)
        personality_snippets = self.fetch_recent_personality_snippets()

        if not self.initial_prompt_sent:
            # Send full seed + memory + user input for first prompt
            combined_prompt = (
                self.seed_prompt
                + "\n\nSHORT-TERM MEMORY:\n" + memory_snippets
                + "\n\nLONG-TERM MEMORY SNIPPETS:\n" + personality_snippets
                + "\n\nUser: " + user_input
            )
            self.initial_prompt_sent = True
        else:
            # For subsequent prompts, just send emotion + user input
            combined_prompt = "User: " + user_input

        # Combine emotion context and combined prompt for final input
        full_prompt = emotion_context + "\n\n" + combined_prompt

        # Generate response depending on trigger
        try:
            if trigger_inner:
                print("[DEBUG] Inner monologue response triggered.")
                response = self.inner_monologue_agent.run(full_prompt)
            else:
                response = self.chat_agent.chat(full_prompt)
            response = response.replace("Assistant:", "Axiom AI:").strip()
        except Exception as e:
            return f"Error generating response: {e}"

        # Store full interaction in memory
        self.memory_log.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": user_input
        })
        self.memory_log.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": response
        })
        self.save_memory()

            # Store chat + emotional metadata
        self.memory_agent.store_tagged_memory(
            tag="chat",
            data={"user_input": user_input, "ai_response": response},
            metadata={"emotion": current_emotion, "resonance_score": resonance_score, "sacred_moment": sacred_moment}
        )

            # If monologue triggered, run it now
        if trigger_inner:
            self.inner_monologue_active = True
            inner_response = self.run_inner_monologue(response, mode='monologue')
            self.inner_monologue_active = False
            self.memory_log.append({
                "timestamp": datetime.now().isoformat(),
                "role": "inner_monologue",
                "content": inner_response
            })
            self.save_memory()
            return f"{response}\n\n[Inner Monologue]\n{inner_response}"

        return response


    def save_on_exit(self):
        print("Saving memories before exit...")
        try:
            self.memory_agent.save_index()  # Save memory index JSON
            self.memory_agent._flush_text_log_batch()  # Flush any pending text logs
            self.memory_agent.save_dialogue_memory()  # If you use this for dialogue memory
        except Exception as e:
            print(f"Error during save_on_exit: {e}")
    def reset_session(self):
        self.initial_prompt_sent = False
        self.memory_log.clear()  # optional: clear short-term memory if needed
        # Any other reset logic here

if __name__ == "__main__":
    dispatcher = AxiomDispatcher()

    print("Axiom AI Dispatcher with Local ChatAgent Ready.")
    print("Type 'exit' or 'quit' to stop. Inner monologue is only available thru programming.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break

        user_input, trigger_inner = dispatcher.preprocess_input(user_input)
        dialogue_response = dispatcher.process_input(user_input, trigger_inner=trigger_inner)
        print("Axiom AI:", dialogue_response)
        



def signal_handler(sig, frame):
    dispatcher.save_on_exit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

atexit.register(dispatcher.save_on_exit)
