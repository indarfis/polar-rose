"""Панель управления: выбор кривой, слайдеры параметров и кнопки."""

import tkinter as tk
from tkinter import ttk

HELP_TEXT = (
    "Горячие клавиши:\n"
    "Space — пауза / продолжить\n"
    "R — начать заново\n"
    "F — нарисовать сразу\n"
    "← / → — параметр 1\n"
    "↓ / ↑ — параметр 2\n"
    "+ / − — скорость\n"
    "Esc — выход"
)


class ControlPanel(ttk.Frame):
    """Боковая панель с элементами управления анимацией.

    Панель ничего не знает о логике приложения: при действиях
    пользователя она вызывает переданные ей функции-обработчики.
    """

    def __init__(self, parent, curve_names, speed, on_curve, on_params,
                 on_speed, on_pause, on_reset, on_instant, on_radius):
        """Создать виджеты панели и связать их с обработчиками."""
        super().__init__(parent, padding=12)
        self._on_params = on_params
        self._silent = False

        ttk.Label(self, text="Кривая").pack(anchor="w")
        self.curve_var = tk.StringVar(value=curve_names[0])
        combo = ttk.Combobox(self, textvariable=self.curve_var,
                             values=curve_names, state="readonly",
                             width=24)
        combo.pack(fill="x", pady=(0, 10))
        combo.bind("<<ComboboxSelected>>",
                   lambda _e: on_curve(self.curve_var.get()))

        self.labels = []
        self.scales = []
        for _ in range(2):
            label = ttk.Label(self)
            label.pack(anchor="w")
            scale = tk.Scale(self, orient="horizontal", resolution=1,
                             length=210, command=self._params_changed)
            scale.pack(fill="x", pady=(0, 6))
            self.labels.append(label)
            self.scales.append(scale)

        ttk.Label(self, text="Скорость (точек за кадр)").pack(anchor="w")
        self.speed_scale = tk.Scale(
            self, orient="horizontal", from_=1, to=60, length=210,
            command=lambda v: on_speed(int(v)))
        self.speed_scale.set(speed)
        self.speed_scale.pack(fill="x", pady=(0, 10))

        self.radius_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Показывать радиус-вектор",
                        variable=self.radius_var,
                        command=lambda: on_radius(self.radius_var.get())
                        ).pack(anchor="w", pady=(0, 10))

        self.pause_button = ttk.Button(self, text="Пауза", command=on_pause)
        self.pause_button.pack(fill="x", pady=2)
        ttk.Button(self, text="Заново", command=on_reset).pack(fill="x",
                                                               pady=2)
        ttk.Button(self, text="Нарисовать сразу",
                   command=on_instant).pack(fill="x", pady=2)

        ttk.Label(self, text=HELP_TEXT, foreground="#666",
                  justify="left").pack(anchor="w", pady=(16, 0))

    def set_curve(self, curve):
        """Настроить подписи и диапазоны слайдеров под кривую."""
        self._silent = True
        for i in range(2):
            low, high = curve.param_ranges[i]
            self.labels[i].configure(text=f"Параметр {curve.param_names[i]}")
            self.scales[i].configure(from_=low, to=high)
            self.scales[i].set((curve.p1, curve.p2)[i])
        self._silent = False

    def params(self):
        """Вернуть текущие значения двух параметров."""
        return tuple(int(s.get()) for s in self.scales)

    def set_params(self, p1, p2):
        """Установить значения слайдеров (сработает обработчик)."""
        self.scales[0].set(p1)
        self.scales[1].set(p2)

    def set_speed(self, speed):
        """Установить значение слайдера скорости."""
        self.speed_scale.set(speed)

    def set_paused(self, paused):
        """Обновить надпись на кнопке паузы."""
        self.pause_button.configure(
            text="Продолжить" if paused else "Пауза")

    def _params_changed(self, _value):
        """Сообщить приложению о сдвиге любого из слайдеров."""
        if not self._silent:
            self._on_params(*self.params())
