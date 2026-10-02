"""Главное окно приложения и цикл анимации."""

import math
import tkinter as tk

from src.models.animation_model import PolarRose
from src.renderers.renderer import Renderer

CANVAS_SIZE = 600
BG_COLOR = "#0f1117"
#: Интервал между кадрами в миллисекундах (~60 кадров в секунду).
FRAME_MS = 16
DEFAULT_SPEED = 8


class App:
    """Окно с холстом, в котором кривая рисуется постепенно."""

    def __init__(self):
        """Создать окно, холст, рендерер и запустить анимацию."""
        self.root = tk.Tk()
        self.root.title("Полярная роза — Тасоев Арсен")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=CANVAS_SIZE,
                                height=CANVAS_SIZE, bg=BG_COLOR,
                                highlightthickness=0)
        self.canvas.pack()
        self.renderer = Renderer(self.canvas, CANVAS_SIZE)

        self.curve = PolarRose()
        self.speed = DEFAULT_SPEED
        self.running = True
        self.restart()
        self._tick()

    def restart(self):
        """Начать рисование текущей кривой с начала."""
        self.renderer.clear()
        self.index = 0
        self.total = self.curve.sample_count()
        self.done = False
        self._update_cursor()

    def _tick(self):
        """Один кадр анимации: дорисовать очередной участок кривой."""
        if self.running:
            if self.done:
                # Кривая готова — курсор продолжает бежать по ней.
                self.index = (self.index + self.speed) % self.total
            else:
                end = min(self.index + self.speed, self.total)
                points = [self.curve.sample(i)
                          for i in range(self.index, end + 1)]
                self.renderer.draw_path(points, self.index / self.total)
                self.index = end
                self.done = end >= self.total
            self._update_cursor()
        self.root.after(FRAME_MS, self._tick)

    def _update_cursor(self):
        """Перерисовать курсор и строку с информацией."""
        self.renderer.draw_cursor(self.curve.sample(self.index),
                                  self.curve.is_polar)
        self.renderer.draw_info(self._info_text())

    def _info_text(self):
        """Собрать подпись: формула, период и текущее значение t."""
        t = self.index * self.curve.t_step
        return (f"{self.curve.name}\n{self.curve.formula()}\n"
                f"θ = {t / math.pi:5.2f}π  из "
                f"{self.curve.period() / math.pi:.0f}π")

    def run(self):
        """Запустить главный цикл tkinter."""
        self.root.mainloop()
