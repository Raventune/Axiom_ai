import random
import json
import time
from datetime import datetime
import numpy as np
from memory_agent import MemoryAgent

class EmotionState:
    def __init__(self, initial_emotions=None):
        # Allow custom set of emotions or use default
        if initial_emotions is None:
            initial_emotions = {
                "joy": 0.25,
                "sadness": 0.25,
                "anger": 0.25,
                "calm": 0.25
            }
        self.center = initial_emotions
        self.last_state = None

    def collapse_state(self, resonance_score, sacred_moment=False):
        emotions = list(self.center.keys())
        probabilities = np.array([self.center[e] for e in emotions])

        if sacred_moment:
            for e in ["joy", "calm"]:
                if e in self.center:
                    probabilities[emotions.index(e)] += 0.1

        probabilities /= probabilities.sum()

        adjusted = {}
        for e in emotions:
            base = probabilities[emotions.index(e)]
            if e in ["joy", "calm"]:
                adjusted[e] = base + 0.2 * resonance_score
            else:
                adjusted[e] = base * (1 - resonance_score)

        total = sum(adjusted.values())
        for e in adjusted:
            adjusted[e] /= total

        self.center = adjusted
        self.last_state = max(adjusted, key=adjusted.get)
        return self.center


    def decay_and_stabilize(self, factor=0.95):
        """Decay emotion weights to introduce memory persistence."""
        for key in self.center:
            self.center[key] *= factor
        if self.last_state:
            self.center[self.last_state] += 0.1
        total = sum(self.center.values())
        for key in self.center:
            self.center[key] /= total


class EmotionAgent:
    def __init__(self, memory_agent=None):
        self.state = EmotionState()
        self.memory_agent = memory_agent or MemoryAgent()

    def update_from_resonance(self, resonance_score, sacred_moment=False):
        emotion_vector = self.state.collapse_state(resonance_score, sacred_moment)
        self.state.decay_and_stabilize()

        metadata = {
            "emotion_vector": emotion_vector,
            "dominant_emotion": self.state.last_state,
            "resonance_score": resonance_score,
            "sacred": sacred_moment
        }
        self.memory_agent.store_tagged_memory(
            tag="emotion",
            data=emotion_vector,
            data_type="emotion_vector",
            metadata=metadata
        )

        return self.state.last_state


        # Log into memory
        metadata = {
            "emotion": emotion,
            "resonance_score": resonance_score,
            "sacred": sacred_moment
        }
        self.memory_agent.store_tagged_memory(
            tag="emotion",
            data=emotion,
            data_type="emotion_state",
            metadata=metadata
        )

        return emotion

    def current_emotion(self):
        return self.state.last_state or "neutral"

    def emotion_vector(self):
        return self.state.center.copy()
