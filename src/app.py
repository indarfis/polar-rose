"""Главное окно приложения и цикл анимации."""

import math
import tkinter as tk

from src.models.animation_model import CURVES, curve_by_name
from src.renderers.renderer import Renderer
from src.widgets.controls import ControlPanel

CANVAS_SIZE = 600
BG_COLOR = "#0f1117"
#: Интервал между кадрами в миллисекундах (~60 кадров в секунду).
FRAME_MS = 16
DEFAULT_SPEED = 8
MAX_SPEED = 60


class App:
    """Окно с холстом и панелью управления.

    App связывает модель (кривую), рендерер и панель управления:
    хранит состояние анимации и обрабатывает действия пользователя.
    """

    def __init__(self):
        """Создать окно, холст, панель управления и запустить анимацию."""
        self.root = tk.Tk()
        self.root.title("Полярная роза — Тасоев Арсен")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=CANVAS_SIZE,
                                height=CANVAS_SIZE, bg=BG_COLOR,
                                highlightthickness=0)
        self.canvas.pack(side="left")
        self.renderer = Renderer(self.canvas, CANVAS_SIZE)

        self.curve = CURVES[0]()
        self.speed = DEFAULT_SPEED
        self.running = True
        self.show_radius = True

        self.panel = ControlPanel(
            self.root, [cls.name for cls in CURVES], self.speed,
            on_curve=self.select_curve, on_params=self.set_params,
            on_speed=self.set_speed, on_pause=self.toggle_pause,
            on_reset=self.restart, on_instant=self.draw_instantly,
            on_radius=self.set_show_radius)
        self.panel.pack(side="right", fill="y")
        self.panel.set_curve(self.curve)
        self._bind_keys()

        self.restart()
        self._tick()

    # ----- Состояние анимации -------------------------------------------

    def restart(self):
        """Начать рисование текущей кривой с начала."""
        self.renderer.clear()
        self.index = 0
        self.total = self.curve.sample_count()
        self.done = False
        self._update_cursor()

    def draw_instantly(self):
        """Нарисовать кривую целиком без анимации."""
        self.renderer.clear()
        self.renderer.draw_full(self.curve)
        self.done = True
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
                                  self.curve.is_polar and self.show_radius)
        self.renderer.draw_info(self._info_text())

    def _info_text(self):
        """Собрать подпись: формула, период и текущее значение t."""
        curve = self.curve
        lines = [curve.name, curve.formula()]
        petals = getattr(curve, "petals", lambda: None)()
        if petals:
            lines.append(f"лепестков: {petals}")
        t = min(self.index * curve.t_step, curve.period())
        if curve.t_step < 1:
            var = "θ" if curve.is_polar else "t"
            lines.append(f"{var} = {t / math.pi:5.2f}π  из "
                         f"{curve.period() / math.pi:.0f}π")
        else:
            lines.append(f"шаг {int(t)} из {int(curve.period())}")
        return "\n".join(lines)

    # ----- Обработчики панели управления --------------------------------

    def select_curve(self, name):
        """Переключиться на другую кривую с параметрами по умолчанию."""
        self.curve = curve_by_name(name)()
        self.panel.set_curve(self.curve)
        self.restart()

    def set_params(self, p1, p2):
        """Пересоздать кривую с новыми параметрами и начать заново."""
        if (p1, p2) == (self.curve.p1, self.curve.p2):
            return
        try:
            self.curve = type(self.curve)(p1, p2)
        except ValueError:
            # Слайдер ещё не перенастроен под новую кривую — пропускаем.
            return
        self.restart()

    def set_speed(self, speed):
        """Изменить число точек, добавляемых за один кадр."""
        self.speed = max(1, min(MAX_SPEED, speed))

    def toggle_pause(self):
        """Поставить анимацию на паузу или продолжить."""
        self.running = not self.running
        self.panel.set_paused(not self.running)

    def set_show_radius(self, value):
        """Включить или выключить радиус-вектор."""
        self.show_radius = value
        self._update_cursor()

    # ----- Клавиатура ---------------------------------------------------

    def _bind_keys(self):
        """Назначить горячие клавиши."""
        keys = {
            "<space>": lambda e: self.toggle_pause(),
            "<r>": lambda e: self.restart(),
            "<f>": lambda e: self.draw_instantly(),
            "<Left>": lambda e: self._shift_param(0, -1),
            "<Right>": lambda e: self._shift_param(0, 1),
            "<Down>": lambda e: self._shift_param(1, -1),
            "<Up>": lambda e: self._shift_param(1, 1),
            "<plus>": lambda e: self._shift_speed(2),
            "<equal>": lambda e: self._shift_speed(2),
            "<minus>": lambda e: self._shift_speed(-2),
            "<Escape>": lambda e: self.root.destroy(),
        }
        for key, handler in keys.items():
            self.root.bind(key, handler)
        # Русская раскладка: те же физические клавиши R и F.
        self.root.bind("<Cyrillic_ka>", lambda e: self.restart())
        self.root.bind("<Cyrillic_a>", lambda e: self.draw_instantly())

    def _shift_param(self, which, delta):
        """Изменить параметр which на delta в пределах диапазона."""
        params = list(self.panel.params())
        low, high = self.curve.param_ranges[which]
        params[which] = max(low, min(high, params[which] + delta))
        self.panel.set_params(*params)
        self.set_params(*params)

    def _shift_speed(self, delta):
        """Изменить скорость анимации на delta."""
        self.set_speed(self.speed + delta)
        self.panel.set_speed(self.speed)

    def run(self):
        """Запустить главный цикл tkinter."""
        self.root.mainloop()
