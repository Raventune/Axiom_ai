# perception_interface.py

from datetime import datetime

class PerceptionInterface:
    def __init__(self):
        self.events = []

    def perceive(self, input_text, source="user", tags=None):
        """Receive input, tag it, and store as a structured event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "content": input_text,
            "tags": tags or []
        }
        self.events.append(event)
        return event  # Optionally return for dispatcher use

    def get_recent_events(self, limit=5):
        return self.events[-limit:]

    def clear_events(self):
        self.events = []
