import os
import time
import json
from collections import deque
import numpy as np
import uuid
import threading
from datetime import datetime

class MemoryItem:
    def __init__(self, data, data_type, timestamp=None, weight=1.0, metadata=None, id=None):
        self.data = data
        self.data_type = data_type
        self.timestamp = timestamp or time.time()
        self.weight = weight
        self.metadata = metadata or {}
        self.id = id or str(uuid.uuid4())

    def to_dict(self):
        serializable_data = self.data
        if isinstance(self.data, np.ndarray):
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
    def __init__(self, capacity=1000, decay_rate=0.001, storage_dir="memory_storage", batch_size=5, batch_time_seconds=60):
        self.capacity = capacity
        self.decay_rate = decay_rate
        self.memory_bank = deque(maxlen=capacity)
        self.storage_dir = storage_dir
        self.batch_size = batch_size
        self.batch_time_seconds = batch_time_seconds
        self._text_log_batch = []
        self._batch_lock = threading.Lock()
        self._last_batch_time = time.time()

        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

        self._batch_flush_thread = threading.Thread(target=self._batch_flush_worker, daemon=True)
        self._batch_flush_thread.start()

    def store_memory(self, data, data_type="generic", weight=1.0, metadata=None):
        """Store a memory item with explicit parameters."""
        metadata = metadata or {}
        timestamp = time.time()
        item = MemoryItem(
            data=data,
            data_type=data_type,
            timestamp=timestamp,
            weight=weight,
            metadata=metadata
        )
        self.memory_bank.append(item)

    def get_memories(self, data_type=None, metadata_filter=None, time_window=None, prioritize=False):
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
        if prioritize:
            results.sort(key=lambda x: (x.metadata.get("important", False), x.weight), reverse=True)
        return results

    def enrich_metadata(self, memory_id, new_metadata):
        for item in self.memory_bank:
            if item.id == memory_id:
                item.metadata.update(new_metadata)
                return True
        return False

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

    def _batch_flush_worker(self):
        while True:
            time.sleep(self.batch_time_seconds / 2)
            with self._batch_lock:
                if self._text_log_batch and (time.time() - self._last_batch_time) >= self.batch_time_seconds:
                    self._flush_text_log_batch()

    def _flush_text_log_batch(self):
        if not self._text_log_batch:
            return
        filename = f"batch_log_{int(time.time()*1000)}.txt"
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n".join(self._text_log_batch) + "\n")
        self.store_memory(data=filename, data_type="text_file", weight=1.0,
                        metadata={"description": "batched log file", "batch": True})
        self._text_log_batch.clear()
        self._last_batch_time = time.time()

    def save_text_log(self, text, filename=None):
        with self._batch_lock:
            self._text_log_batch.append(text)
            if len(self._text_log_batch) >= self.batch_size:
                self._flush_text_log_batch()
        return None

    def mark_memory_important(self, memory_id):
        for item in self.memory_bank:
            if item.id == memory_id:
                item.metadata["important"] = True
                return True
        return False

    def unmark_memory_important(self, memory_id):
        for item in self.memory_bank:
            if item.id == memory_id and "important" in item.metadata:
                del item.metadata["important"]
                return True
        return False

    def decay_memory(self):
        for item in list(self.memory_bank):
            if item.metadata.get("important", False):
                continue
            item.weight *= (1 - self.decay_rate)
            if item.weight < 0.01:
                # Summarization removed here — just remove low weight memory
                self.memory_bank.remove(item)
                self.save_index()
                
    def store_tagged_memory(self, tag, data, data_type="emotion_state", weight=1.0, metadata=None):
        """Stores memory with a custom tag in metadata."""
        if metadata is None:
            metadata = {}
        metadata["tag"] = tag
        self.store_memory(data=data, data_type=data_type, weight=weight, metadata=metadata)
    
    def retrieve_latest_tagged_memory(self, tag):
        """Fetch the most recent memory with a specific tag."""
        
        for item in reversed(self.memory_bank):
            if item.metadata.get("tag") == tag:
                return item
        return None

