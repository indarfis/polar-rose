"""Математические модели параметрических кривых.

Каждая кривая задаётся двумя целыми параметрами и умеет вычислять
точку по значению параметра t. Координаты нормированы так, чтобы
кривая помещалась в квадрат [-1; 1] x [-1; 1], — масштабирование
под размер холста выполняет рендерер.
"""

import math
from abc import ABC, abstractmethod


class Curve(ABC):
    """Базовый класс параметрической кривой с двумя параметрами."""

    #: Название кривой для списка выбора.
    name = "Кривая"
    #: Подписи параметров для слайдеров.
    param_names = ("p1", "p2")
    #: Допустимые диапазоны параметров (включительно).
    param_ranges = ((1, 10), (1, 10))
    #: Значения параметров по умолчанию.
    defaults = (1, 1)
    #: Шаг параметра t между соседними точками.
    t_step = 0.01
    #: Является ли кривая полярной (для отрисовки радиус-вектора).
    is_polar = False

    def __init__(self, p1=None, p2=None):
        """Создать кривую с параметрами p1 и p2.

        Если параметр не задан, берётся значение по умолчанию.
        """
        self.p1 = self.defaults[0] if p1 is None else int(p1)
        self.p2 = self.defaults[1] if p2 is None else int(p2)
        self._validate()

    def _validate(self):
        """Проверить, что параметры попадают в допустимые диапазоны."""
        for value, (low, high), label in zip(
                (self.p1, self.p2), self.param_ranges, self.param_names):
            if not low <= value <= high:
                raise ValueError(
                    f"Параметр {label}={value} вне диапазона "
                    f"[{low}; {high}]")

    @abstractmethod
    def period(self):
        """Вернуть длину промежутка t, за который кривая замыкается."""

    @abstractmethod
    def point(self, t):
        """Вернуть нормированную точку (x, y) кривой при параметре t."""

    @abstractmethod
    def formula(self):
        """Вернуть строку с формулой кривой для подписи на экране."""

    def sample_count(self):
        """Вернуть количество отрезков, из которых строится кривая."""
        return max(1, math.ceil(self.period() / self.t_step))

    def sample(self, i):
        """Вернуть i-ю точку кривой (i от 0 до sample_count())."""
        return self.point(min(i * self.t_step, self.period()))

    def points(self):
        """Вернуть список всех точек замкнутой кривой."""
        return [self.sample(i) for i in range(self.sample_count() + 1)]


class PolarRose(Curve):
    """Полярная роза r = cos(k·θ), где k = n / d.

    При целом k у розы k лепестков, если k нечётно, и 2k лепестков,
    если k чётно. При дробном k лепестки перекрываются, и кривая
    замыкается не за один оборот.
    """

    name = "Полярная роза"
    param_names = ("n", "d")
    param_ranges = ((1, 12), (1, 12))
    defaults = (4, 1)
    is_polar = True

    def reduced(self):
        """Вернуть несократимую дробь (n, d) для k = n / d."""
        g = math.gcd(self.p1, self.p2)
        return self.p1 // g, self.p2 // g

    def period(self):
        """Вернуть период розы по углу θ.

        Для несократимой дроби n/d: если n и d оба нечётные, то
        cos(k(θ + πd)) = cos(kθ + πn) = -cos(kθ), и точка с
        отрицательным r совпадает с исходной — период равен π·d.
        Иначе период равен 2π·d.
        """
        n, d = self.reduced()
        if n % 2 == 1 and d % 2 == 1:
            return math.pi * d
        return 2 * math.pi * d

    def radius(self, theta):
        """Вернуть полярный радиус r(θ) = cos(n/d · θ)."""
        return math.cos(self.p1 / self.p2 * theta)

    def point(self, t):
        """Перевести полярные координаты (r, θ) в декартовы."""
        r = self.radius(t)
        return r * math.cos(t), r * math.sin(t)

    def petals(self):
        """Вернуть число лепестков для целого k или None для дробного."""
        n, d = self.reduced()
        if d != 1:
            return None
        return n if n % 2 == 1 else 2 * n

    def formula(self):
        """Вернуть формулу розы с текущими параметрами."""
        n, d = self.reduced()
        k = str(n) if d == 1 else f"{n}/{d}"
        return f"r = cos({k}·θ)"


class MaurerRose(Curve):
    """Роза Маурера: ломаная по 361 точке полярной розы r = sin(n·θ).

    k-я вершина лежит на розе при угле θ_k = k·d градусов,
    k = 0, 1, ..., 360. Соседние вершины соединяются отрезками,
    поэтому параметр t здесь — целый номер вершины.
    """

    name = "Роза Маурера"
    param_names = ("n", "d°")
    param_ranges = ((1, 12), (1, 179))
    defaults = (6, 71)
    t_step = 1
    is_polar = True

    def period(self):
        """Вернуть число отрезков ломаной (360)."""
        return 360

    def point(self, t):
        """Вернуть вершину с номером t."""
        theta = math.radians(t * self.p2)
        r = math.sin(self.p1 * theta)
        return r * math.cos(theta), r * math.sin(theta)

    def formula(self):
        """Вернуть формулу розы Маурера."""
        return f"r = sin({self.p1}·θ),  θ = k·{self.p2}°"


class Lissajous(Curve):
    """Фигура Лиссажу: x = sin(a·t + π/2), y = sin(b·t)."""

    name = "Фигура Лиссажу"
    param_names = ("a", "b")
    param_ranges = ((1, 10), (1, 10))
    defaults = (3, 2)

    def period(self):
        """Синусы с целыми частотами повторяются через 2π."""
        return 2 * math.pi

    def point(self, t):
        """Вернуть точку фигуры Лиссажу (уже лежит в [-1; 1])."""
        return math.sin(self.p1 * t + math.pi / 2), math.sin(self.p2 * t)

    def formula(self):
        """Вернуть формулу фигуры Лиссажу."""
        return f"x = sin({self.p1}t + π/2),  y = sin({self.p2}t)"


class Hypotrochoid(Curve):
    """Гипотрохоида (спирограф).

    Окружность радиуса r катится внутри окружности радиуса R,
    рисующая точка удалена от центра малой окружности на h = 0.8·r:
        x = (R − r)·cos t + h·cos((R − r)/r · t)
        y = (R − r)·sin t − h·sin((R − r)/r · t)
    """

    name = "Спирограф (гипотрохоида)"
    param_names = ("R", "r")
    param_ranges = ((2, 15), (1, 14))
    defaults = (7, 4)
    HOLE = 0.8

    def period(self):
        """Кривая замыкается, когда малая окружность сделает целое
        число оборотов: t = 2π · r / НОД(R, r)."""
        return 2 * math.pi * self.p2 / math.gcd(self.p1, self.p2)

    def point(self, t):
        """Вернуть точку гипотрохоиды, делённую на её макс. радиус."""
        big, small = self.p1, self.p2
        h = self.HOLE * small
        diff = big - small
        x = diff * math.cos(t) + h * math.cos(diff / small * t)
        y = diff * math.sin(t) - h * math.sin(diff / small * t)
        # Максимальное удаление от центра: |R − r| + h.
        extent = abs(diff) + h
        return x / extent, y / extent

    def formula(self):
        """Вернуть параметры спирографа."""
        return f"R = {self.p1}, r = {self.p2}, h = {self.HOLE}·r"


#: Все доступные кривые в порядке отображения в списке.
CURVES = [PolarRose, MaurerRose, Lissajous, Hypotrochoid]


def curve_by_name(name):
    """Найти класс кривой по названию."""
    for cls in CURVES:
        if cls.name == name:
            return cls
    raise KeyError(name)
