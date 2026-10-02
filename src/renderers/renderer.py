"""Отрисовка кривых, сетки и курсора на холсте tkinter."""

import colorsys
import math

GRID_COLOR = "#262a36"
AXIS_COLOR = "#3a3f4f"
TEXT_COLOR = "#c9cdd8"
CURSOR_COLOR = "#ffffff"
RADIUS_COLOR = "#ffb347"
LINE_WIDTH = 2
#: Сколько точек объединяется в одну ломаную при мгновенной отрисовке.
CHUNK = 25


def gradient_color(fraction):
    """Вернуть цвет радуги для доли пройденного пути fraction ∈ [0; 1].

    Тон (hue) меняется по кругу HSV, поэтому начало и конец кривой
    плавно переходят друг в друга.
    """
    hue = (0.55 + fraction) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 1.0)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


class Renderer:
    """Рисует нормированные кривые в квадратной области холста."""

    def __init__(self, canvas, size, margin=0.9):
        """Связать рендерер с холстом размера size × size.

        margin — доля полуразмера холста, занимаемая кривой.
        """
        self.canvas = canvas
        self.size = size
        self.center = size / 2
        self.scale = size / 2 * margin
        self._cursor = None
        self._radius = None
        self._info = None
        self.draw_grid()

    def to_screen(self, point):
        """Перевести нормированную точку (x, y) в пиксели холста.

        Ось Y на экране направлена вниз, поэтому y берётся с минусом.
        """
        x, y = point
        return self.center + x * self.scale, self.center - y * self.scale

    def draw_grid(self):
        """Нарисовать полярную сетку: окружности и лучи через 30°."""
        c, s = self.center, self.scale
        for i in range(1, 5):
            r = s * i / 4
            self.canvas.create_oval(c - r, c - r, c + r, c + r,
                                    outline=GRID_COLOR, tags="grid")
        for angle in range(0, 180, 30):
            a = math.radians(angle)
            dx, dy = s * math.cos(a), s * math.sin(a)
            color = AXIS_COLOR if angle in (0, 90) else GRID_COLOR
            self.canvas.create_line(c - dx, c + dy, c + dx, c - dy,
                                    fill=color, tags="grid")

    def clear(self):
        """Удалить кривую и курсор, оставив сетку."""
        self.canvas.delete("curve", "cursor")
        self._cursor = self._radius = None

    def draw_path(self, points, fraction):
        """Нарисовать ломаную по точкам одним цветом градиента."""
        if len(points) < 2:
            return
        coords = []
        for p in points:
            coords.extend(self.to_screen(p))
        self.canvas.create_line(*coords, fill=gradient_color(fraction),
                                width=LINE_WIDTH, capstyle="round",
                                joinstyle="round", tags="curve")

    def draw_full(self, curve):
        """Нарисовать всю кривую сразу, разбив её на цветные участки."""
        points = curve.points()
        total = len(points) - 1
        for start in range(0, total, CHUNK):
            end = min(start + CHUNK, total)
            self.draw_path(points[start:end + 1], start / total)

    def draw_cursor(self, point, show_radius):
        """Показать текущую точку и (для полярных кривых) радиус-вектор."""
        x, y = self.to_screen(point)
        r = 5
        if self._cursor is None:
            self._radius = self.canvas.create_line(
                self.center, self.center, x, y, fill=RADIUS_COLOR,
                width=1, dash=(4, 3), tags="cursor")
            self._cursor = self.canvas.create_oval(
                x - r, y - r, x + r, y + r, fill=CURSOR_COLOR,
                outline="", tags="cursor")
        self.canvas.coords(self._radius, self.center, self.center, x, y)
        self.canvas.itemconfigure(
            self._radius, state="normal" if show_radius else "hidden")
        self.canvas.coords(self._cursor, x - r, y - r, x + r, y + r)
        self.canvas.tag_raise("cursor")

    def draw_info(self, text):
        """Вывести текст с параметрами в левом верхнем углу."""
        if self._info is None:
            self._info = self.canvas.create_text(
                12, 12, anchor="nw", fill=TEXT_COLOR,
                font=("Consolas", 11))
        self.canvas.itemconfigure(self._info, text=text)
        self.canvas.tag_raise(self._info)
