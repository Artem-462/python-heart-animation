import math
import random
import ctypes
import os
import sys
import tkinter as tk
from tkinter import font as tkfont

BG = "#000000"
FPS = 60
MUSIC_FILE = "love_you.mp3"

WORDS = ["love you", "Love You", "LOVE YOU"]
CENTER_TEXT = " Love You "
COLORS = [
    (70, 130, 180),
    (30, 144, 255),
    (0, 191, 255),
    (100, 149, 237),
    (65, 105, 225),
]

WIDTH, HEIGHT = 1200, 800
SCALE = 13.0


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__) or "."))
    return os.path.join(base, rel)


def play_music(path):
    try:
        winmm = ctypes.windll.winmm
        winmm.mciSendStringW('close mymusic', None, 0, 0)
        abs_path = os.path.abspath(path)
        if not os.path.isfile(abs_path):
            return False
        err = winmm.mciSendStringW(
            f'open "{abs_path}" type mpegvideo alias mymusic', None, 0, 0
        )
        if err != 0:
            return False
        winmm.mciSendStringW('play mymusic repeat', None, 0, 0)
        return True
    except Exception:
        return False


def stop_music():
    try:
        ctypes.windll.winmm.mciSendStringW('close mymusic', None, 0, 0)
    except Exception:
        pass


def blend(color, alpha):
    a = max(0.0, min(1.0, alpha / 255.0))
    r, g, b = color
    return f'#{int(r * a):02x}{int(g * a):02x}{int(b * a):02x}'


def heart_xy(t):
    x = 16 * (math.sin(t) ** 3)
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return x, -y - 1.8


class Particle:
    __slots__ = ('x', 'y', 'order', 'kind', 'word', 'color',
                 'alpha', 'flicker', 'delay', 'main_id', 'glow_id')

    def __init__(self, x, y, order, kind):
        self.x = x
        self.y = y
        self.order = order
        self.kind = kind
        self.word = random.choice(WORDS)
        self.color = random.choice(COLORS)
        self.alpha = 0.0
        self.flicker = random.uniform(0, math.pi * 2)
        self.delay = 0
        self.main_id = None
        self.glow_id = None


def to_screen(x, y):
    return x * SCALE + WIDTH / 2, y * SCALE + HEIGHT / 2


def build_outline(n_outline, min_gap):
    particles, placed = [], []
    for i in range(n_outline):
        t = (i / n_outline) * 2 * math.pi
        bx, by = heart_xy(t)
        sx, sy = to_screen(bx, by)
        if any(math.hypot(sx - px, sy - py) < min_gap for px, py in placed):
            continue
        placed.append((sx, sy))
        particles.append(Particle(sx, sy, i, "outline"))
    return particles


def build_fill(n_fill, min_gap):
    particles, placed = [], []
    attempts, max_attempts = 0, n_fill * 80
    while len(particles) < n_fill and attempts < max_attempts:
        attempts += 1
        t = random.uniform(0, 2 * math.pi)
        r = random.uniform(0.0, 0.85)
        bx, by = heart_xy(t)
        sx, sy = to_screen(bx * r, by * r)
        if any(math.hypot(sx - qx, sy - qy) < min_gap for qx, qy in placed):
            continue
        placed.append((sx, sy))
        particles.append(Particle(sx, sy, random.randint(0, 300), "fill"))
    return particles


def main():
    global WIDTH, HEIGHT, SCALE

    root = tk.Tk()
    root.title("I love you <3")
    root.configure(bg=BG)
    root.attributes('-fullscreen', True)

    WIDTH = root.winfo_screenwidth()
    HEIGHT = root.winfo_screenheight()

    SCALE = min(WIDTH / 46.0, HEIGHT / 32.0)

    k = SCALE / 13.0

    def fs(base):
        return max(8, int(base * k))

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    font_main_outline = tkfont.Font(family="Arial", size=fs(14), weight="bold")
    font_main_fill = tkfont.Font(family="Arial", size=fs(12), weight="bold")
    font_glow_outline = tkfont.Font(family="Arial", size=fs(20), weight="bold")
    font_glow_fill = tkfont.Font(family="Arial", size=fs(17), weight="bold")
    font_center = tkfont.Font(family="Georgia", size=fs(44), weight="bold")
    font_center_glow = tkfont.Font(family="Georgia", size=fs(58), weight="bold")

    n_outline = max(90, int(150 * k))
    n_fill = max(70, int(110 * k))

    min_gap_outline = max(18, int(28 * k))
    min_gap_fill = max(26, int(40 * k))

    outline = build_outline(n_outline, min_gap_outline)
    fill = build_fill(n_fill, min_gap_fill)

    outline_span = max(p.order for p in outline) if outline else 0
    frames_per_step = 1.6
    fill_start = int(outline_span * frames_per_step) + 30

    for p in fill:
        p.delay = fill_start + p.order
    for p in outline:
        p.delay = int(p.order * frames_per_step)

    particles = outline + fill

    for p in particles:
        main_font = font_main_outline if p.kind == "outline" else font_main_fill
        glow_font = font_glow_outline if p.kind == "outline" else font_glow_fill
        p.glow_id = canvas.create_text(p.x, p.y, text=p.word,
                                       font=glow_font, fill=BG, state='hidden')
        p.main_id = canvas.create_text(p.x, p.y, text=p.word,
                                       font=main_font, fill=BG, state='hidden')

    center_glow_id = canvas.create_text(WIDTH / 2, HEIGHT / 2, text=CENTER_TEXT,
                                        font=font_center_glow, fill=BG, state='hidden')
    center_main_id = canvas.create_text(WIDTH / 2, HEIGHT / 2, text=CENTER_TEXT,
                                        font=font_center, fill=BG, state='hidden')

    center_start = fill_start + 200
    state = {'frame': 0}

    def frame_loop():
        state['frame'] += 1
        f = state['frame']

        for p in particles:
            if f > p.delay and p.alpha < 255:
                p.alpha = min(255.0, p.alpha + 14 + random.randint(0, 4))

            if p.alpha >= 255:
                flick = 0.75 + 0.25 * math.sin(f * 0.04 + p.flicker)
            else:
                flick = 1.0

            a = int(p.alpha * flick)
            if a <= 2:
                continue

            canvas.itemconfigure(p.main_id, state='normal', fill=blend(p.color, a))
            canvas.itemconfigure(p.glow_id, state='normal', fill=blend(p.color, a // 3))

        if f > center_start:
            progress = min(1.0, (f - center_start) / 60)
            center_alpha = int(255 * (1 - math.exp(-progress * 8)))
            pulse = max(0.7, 0.9 + 0.1 * math.sin(f * 0.05))
            ca = int(center_alpha * pulse)
            if ca > 3:
                canvas.itemconfigure(center_main_id, state='normal',
                                     fill=blend((255, 250, 245), ca))
                canvas.itemconfigure(center_glow_id, state='normal',
                                     fill=blend((160, 190, 255), ca // 4))

        root.after(int(1000 / FPS), frame_loop)

    def on_close(_e=None):
        stop_music()
        root.destroy()

    root.bind("<Escape>", on_close)
    root.bind("<F11>", lambda e: root.attributes(
        '-fullscreen', not root.attributes('-fullscreen')))
    root.protocol("WM_DELETE_WINDOW", on_close)

    play_music(resource_path(MUSIC_FILE))

    frame_loop()
    root.mainloop()
    stop_music()


if __name__ == "__main__":
    main()