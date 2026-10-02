"""Главное окно приложения."""

import tkinter as tk

CANVAS_SIZE = 600
BG_COLOR = "#0f1117"


class App:
    """Окно с холстом для рисования."""

    def __init__(self):
        """Создать окно и холст."""
        self.root = tk.Tk()
        self.root.title("Полярная роза — Тасоев Арсен")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=CANVAS_SIZE,
                                height=CANVAS_SIZE, bg=BG_COLOR,
                                highlightthickness=0)
        self.canvas.pack()

    def run(self):
        """Запустить главный цикл tkinter."""
        self.root.mainloop()
