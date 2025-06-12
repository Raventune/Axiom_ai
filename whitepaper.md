

# The Axiom AI Method  
### Resonance-Based Intelligence Architecture  
**By Raven Wilson**

---

## Overview

The Axiom AI Method is a modular, resonance-driven approach to artificial intelligence inspired by biological, emotional, and energetic systems. It emphasizes timing, internal memory, and adaptive thresholds to create a more lifelike decision-making process.

This repository contains the foundational components of the system:

- `resonant_ai.py`: An agent that uses resonance to decide when to act.
- `memory_agent.py`: A hybrid memory system for logging, decaying, and analyzing events and states.

---

## Philosophy

Modern AI often acts the moment a stimulus arrives. The Axiom Method challenges that. It introduces the concept of **resonance** — a measure of internal alignment across memory, timing, and relevance. Instead of reacting instantly, the AI **waits** for the right moment to act. This creates a more organic intelligence with real-time introspection, pacing, and priority awareness.

The **"Sacred Moment"** is when all internal and external signals align perfectly — a rare but critical threshold where the AI may act decisively. However, most actions emerge when the internal resonance score merely crosses a programmable **threshold**, allowing the system to remain dynamic and responsive.

---

## Structure

/axiom_ai/
├── resonant_ai.py # ResonantAgent class: controls when to act
├── memory_agent.py # MemoryAgent class: manages short and long-term memory
├── requirements.txt # Dependencies
└── README.md # This document


---

## Modules

### `resonant_ai.py`

This module evaluates actions based on time, memory influence, and resonance thresholds. It also integrates real-world and astronomical data like moon phase and solar activity to simulate ambient conditions.

Key Components:
- `calculate_resonance_score()`: Weighted combination of memory, randomness, and external influences.
- `should_act()`: Decides if an action should occur based on resonance and internal threshold.
- Dynamic threshold that adapts based on memory success/failure history.

> **Pseudocode:**  
> `if resonance_score >= threshold: act() else: wait_and_adjust()`

memory_agent.py

A flexible, decaying memory system that logs both:

    Vector Memories — decaying float arrays.

    Event Logs — timestamped dictionary entries with weights and metadata.

Features:

    Reinforcement and decay of individual memories

    Weighted success/failure tracking

    Event histograms and summaries

    CSV saving and loading

This system is designed to be scalable and modular, functioning like a lightweight, programmable filesystem for storing AI-relevant state.
Example Usage
Resonant Agent

from resonant_ai import ResonantAgent
from memory_agent import MemoryAgent

mem = MemoryAgent()
resonant = ResonantAgent(mem)

if resonant.should_act():
    print("Resonance threshold met. Acting.")
else:
    print("Still waiting...")

Memory Agent

from memory_agent import MemoryAgent
import numpy as np

mem = MemoryAgent()
vec = np.array([0.2, 0.4, 0.1, 0.9, 0.3])
mem.store_memory(vec)

mem.log_event("check", "success", weight=0.8)
summary = mem.get_event_summary()
print(summary)

Requirements

Install dependencies with:

pip install -r requirements.txt

requirements.txt:

numpy
requests

Licensing
Repository Code License: MIT

This codebase (resonant_ai.py, memory_agent.py, and all supporting scripts) is released under the MIT License. You may use, modify, and distribute it freely.
White Paper License: CC BY 4.0

This document, The Axiom AI Method: Resonance-Based Intelligence Architecture, by Raven Wilson, is licensed under the Creative Commons Attribution 4.0 International License.

You are free to:

    Share — copy and redistribute the material in any medium or format

    Adapt — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:

    Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. Attribution should credit: Raven Wilson as the creator of the Axiom AI Method.

Acknowledgments

This project was developed in collaboration with ChatGPT, used as a cognitive partner and code assistant throughout the design and writing process.
Future Work

    Integration with visual memory (image metadata storage)

    Audio/voice inputs for narrative understanding

    Reinforcement learning-based resonance adaptation

    Long-form memory chunking across sessions

Contact

For questions, academic collaboration, or contributions:
Raven Wilson
GitHub Repo
