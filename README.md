# Smart Rock-Paper-Scissors (SmartRPS)

> An intelligent, computer-vision-powered rock-paper-scissors game that combines hand gesture recognition with strategic AI gameplay.

## Overview

**SmartRPS** is an interactive rock-paper-scissors game that uses hand gesture recognition (via MediaPipe) and machine learning-based AI to provide an engaging, fair gaming experience. The project aims to promote computer science education through interactive play, featuring a strategic bot that learns from player behavior and fairness mechanisms to ensure game integrity.

- Video Demo: [YouTube Link](https://youtu.be/O-qPXGXM6Y8)
- Promotional Video: [YouTube Link](https://youtu.be/1EbIFyo-VeQ)

**Key Features:**
- **Real-time Hand Gesture Recognition** – Uses MediaPipe for accurate hand tracking and gesture detection
- **Strategic AI Bot** – Powered by dataset-derived statistics from 69,365+ professional RPS rounds
- **Fairness System** – Commitment scheme to verify that the bot's move is made before seeing the player's gesture
- **Interactive UI** – Built with Pygame, featuring multiple game screens and themes
- **Gesture Confirmation** – Prevent false inputs with a confirmation gesture system

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Game Mechanics](#game-mechanics)
- [Technical Architecture](#technical-architecture)
- [Dependencies](#dependencies)
- [System Requirements](#system-requirements)

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Webcam/camera device
- 500MB+ disk space for dependencies

### Installation

1. **Clone the repository:**
   ```bash
   cd /Users/gergiosavdeliotis/Downloads/Temp/SE-Project-Group-F
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   cd src/smart-rps
   pip install -r requirements.txt
   ```

### Running the Game

```bash
python ui/ui.py
```

The game window will open showing the main menu. Select your opponent difficulty and start playing!

## Usage

### Game Flow

1. **Menu Screen** – Select game mode and difficulty level
2. **Bot Selection** – Choose opponent difficulty (Easy, Medium, Hard)
3. **Playing Screen** – Show your hand gesture in the marked ROI (Region of Interest)
4. **Results** – View round outcome and running score
5. **Game Over** – Summary statistics and option to play again

### Hand Gestures

Within the **300×300 pixel Region of Interest (ROI)** on the screen:

- **Rock** – Closed fist
- **Paper** – Open hand, all fingers extended
- **Scissors** – Two fingers extended (index and middle)
- **Confirmation** – Specific gesture to lock in your choice

**Important:** Gestures must be held within the marked ROI to register.

### Difficulty Levels

- **Easy** – Bot uses random or simple strategies
- **Medium** – Bot uses Markov chain predictions (default)
- **Hard** – Bot uses advanced statistical analysis with Win-Stay/Lose-Shift patterns

## Project Structure

```
src/smart-rps/
├── bot/                    # AI opponent logic
│   ├── bot.py             # Strategic bot implementation
│   ├── game_bot.py        # Bot integration with game engine
│   └── __init__.py
├── camera/                 # Hand gesture recognition
│   ├── camera.py          # Camera feed capture
│   ├── hand_gestures.py   # Hand landmark detection and gesture classification
│   ├── integration.py     # Camera-to-game integration
│   └── __init__.py
├── game/                   # Core game logic
│   ├── engine.py          # Main game state machine and loop
│   ├── constants.py       # Game constants (window size, FPS, moves)
│   ├── gesture_lock.py    # Gesture confirmation/validation
│   └── __init__.py
├── ui/                     # User interface
│   ├── ui.py              # Application entry point
│   ├── screens.py         # Game screens (menu, playing, game-over)
│   ├── widgets.py         # Reusable UI components
│   ├── theme.py           # Color themes and styling
│   ├── fairness.py        # Fairness/commitment verification
│   ├── assets.py          # Asset management
│   └── __init__.py
├── data/                   # Pre-trained models
│   └── hand_landmarker.task  # MediaPipe hand detection model
├── assets/                 # Game assets (images, sounds, etc.)
├── pyproject.toml         # Project metadata and configuration
└── requirements.txt       # Python dependencies
```

## Game Mechanics

### AI Strategy

The bot uses a **Markov chain prediction model** based on the Brockbank & Vul (2021) dataset:

- **69,365 professional RPS rounds** from online human-vs-bot games
- **3,059 opening moves** from Uppsala tournament (human-vs-human)
- **Move frequency priors**: Rock (30.9%), Paper (33.2%), Scissors (35.9%)
- **Win-Stay/Lose-Shift patterns**: Captures human behavioral biases

**Prediction Logic:**
1. On the first move, the bot uses the opening move prior (counters Scissors at 35.9%)
2. For subsequent moves, it predicts the player's next move using a Markov transition matrix
3. The bot then plays the counter-move to maximize winning chances

**No runtime training** – all statistics are pre-computed offline for real-time responsiveness.

### Fairness System

The game implements a **commitment scheme** to prove fairness:

1. **Bot commits** to its move and generates a hash before the player shows their gesture
2. **Player makes** their move
3. **Verification** – The hash is checked against the bot's revealed move to prove no cheating occurred

### Gesture Confirmation

To prevent accidental inputs:
- Players must **hold a confirmation gesture** to lock in their choice
- Any unintended hand movements won't trigger false plays
- Visual feedback confirms when a gesture is locked

## Technical Architecture

### Core Components

| Module | Purpose | Key Classes |
|--------|---------|------------|
| **Camera** | Hand detection & gesture recognition | `CameraFeed`, `HandGestureRecognizer` |
| **Bot** | AI decision-making | `StrategicBot`, `pick_bot_move()` |
| **Game** | State machine & game flow | `SmartRPSGame` |
| **UI** | Rendering & user interaction | Pygame screens, widgets, theme system |

### Dependencies

```
pygame              # Game window and graphics
opencv-python      # Computer vision utilities
mediapipe==0.10.21 # Hand pose estimation
```

### Hand Recognition Pipeline

1. **Capture** – Webcam frame capture (640×480)
2. **Detection** – MediaPipe detects hand landmarks (21 keypoints per hand)
3. **Classification** – Hand posture classified into Rock/Paper/Scissors
4. **ROI Validation** – Gesture must be within the 300×300 pixel ROI
5. **Confirmation** – Player must hold confirmation gesture to lock the move

## System Requirements

- **OS:** macOS, Linux, or Windows
- **Python:** 3.11+
- **Webcam:** Required for hand gesture recognition
- **RAM:** 2GB minimum (4GB recommended)
- **Disk Space:** 500MB for dependencies
- **CPU:** Dual-core or better (real-time hand detection requires processing power)

## Installation Troubleshooting

### MediaPipe Model Not Found
The `hand_landmarker.task` model should be in `data/`. If missing:
```bash
# The model will be automatically loaded from the MediaPipe Python package
```

### Webcam Not Detected
- Ensure your webcam is connected and recognized by the OS
- Check camera permissions in system settings
- On macOS, grant Pygame camera access in Privacy settings

### Low FPS / Stuttering
- Reduce window resolution in `game/constants.py`
- Close other CPU-intensive applications
- Check lighting in your play area (hand detection improves in bright environments)

## Development Notes

### Configuration
Key game parameters are in `game/constants.py`:
- `WINDOW_W`, `WINDOW_H` – Display resolution
- `FPS` – Target frame rate
- `MOVES` – Valid game moves
- `BEATS` – Win conditions

### Extending the Bot
To add new bot strategies, extend `bot/bot.py`:
```python
class CustomBot(StrategicBot):
    def predict(self) -> str:
        # Your custom prediction logic
        pass
```

### Adding New Gestures
Hand gesture mapping is in `camera/hand_gestures.py`. Add new gesture classifiers here.

## Dataset Attribution

- **Brockbank & Vul (2021)** – "Seeing what you want to see: Confirmation bias in human-AI game playing" – Contains 69,365 rounds of professional RPS gameplay
- **Uppsala Tournament Data** – 3,059 human-vs-human rounds for opening move priors

## Asset Attribution

- **Minecraft Assets** – Textures and visual elements sourced from Minecraft for UI theming and game aesthetics

---

**Version:** 1.0.0  
**Team:** Group F  
**Members:**
- Avdeliotis Georgios
- Pelagia Massarou
- Gabriel Marique
- Irina Pavel

**Python:** 3.11+