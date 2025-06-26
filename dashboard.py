import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from resonant_ai import ResonantAgent
from emotion_agent import EmotionAgent
import threading
import time
import sys
import math


def color_for_solar_level(level):
    # Simplified color scheme for solar activity type
    return {
        "F10.7": "#00ff00",    # Green for valid flux data
        "UNKNOWN": "#cccccc"   # Gray if unknown
    }.get(level.upper(), "#cccccc")


def color_for_kp(kp):
    if kp < 4:
        return "#00ff00"
    elif kp < 6:
        return "#ffff00"
    elif kp < 8:
        return "#ff9900"
    else:
        return "#ff0000"


class AxiomDashboard(tk.Tk):
    def __init__(self, refresh_interval=5):
        super().__init__()
        self.title("Axiom Agent Dashboard")
        self.geometry("700x900")
        self.configure(bg="#1e1e1e")

        self.resonant_agent = ResonantAgent()
        self.emotion_agent = EmotionAgent(memory_agent=self.resonant_agent.memory)
        self.refresh_interval = refresh_interval
        self.running = True

        self._setup_ui()
        self._stop_event = threading.Event()
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_ui(self):
        self.moon_canvas_size = 200
        self.moon_canvas = tk.Canvas(
            self, width=self.moon_canvas_size, height=self.moon_canvas_size,
            bg="#1e1e1e", highlightthickness=0
        )
        self.moon_canvas.pack(pady=10)

        self.factors_frame = tk.Frame(self, bg="#1e1e1e")
        self.factors_frame.pack(pady=5)

        self.factor_labels = {}
        for factor in ["Moon Phase", "Solar Activity", "Solar Level", "Geomagnetic", "Kp Index", "Fatigue"]:
            lbl = tk.Label(self.factors_frame, text=f"{factor}: --", font=("Courier", 12),
                           bg="#1e1e1e", fg="#00ff00")
            lbl.pack(anchor="w")
            self.factor_labels[factor] = lbl

        self.output_box = ScrolledText(self, font=("Courier", 10), bg="#0a0a0a", fg="#00ff00", height=20)
        self.output_box.pack(expand=True, fill='both', padx=10, pady=10)

        self.toggle_button = tk.Button(self, text="Pause", command=self.toggle_running, bg="#222", fg="#fff")
        self.toggle_button.pack(pady=5)

    def toggle_running(self):
        self.running = not self.running
        self.toggle_button.config(text="Resume" if not self.running else "Pause")

    def update_loop(self):
        while not self._stop_event.is_set():
            if self.running:
                self.update_agents()
            time.sleep(self.refresh_interval)

    def draw_moon_phase_clock(self, phase_raw):
        self.moon_canvas.delete("all")
        center = self.moon_canvas_size // 2
        radius = center - 10
        self.moon_canvas.create_oval(center - radius, center - radius, center + radius, center + radius,
                                    outline="#00ff00", width=2)
        angle = (phase_raw * 360) - 90
        angle_rad = math.radians(angle)
        pointer_length = radius - 20
        end_x = center + pointer_length * math.cos(angle_rad)
        end_y = center + pointer_length * math.sin(angle_rad)
        self.moon_canvas.create_line(center, center, end_x, end_y, fill="#00ff00", width=3)
        self.moon_canvas.create_oval(center - 5, center - 5, center + 5, center + 5, fill="#00ff00")
        self.moon_canvas.create_text(center, center - radius + 15, text="New Moon", fill="#00ff00", font=("Arial", 10))
        self.moon_canvas.create_text(center, center + radius - 15, text="Full Moon", fill="#00ff00", font=("Arial", 10))

    def update_agents(self):
        result = self.resonant_agent.run_cycle()
        emotion = self.emotion_agent.update_from_resonance(
            resonance_score=result["score"],
            sacred_moment=result["sacred_moment"]
        )
        cosmic = self.resonant_agent.get_cosmic_factors()
        state_vec = self.resonant_agent.get_state_vector()
        emotion_vec = self.emotion_agent.emotion_vector()

        moon_factor = cosmic["moon"]
        # Reverse scaling from moon_factor (0.1 to 1.0) to raw phase (0 to 1)
        raw_cos = (moon_factor - 0.55) / 0.45
        try:
            raw_phase = math.acos(-raw_cos) / (2 * math.pi)
        except Exception:
            raw_phase = 0.0

        self.factor_labels["Moon Phase"].config(
            text=f"Moon Phase Factor: {moon_factor:.3f} (Raw: {raw_phase:.3f})",
            fg="#00ff00"
        )

        solar_factor = cosmic["solar"]
        solar_level = cosmic.get("solar_level", "UNKNOWN")
        geomagnetic_factor = cosmic["geomagnetic"]
        kp = cosmic.get("kp", 0.0)
        fatigue_factor = cosmic["fatigue"]

        self.draw_moon_phase_clock(raw_phase)

        self.factor_labels["Solar Activity"].config(
            text=f"Solar Activity Factor: {solar_factor:.3f}",
            fg=color_for_solar_level(solar_level)
        )
        self.factor_labels["Solar Level"].config(
            text=f"Solar Data Type: {solar_level}",
            fg=color_for_solar_level(solar_level)
        )
        self.factor_labels["Geomagnetic"].config(
            text=f"Geomagnetic Factor: {geomagnetic_factor:.3f}",
            fg=color_for_kp(kp)
        )
        self.factor_labels["Kp Index"].config(
            text=f"Kp Index: {kp:.1f}",
            fg=color_for_kp(kp)
        )
        self.factor_labels["Fatigue"].config(
            text=f"Fatigue Factor: {fatigue_factor:.3f}",
            fg="#00ff00"
        )

        self.output_box.delete('1.0', tk.END)
        self.output_box.insert(tk.END, "[ResonantAgent Status]\n", 'bold')
        self.output_box.insert(tk.END, f"  Score         : {result['score']:.3f}\n")
        self.output_box.insert(tk.END, f"  Threshold     : {result['threshold']:.3f}\n")
        self.output_box.insert(tk.END, f"  Resonance     : {result['resonance']}\n")
        self.output_box.insert(tk.END, f"  Sacred Moment : {result['sacred_moment']}\n")
        self.output_box.insert(tk.END, "\n  State Vector:\n")
        for i, val in enumerate(state_vec):
            self.output_box.insert(tk.END, f"    [{i}] {val:.3f}\n")

        self.output_box.insert(tk.END, "\n  Cosmic Factors:\n")
        self.output_box.insert(tk.END, f"    Moon Phase Factor : {moon_factor:.3f} (Raw Phase: {raw_phase:.3f})\n")
        self.output_box.insert(tk.END, f"    Solar Activity    : {solar_factor:.3f} ({solar_level})\n")
        self.output_box.insert(tk.END, f"    Geomagnetic Factor: {geomagnetic_factor:.3f} (KP: {kp:.1f})\n")
        self.output_box.insert(tk.END, f"    Fatigue Factor    : {fatigue_factor:.3f}\n")

        self.output_box.insert(tk.END, "\n[EmotionAgent Status]\n", 'bold')
        self.output_box.insert(tk.END, f"  Dominant Emotion: {emotion}\n")
        self.output_box.insert(tk.END, f"  Emotion Vector:\n")
        for e, val in emotion_vec.items():
            self.output_box.insert(tk.END, f"    {e.capitalize():<10}: {val:.3f}\n")

        if self.resonant_agent.debug:
            print(f"[Dashboard] Cosmic Factors: {cosmic}")

    def on_close(self):
        self._stop_event.set()
        self.update_thread.join(timeout=2)
        self.destroy()
        sys.exit()


if __name__ == "__main__":
    app = AxiomDashboard(refresh_interval=5)
    app.mainloop()
