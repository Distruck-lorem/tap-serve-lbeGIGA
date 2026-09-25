# 🍪 Tap & Serve

A 2D Bakery Management & Cookie Crafting Game built with **Python & Pygame**.

---

## 🎮 Gameplay Features

* **Baking QTE (Quick Time Event)**:
  * Multi-tier timing bar (PERFECT, GOOD, BAD, MISS).
  * High precision scoring system.
* **Rapid Whisking Mini-Game**:
  * 10-second rapid clicking mini-game to whisk dough.
* **Game Modes**:
  * ⏱️ **Casual Mode**: 1-minute countdown challenge mode.
  * ♾️ **Unlimited Mode**: Endless mode with session finish/close button.
* **Animations & Polish**:
  * Smooth customer entrance (Ease-Out Cubic) and automatic 1.5s exit animation.
  * Warm pastel gradient background & custom UI cards.
* **Audio & Music**:
  * Dynamic Jazz BGM selection (Lobby: Jazz 1-3, Gameplay: Jazz 4-10).
  * Immersive SFX for butter drop, egg crack, whisking, and microwave baking.

---

## 🛠️ Project Structure

```text
LBE-project-tap&serve-lite/
│── asset/                   # Game graphics and audio assets
│   ├── audio/
│   │   ├── music/           # Jazz BGM tracks (1-10)
│   │   └── sfx/             # Sound effects
│   └── ...
│── config.py                # Global configurations and parameters
│── game.py                  # Main Game Loop, Controllers & State Manager
│── main.py                  # Entry Point
└── models/                  # OOP Game Objects
    ├── customer.py          # Customer class (Entrance/Exit animations & speech bubbles)
    ├── kitchen.py           # Kitchen recipe manager & ingredient hitboxes
    ├── oven.py              # Oven baking frame animation timer
    ├── qte.py               # Baking QTE timing bar
    └── whisk.py             # Whisking mini-game
```

---

## 🚀 How to Run

### Prerequisites
* Python 3.8+
* Pygame 2.5+

### Installation

1. **Clone Repository**:
   ```bash
   git clone https://github.com/your-username/LBE-project-tap-and-serve.git
   cd LBE-project-tap-and-serve
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Game**:
   ```bash
   python main.py
   ```

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
