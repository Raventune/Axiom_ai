
Changelog
[Unreleased] - 2025-06-15
Added

    Integrated EmotionAgent with the core system to maintain a quantum-inspired emotional state influenced by resonance scores and sacred moments.

    Added ResonantAgent integration inside AxiomDispatcher to generate resonance scores influencing the emotional state.

    Extended ChatAgent.chat() method to accept an optional context parameter, allowing the injection of emotion context directly into the prompt.

    Updated build_prompt() in ChatAgent to append emotional context to the prompt dynamically.

    Implemented emotional state persistence and decay logic within EmotionAgent to provide consistent emotional tagging over time.

    Stored emotion metadata alongside dialogue in MemoryAgent to enable long-term emotional context tracking.

Changed

    Modified AxiomDispatcher.chat() to:

        Run a resonance cycle via ResonantAgent.

        Update emotional state using the resonance score.

        Pass the current emotional context as part of the prompt when generating AI chat responses.

        Log emotion state and resonance metadata in memory for contextual awareness and future recall.

Files Updated

    dispatcher_axiom_ai.py — Added resonance and emotion integration into main dispatcher logic.

    emotion_agent.py — Added quantum-like emotional state logic, resonance-based collapse, decay, and memory tagging.

    chat_agent.py — Extended chat() and build_prompt() to accept and use emotional context.

### Added

- Inner monologue support triggered by user input prefixed with `!`, allowing the AI to perform self-reflection cycles.
- Personality snippet fetching to include recent memory fragments as long-term context in conversations.
- Improved emotion state handling to ensure AI’s own emotional state is reflected and used during chat responses.

### Fixed

- Corrected emotion context usage to prevent confusion between user emotions and AI’s emotional state.
- Resolved duplicate logic in `process_input` and `query` methods to streamline input processing and response generation.

# Changelog

### [Unreleased] - 2025-06-26

### Added
- 🛰️ Integrated NOAA **Solar Radio Flux** API (`solar-radio-flux.json`) for more accurate solar activity measurements.
- 🌕 Normalized moon phase, solar flux, and geomagnetic KP index into dynamic factors between **0.1 and 1.0**.
- 🧠 Introduced **AxiomDashboard**:
  - Real-time visual monitoring of the **ResonantAgent** and **EmotionAgent**.
  - Displays moon phase clock, cosmic factor breakdown, KP index color coding, emotional state vector, and resonance scoring.
- 🌳 Added **logic tree system** to `MemoryAgent` to begin parsing symbolic memory outcomes and influencing future decisions.

### Changed
- 🛠️ Refactored `get_solar_activity_factor()` in `ResonantAgent` to use new flux data structure.
- 🧹 Cleaned up `get_cosmic_factors()` and ensured proper clamping on all dynamic factor inputs.
- 🎨 Updated color mappings and debug prints in the dashboard to align with scientific scales and expected UX.

### Fixed
- 🧪 Improved error handling for external API timeouts and unexpected response shapes (e.g. missing flux fields).
- 🧮 Corrected moon phase raw-to-factor math for better alignment with lunar cycle midpoint scaling.
