import numpy as np
import time
import math
import requests
from memory_agent import MemoryAgent

class ResonantAgent:
    """
    ResonantAgent evaluates the vibrational alignment of symbolic actions or states
    with internal and external factors like celestial events, emotional states, and
    memory performance. It dynamically adjusts its resonance threshold and internal
    state vector to evolve symbolic awareness over time.
    """

    def __init__(self, threshold=0.95, decay=0.005):
        self.threshold = threshold
        self.memory = MemoryAgent(capacity=100, decay_rate=decay)
        self.state_vector = self._init_state()
        self.threshold_min = 0.7
        self.threshold_max = 0.99
        self.threshold_step = 0.01
        self.debug = True

    def _init_state(self):
        vec = np.random.rand(5)
        return vec / np.linalg.norm(vec)

    def reset_state(self):
        self.state_vector = self._init_state()

    def generate_chaos_vector(self):
        vec = np.random.normal(0, 1, size=5)
        return vec / np.linalg.norm(vec)

    def resonance_score(self, vector, weight=1.0):
        return weight * np.dot(self.state_vector, vector)

    def get_moon_phase_factor(self):
        try:
            r = requests.get("https://api.open-meteo.com/v1/astronomy",
                             params={"latitude": 0.0, "longitude": 0.0, "hourly": "moon_phase"}, timeout=5)
            if r.ok:
                phase = r.json()["hourly"]["moon_phase"][0]
                return 1.0 + 0.5 * math.sin(2 * math.pi * phase)
        except:
            pass
        return 1.0

    def get_solar_activity_factor(self):
        try:
            r = requests.get("https://services.swpc.noaa.gov/products/alerts.json", timeout=5)
            if r.ok and isinstance(r.json(), list):
                level = r.json()[-1].get("message_type", "GREEN")
                return {"GREEN": 1.0, "YELLOW": 0.9, "ORANGE": 0.8, "RED": 0.7}.get(level, 1.0)
        except:
            pass
        return 1.0

    def get_geomagnetic_factor(self):
        try:
            r = requests.get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json", timeout=5)
            if r.ok and isinstance(r.json(), list):
                data = r.json()[-1]
                kp = float(data[1])
                return 1.0 + (kp / 15.0)
        except:
            pass
        return 1.0

    def weighted_success_failure_ratio(self, window_seconds=300):
        return 0.0  # Neutral ratio (no success or failure bias)

    def get_fatigue_factor(self):
        # Placeholder for future sensor-based fatigue integration
        return 1.0

    def get_emotion_factor(self):
        # Placeholder for EmotionAgent input
        return 1.0

    def reevaluate_decision(self):
        adjustments = [self.resonance_score(self.generate_chaos_vector()) for _ in range(3)]
        return sum(adjustments) / 3

    # def adjust_threshold_based_on_memory(self):
    #    ratio = self.memory.weighted_success_failure_ratio(window_seconds=300)
    #    if ratio > 0.1:
    #        new_threshold = min(self.threshold_max, self.threshold + self.threshold_step)
    #    elif ratio < -0.1:
    #        new_threshold = max(self.threshold_min, self.threshold - self.threshold_step)
    #    else:
    #       new_threshold = self.threshold
    #   self.set_threshold(new_threshold)

    def run_cycle(self):
        moon_f = self.get_moon_phase_factor()
        solar_f = self.get_solar_activity_factor()
        geomag_f = self.get_geomagnetic_factor()
        fatigue_f = self.get_fatigue_factor()
        emotion_f = self.get_emotion_factor()
        brainwave_f = self.get_simulated_brainwave_factor()
        
        cosmic_patience = moon_f * solar_f * geomag_f * fatigue_f * emotion_f

        chaos_vector = self.generate_chaos_vector()
        score = self.resonance_score(chaos_vector)

        result = {
            "score": score,
            "patience": cosmic_patience,
            "resonance": False,
            "threshold": self.threshold,
            "sacred_moment": False
        }

        if score > self.threshold:
            self.state_vector = (self.state_vector + chaos_vector) / 2
            self.state_vector /= np.linalg.norm(self.state_vector)
            self.memory.store_memory(self.state_vector)
            result["resonance"] = True

            if score > 0.99 and cosmic_patience > 1.3:
                result["sacred_moment"] = True

        else:
            # avg_memory = self.memory.average_memory()
            self.state_vector += (0.01 / cosmic_patience) * self.generate_chaos_vector()
            self.state_vector /= np.linalg.norm(self.state_vector)

        # self.adjust_threshold_based_on_memory()

        if self.debug:
            print(f"[CycleLog] Score: {score:.3f} | Threshold: {self.threshold:.3f} | Patience: {cosmic_patience:.3f} | Resonant: {result['resonance']} | Sacred: {result['sacred_moment']}")

        return result

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, new_threshold: float):
        self.threshold = max(self.threshold_min, min(self.threshold_max, new_threshold))

    def get_state_vector(self):
        return self.state_vector.tolist()

    def get_average_resonance_memory(self):
        return self.memory.average_memory()
    
    def get_simulated_brainwave_factor(self):
        # Simulate a brainwave signal oscillating between 0.8 and 1.2
        t = time.time()
        value = 1.0 + 0.2 * math.sin(t)
        return value
