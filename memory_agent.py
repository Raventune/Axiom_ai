
---

## **memory_agent.py**

```python
"""
memory_agent.py

Defines the MemoryAgent class responsible for scalable, weighted memory management
for the AI system. Supports two primary types of memory:

1. Vector Memory:
   - Stores numeric vector representations of memories.
   - Supports decay and reinforcement mechanisms to simulate fading or strengthening
     of memories over time.
   - Provides recall and averaging functions for aggregate memory insights.

2. Event Memory:
   - Logs discrete events with timestamps, types, details, and programmable weights.
   - Supports querying recent events within a time window.
   - Implements decay on event weights to reduce importance over time.
   - Supports saving event logs to CSV for persistence and external analysis.
   - Provides summary statistics and pattern detection (histograms) on logged events.

Additionally, the MemoryAgent is designed for extensibility and scalability, allowing
integration of multi-format data (e.g., narratives, images with metadata) for rich memory
representation.

Classes:
--------
MemoryAgent
    Core memory management class supporting vector and event memories with weighted
    logging and decay.

Key Methods:
------------
- store_memory(memory_vector: np.ndarray)
    Adds a vector memory to the fixed-capacity memory bank.

- recall_memories() -> List[np.ndarray]
    Returns a list of current memories with decay applied.

- reinforce_memory(index: int)
    Strengthens a specific memory vector by increasing its weight.

- average_memory() -> np.ndarray
    Computes the average vector of all recalled memories.

- log_event(event_type: str, detail: str, weight: float = 1.0)
    Logs a weighted event with timestamp and details.

- get_recent_events(window_seconds: int = 60) -> List[dict]
    Retrieves events from the event log within a recent time window.

- decay_event_log(decay_rate: float = 0.005)
    Applies decay to event weights and purges negligible events.

- save_event_log_csv(filename: str)
    Saves the event log to a CSV file.

- get_event_summary(window_seconds: int = 300) -> dict
    Returns counts of success, failure, and other events in recent history.

- weighted_success_failure_ratio(window_seconds: int = 300) -> float
    Calculates a weighted ratio indicating success vs failure dominance.

Usage:
------
Create a MemoryAgent instance to store and query AI experiences. Use event logging
to track outcomes and vector memory to retain abstracted knowledge.

Example:
--------
```python
from memory_agent import MemoryAgent
import numpy as np

memory = MemoryAgent()
memory.store_memory(np.array([0.1, 0.2, 0.3, 0.4, 0.5]))
memory.log_event("interaction", "success", weight=2.0)
summary = memory.get_event_summary()
print(summary)

"""

import os
import time
import json
from collections import deque
import numpy as np
import uuid

class MemoryItem:
    def __init__(self, data, data_type, timestamp=None, weight=1.0, metadata=None, id=None):
        self.data = data  # Could be raw data, or filepath for files
        self.data_type = data_type  # e.g., "vector", "text", "image_file", "log_file"
        self.timestamp = timestamp or time.time()
        self.weight = weight
        self.metadata = metadata or {}
        self.id = id or str(uuid.uuid4())  # Unique ID for reference
    
    def to_dict(self):
        # Serialize for saving (note: raw numpy arrays should be saved externally)
        serializable_data = self.data
        if isinstance(self.data, np.ndarray):
            # Store vectors externally as JSON or numpy binary? For now, skip direct numpy storage
            serializable_data = None

        return {
            "id": self.id,
            "data": serializable_data,
            "data_type": self.data_type,
            "timestamp": self.timestamp,
            "weight": self.weight,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            data=d.get("data"),
            data_type=d.get("data_type"),
            timestamp=d.get("timestamp"),
            weight=d.get("weight", 1.0),
            metadata=d.get("metadata", {}),
            id=d.get("id")
        )


class MemoryAgent:
    def __init__(self, capacity=1000, decay_rate=0.001, storage_dir="memory_storage"):
        self.capacity = capacity
        self.decay_rate = decay_rate
        self.memory_bank = deque(maxlen=capacity)
        self.storage_dir = storage_dir

        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def store_memory(self, data, data_type="vector", weight=1.0, metadata=None, id=None):
        # For numpy arrays, optionally save externally
        if isinstance(data, np.ndarray):
            # Save vector as JSON or npy file
            filename = f"vector_{int(time.time()*1000)}_{uuid.uuid4().hex}.npy"
            filepath = os.path.join(self.storage_dir, filename)
            np.save(filepath, data)
            data = filename
            data_type = "vector_file"

        item = MemoryItem(data, data_type, weight=weight, metadata=metadata, id=id)
        self.memory_bank.append(item)
        return item.id

    def get_memories(self, data_type=None, metadata_filter=None, time_window=None):
        now = time.time()
        results = []
        for item in self.memory_bank:
            if data_type and item.data_type != data_type:
                continue
            if metadata_filter and not all(item.metadata.get(k) == v for k, v in metadata_filter.items()):
                continue
            if time_window and (now - item.timestamp) > time_window:
                continue
            results.append(item)
        return results

    def decay_memory(self):
        for item in list(self.memory_bank):
            item.weight *= (1 - self.decay_rate)
            if item.weight < 0.01:
                self.memory_bank.remove(item)

    def save_index(self, filename="memory_index.json"):
        index_list = [item.to_dict() for item in self.memory_bank]
        with open(os.path.join(self.storage_dir, filename), "w") as f:
            json.dump(index_list, f, indent=2)

    def load_index(self, filename="memory_index.json"):
        path = os.path.join(self.storage_dir, filename)
        if os.path.exists(path):
            with open(path, "r") as f:
                index_list = json.load(f)
            self.memory_bank.clear()
            for d in index_list:
                item = MemoryItem.from_dict(d)
                self.memory_bank.append(item)

    def save_text_log(self, text, filename=None):
        filename = filename or f"log_{int(time.time()*1000)}.txt"
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        self.store_memory(data=filename, data_type="text_file", weight=1.0, metadata={"description": "log file"})
        return filepath

    def save_image(self, image_bytes, filename=None):
        filename = filename or f"img_{int(time.time()*1000)}.png"
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        self.store_memory(data=filename, data_type="image_file", weight=1.0)
        return filepath

    def get_recent_memories_summary(self, time_window=300):
        memories = self.get_memories(time_window=time_window)
        summary = {"count": len(memories), "by_type": {}}
        for m in memories:
            summary["by_type"][m.data_type] = summary["by_type"].get(m.data_type, 0) + 1
        return summary
