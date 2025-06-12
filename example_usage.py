import numpy as np
from memory_agent import MemoryAgent

agent = MemoryAgent()

# Store a vector (saved as file)
agent.store_memory(np.array([1, 2, 3]), data_type="vector")

# Store a narrative text
agent.store_memory("Agent succeeded in task", data_type="text", metadata={"outcome": "success"})

# Save a text log file
agent.save_text_log("Event happened at timestamp...")

# Decay weights periodically
agent.decay_memory()

# Save/load index for persistence
agent.save_index()
agent.load_index()

# Get recent summary
print(agent.get_recent_memories_summary())


from resonant_ai import ResonantAgent

def main():
    agent = ResonantAgent(threshold=0.9)

    for cycle in range(5):
        result = agent.run_cycle()
        print(f"Cycle {cycle+1}:")
        print(f"  Resonance score: {result['score']:.3f}")
        print(f"  Patience factor: {result['patience']:.3f}")
        print(f"  Threshold: {result['threshold']:.3f}")
        print(f"  Resonance achieved: {result['resonance']}")
        print()

if __name__ == "__main__":
    main()