# Axiom_ai

Axiom_ai is a modular AI framework inspired by cognitive resonance and memory systems. It features key components such as a **Resonant Agent** — an AI decision-maker guided by internal and external resonances — and a **Memory Agent** that stores and manages multi-format memories and event logs with weighted importance and decay.

This project aims to provide a scalable, extensible base for advanced AI agents that simulate nuanced decision-making and adaptive memory, useful for AI-driven storytelling, autonomous agents, and experimental AI architectures.

---

## Philosophy

Axiom_ai is grounded in the concept of *resonance* — the alignment of internal states with external stimuli to trigger meaningful action. The Resonant Agent evaluates multiple factors such as celestial influences, historical success, and real-time sensory data to decide when to act.

Memory is treated as a dynamic, decaying system capable of storing diverse data formats, including numerical vectors, text narratives, and images with associated metadata. This is designed to simulate an AI’s evolving knowledge base and contextual awareness, with programmable weights reflecting importance or confidence.

Together, these agents aim to mimic a cognitive system that balances long-term memory, real-time data processing, and nuanced decision thresholds, creating a foundation for emergent intelligence.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Raventune/Axiom_ai.git
   cd Axiom_ai

    (Optional but recommended) Create a virtual environment:

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

Usage Examples
ResonantAgent Example

from resonant_ai import ResonantAgent

# Initialize agent
agent = ResonantAgent()

# Run a decision cycle
result = agent.run_cycle()

print("Cycle result:", result)
print("Current resonance threshold:", agent.threshold)

MemoryAgent Example

from memory_agent import MemoryAgent
import numpy as np

memory = MemoryAgent(capacity=100, decay_rate=0.01)

# Store a sample memory vector
sample_vector = np.array([0.1, 0.5, 0.3, 0.7, 0.2])
memory.store_memory(sample_vector)

# Log a success event with weight
memory.log_event(event_type="interaction", detail="success", weight=1.5)

# Retrieve recent events from last 5 minutes
events = memory.get_recent_events(window_seconds=300)
print(f"Recent events: {events}")

# Save event log to CSV
memory.save_event_log_csv("event_log.csv")

API Overview
ResonantAgent (resonant_ai.py)

    run_cycle(): Performs one decision evaluation cycle based on resonance inputs.

    set_threshold(value): Adjusts the threshold for triggering actions.

    get_resonance_score(): Computes the current resonance score based on factors like moon phase and past success.

MemoryAgent (memory_agent.py)

    store_memory(memory_vector): Adds a numerical memory vector to the memory bank.

    recall_memories(): Returns decayed memory vectors.

    log_event(event_type, detail, weight): Adds a timestamped event with an importance weight.

    get_recent_events(window_seconds): Returns events within a specified time window.

    save_event_log_csv(filename): Exports event logs as a CSV file.

    weighted_success_failure_ratio(window_seconds): Returns a weighted ratio of recent successes vs failures, useful for feedback loops.

Development

Contributions are welcome! If you'd like to contribute:

    Fork the repository.

    Create a feature branch (git checkout -b feature-name).

    Commit your changes (git commit -m "Add feature").

    Push to your branch (git push origin feature-name).

    Open a Pull Request.

Please ensure code style consistency and provide tests where applicable.
Requirements

Dependencies are listed in requirements.txt. Key libraries include:

    numpy for numerical operations

    requests for external data fetching (e.g., celestial data)

    Other dependencies as needed for extended modules

Install all dependencies with:

pip install -r requirements.txt

## Acknowledgments

This project was developed with the assistance of ChatGPT, an AI language model by OpenAI, which helped generate code snippets, documentation, and design ideas.


License

This project is licensed under the MIT License. See the LICENSE file for details.
Contact

For questions or discussions, please open an issue or contact Raven Wilson.

Thank you for exploring Axiom_ai!


