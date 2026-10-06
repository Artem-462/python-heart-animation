# Python Heart Animation 💙

A lightweight creative coding project that renders a dynamic, mathematical heart-shaped animation with particle glow effects, synchronized with background audio.

![Demo](preview.gif)

## ✨ Features
- **Parametric Mathematics:** Particle trajectories calculated dynamically using parametric heart formulas.
- **Pure Tkinter Canvas:** Smooth rendering without heavy third-party graphics engines.
- **Native Windows Audio:** Background audio playback powered directly by Windows Multimedia API (`ctypes` + `winmm.dll`).
- **Standalone Build Ready:** Includes PyInstaller `.spec` configuration for single-binary packaging.

## 🛠 Tech Stack
- **Language:** Python
- **GUI Engine:** Tkinter (Canvas)
- **Audio Interface:** Windows Multimedia API (`winmm.dll` via `ctypes`)
- **Math:** Native `math` & `random`

## 🚀 Quick Start

```bash
git clone https://github.com/Artem-462/python-heart-animation.git
cd python-heart-animation
python heart.py
```
*(Note: Background audio requires Windows for native WinMM API support).*
