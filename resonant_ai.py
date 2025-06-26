import numpy as np
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
        vec = np.random.rand(4)
        return vec / np.linalg.norm(vec)

    def reset_state(self):
        self.state_vector = self._init_state()

    def resonance_score(self, vector, weight=1.0):
        return weight * np.dot(self.state_vector, vector)

    def get_moon_phase_factor(self):
        try:
            r = requests.get("https://api.open-meteo.com/v1/forecast", params={
                "latitude": 0.0,
                "longitude": 0.0,
                "daily": "moon_phase",
                "timezone": "UTC"
            }, timeout=5)

            if r.ok:
                phase_list = r.json().get("daily", {}).get("moon_phase", [])
                if phase_list:
                    phase = phase_list[0]  # raw 0 to 1
                    scaled_phase = 0.1 + 0.9 * phase  # scale 0-1 to 0.1-1.0
                    if self.debug:
                        print(f"[MoonPhase] Raw: {phase:.3f}, Scaled: {scaled_phase:.3f}")
                    return scaled_phase
        except Exception as e:
            print(f"[MoonPhase] Error: {e}")
        return 0.55  # fallback neutral value around mid range

    def get_solar_activity_factor(self):
        try:
            r = requests.get("https://services.swpc.noaa.gov/json/solar-radio-flux.json", timeout=5)
            if r.ok and isinstance(r.json(), list) and len(r.json()) > 0:
                data = r.json()

                target_freq = 2800  # MHz (approximate F10.7 frequency)
                flux_values = []

                for station in data:
                    details = station.get("details", [])
                    # Find flux at closest frequency to target_freq
                    closest_detail = None
                    min_diff = float('inf')
                    for detail in details:
                        freq = detail.get("frequency", 0)
                        diff = abs(freq - target_freq)
                        if diff < min_diff:
                            min_diff = diff
                            closest_detail = detail
                    if closest_detail and "flux" in closest_detail:
                        flux_values.append(float(closest_detail["flux"]))

                if flux_values:
                    avg_flux = sum(flux_values) / len(flux_values)
                    min_flux = 65.0
                    max_flux = 300.0
                    scaled_factor = (avg_flux - min_flux) / (max_flux - min_flux)
                    scaled_factor = max(0.1, min(scaled_factor, 1.0))

                    if self.debug:
                        print(f"[SolarRadioFlux] Avg Flux: {avg_flux:.1f}, Scaled Factor: {scaled_factor:.3f}")

                    return scaled_factor, "F10.7"

        except Exception as e:
            print(f"[SolarRadioFlux] Error: {e}")

        return 1.0, "UNKNOWN"


    def get_geomagnetic_factor(self):
        try:
            r = requests.get("https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json", timeout=5)
            if r.ok and isinstance(r.json(), list):
                data = r.json()[-1]
                kp = float(data[1])
                kp_normalized = min(kp, 9.0) / 9.0
                factor = 1.0 - 0.9 * kp_normalized
                factor = max(factor, 0.1)
                return factor, kp
        except:
            pass
        return 1.0, 0.0

    def weighted_success_failure_ratio(self, window_seconds=300):
        return 0.0  # Neutral ratio (no success or failure bias)

    def get_fatigue_factor(self):
        # Placeholder for future sensor-based fatigue integration
        return 1.0

    def reevaluate_decision(self):
        adjustments = [self.resonance_score(self.generate_chaos_vector()) for _ in range(3)]
        return sum(adjustments) / 3

    def run_cycle(self):
        factors = self.get_cosmic_factors()

        # Only multiply numeric factors for patience calculation
        numeric_factors = [factors["moon"], factors["solar"], factors["geomagnetic"], factors["fatigue"]]
        cosmic_patience = np.prod(numeric_factors)

        cosmic_vector = self.generate_cosmic_vectors()
        score = self.resonance_score(cosmic_vector)

        result = {
            "score": score,
            "patience": cosmic_patience,
            "resonance": False,
            "threshold": self.threshold,
            "sacred_moment": False
        }

        if score > self.threshold:
            self.state_vector = (self.state_vector + cosmic_vector) / 2
            self.state_vector /= np.linalg.norm(self.state_vector)
            self.memory.store_memory(self.state_vector)
            result["resonance"] = True
            if score > 0.99 and cosmic_patience > 1.3:
                result["sacred_moment"] = True
        else:
            safe_patience = cosmic_patience if cosmic_patience > 0 else 0.01
            self.state_vector += (0.01 / safe_patience) * cosmic_vector
            self.state_vector /= np.linalg.norm(self.state_vector)

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

    def get_cosmic_factors(self):
        moon = self.get_moon_phase_factor()

        # Get detailed solar activity from solar radio flux data
        solar_factor, solar_level = self.get_solar_activity_factor()

        geo_factor, kp = self.get_geomagnetic_factor()
        fatigue = self.get_fatigue_factor()

        # Clamp moon factor to [0.1, 1.0]
        moon = max(min(moon, 1.0), 0.1)

        # Clamp solar factor to [0.1, 1.0]
        solar_factor = max(min(solar_factor, 1.0), 0.1)

        # Normalize geomagnetic factor to [0.1, 1.0]
        geo_factor = max(min(geo_factor, 1.0), 0.1)

        # Clamp fatigue to [0.1, 1.0]
        fatigue = max(min(fatigue, 1.0), 0.1)

        return {
            "moon": moon,
            "solar": solar_factor,
            "solar_level": solar_level,
            "geomagnetic": geo_factor,
            "kp": kp,
            "fatigue": fatigue
        }

    def generate_cosmic_vectors(self):
        factors = self.get_cosmic_factors()
        vec = np.array([
            factors["moon"],
            factors["solar"],
            factors["geomagnetic"],
            factors["fatigue"]
        ])
        return vec / np.linalg.norm(vec)
