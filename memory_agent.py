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
