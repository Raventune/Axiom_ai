import random
import json
from datetime import datetime

class EmotionState:
    def __init__(self):
        self.center = []  # List of dominant emotions
        self.background = {}  # {emotion: intensity (0–1)}
        self.updated_at = datetime.utcnow().isoformat()
        self.valence = 0.0  # Pleasantness
        self.arousal = 0.0  # Energy level
        self.metadata = {}

    def to_dict(self):
        return {
            "center": self.center,
            "background": self.background,
            "valence": self.valence,
            "arousal": self.arousal,
            "metadata": self.metadata,
            "updated_at": self.updated_at,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def update_from_inputs(self, inputs):
        # Placeholder logic: real version would use appraisals
        perceived_threat = inputs.get("threat_level", 0)
        perceived_success = inputs.get("reward_level", 0)
        frustration = inputs.get("low_patience", 0)

        self.background["fear"] = min(1.0, perceived_threat * 0.8)
        self.background["anger"] = min(1.0, frustration * 0.7)
        self.background["joy"] = min(1.0, perceived_success * 0.6)

        # Decide dominant emotions
        candidates = sorted(self.background.items(), key=lambda x: x[1], reverse=True)
        self.center = [e for e, v in candidates if v > 0.3][:3]

        # Simple affect model
        self.valence = (self.background.get("joy", 0) - self.background.get("fear", 0) - self.background.get("anger", 0))
        self.arousal = max(self.background.values(), default=0)

        self.updated_at = datetime.utcnow().isoformat()

    def tag_memory(self):
        return {
            "emotion_center": self.center,
            "emotion_background": self.background,
            "valence": self.valence,
            "arousal": self.arousal,
            "timestamp": self.updated_at,
        }

class EmotionPacket:
    def __init__(self, state):
        self.emotion = state.to_dict()
        self.urgency = self._calculate_urgency(state)
        self.stability = self._calculate_stability(state)

    def _calculate_urgency(self, state):
        return min(1.0, state.arousal + 0.3 if "anger" in state.center else 0.2)

    def _calculate_stability(self, state):
        instability = state.background.get("fear", 0) + state.background.get("anger", 0)
        return round(1.0 - min(1.0, instability), 2)

    def to_dict(self):
        return {
            "emotion": self.emotion,
            "urgency": self.urgency,
            "stability": self.stability,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

class EmotionAgent:
    def __init__(self, dispatcher):
        self.state = EmotionState()
        self.dispatcher = dispatcher  # Reference to the dispatcher object

    def process_cycle(self, external_inputs=None):
        # 1. Request context info from dispatcher
        context = self.dispatcher.get_context()  # e.g., returns dict with patience, threshold

        # 2. Merge external inputs with context
        input_data = external_inputs or {}
        input_data.update(context)

        # 3. Update emotion state based on combined inputs
        self.state.update_from_inputs(input_data)

        # 4. Prepare packet and send back to dispatcher
        packet = EmotionPacket(self.state)
        self.dispatcher.receive_emotion_packet(packet.to_dict())

    def get_emotion_state(self):
        return self.state.to_dict()

    def export_for_memory(self):
        return self.state.tag_memory()

    def export_for_dispatcher(self):
        packet = EmotionPacket(self.state)
        return packet.to_dict()

# Example Dispatcher stub for testing

class Dispatcher:
    def __init__(self):
        self.current_patience = 0.5
        self.current_threshold = 0.3

    def get_context(self):
        return {
            "low_patience": self.current_patience,
            "threshold": self.current_threshold,
        }

    def receive_emotion_packet(self, packet):
        print("Dispatcher received emotion packet:")
        print(json.dumps(packet, indent=2))


# Example usage

if __name__ == "__main__":
    dispatcher = Dispatcher()
    agent = EmotionAgent(dispatcher)
    agent.process_cycle({"threat_level": 0.7, "reward_level": 0.1})
