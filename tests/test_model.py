"""Тесты математической модели кривых.

Запуск: python -m unittest discover tests
"""

import math
import unittest

from src.models.animation_model import (CURVES, Hypotrochoid, Lissajous,
                                        MaurerRose, PolarRose, curve_by_name)


class TestPolarRose(unittest.TestCase):
    """Проверки полярной розы r = cos(n/d · θ)."""

    def test_period_even_and_odd(self):
        """Период: π·d при нечётных n и d, иначе 2π·d."""
        self.assertAlmostEqual(PolarRose(3, 1).period(), math.pi)
        self.assertAlmostEqual(PolarRose(2, 1).period(), 2 * math.pi)
        self.assertAlmostEqual(PolarRose(1, 2).period(), 4 * math.pi)
        self.assertAlmostEqual(PolarRose(3, 5).period(), 5 * math.pi)

    def test_period_uses_reduced_fraction(self):
        """Дробь 2/4 сокращается до 1/2."""
        self.assertEqual(PolarRose(2, 4).reduced(), (1, 2))
        self.assertAlmostEqual(PolarRose(2, 4).period(), 4 * math.pi)

    def test_petals(self):
        """k лепестков при нечётном k, 2k — при чётном."""
        self.assertEqual(PolarRose(3, 1).petals(), 3)
        self.assertEqual(PolarRose(4, 1).petals(), 8)
        self.assertIsNone(PolarRose(5, 2).petals())

    def test_radius_at_zero(self):
        """При θ = 0 радиус равен cos(0) = 1."""
        self.assertEqual(PolarRose(5, 3).point(0), (1.0, 0.0))

    def test_formula(self):
        """Формула показывает сокращённую дробь."""
        self.assertEqual(PolarRose(4, 1).formula(), "r = cos(4·θ)")
        self.assertEqual(PolarRose(6, 4).formula(), "r = cos(3/2·θ)")

    def test_invalid_params(self):
        """Параметры вне диапазона отклоняются."""
        with self.assertRaises(ValueError):
            PolarRose(0, 1)
        with self.assertRaises(ValueError):
            PolarRose(1, 13)


class TestAllCurves(unittest.TestCase):
    """Общие свойства для всех кривых и всех их параметров."""

    def _each_curve(self):
        """Перебрать все кривые на сетке допустимых параметров."""
        for cls in CURVES:
            (lo1, hi1), (lo2, hi2) = cls.param_ranges
            for p1 in range(lo1, hi1 + 1, max(1, (hi1 - lo1) // 4)):
                for p2 in range(lo2, hi2 + 1, max(1, (hi2 - lo2) // 4)):
                    yield cls(p1, p2)

    def test_curve_is_closed(self):
        """Первая и последняя точки совпадают — кривая замкнута."""
        for curve in self._each_curve():
            with self.subTest(curve=curve.name, p=(curve.p1, curve.p2)):
                x0, y0 = curve.sample(0)
                x1, y1 = curve.sample(curve.sample_count())
                self.assertAlmostEqual(x0, x1, places=6)
                self.assertAlmostEqual(y0, y1, places=6)

    def test_points_are_normalized(self):
        """Все точки лежат внутри единичного квадрата."""
        for curve in self._each_curve():
            with self.subTest(curve=curve.name, p=(curve.p1, curve.p2)):
                for x, y in curve.points():
                    self.assertLessEqual(abs(x), 1 + 1e-9)
                    self.assertLessEqual(abs(y), 1 + 1e-9)

    def test_defaults_are_valid(self):
        """Кривую можно создать без аргументов."""
        for cls in CURVES:
            self.assertEqual(cls().p1, cls.defaults[0])

    def test_curve_by_name(self):
        """Поиск кривой по названию."""
        self.assertIs(curve_by_name("Полярная роза"), PolarRose)
        with self.assertRaises(KeyError):
            curve_by_name("Нет такой")


class TestOtherCurves(unittest.TestCase):
    """Проверки дополнительных кривых."""

    def test_maurer_has_361_vertices(self):
        """У розы Маурера 360 отрезков и 361 вершина."""
        self.assertEqual(len(MaurerRose(6, 71).points()), 361)

    def test_lissajous_start(self):
        """При t = 0: x = sin(π/2) = 1, y = 0."""
        x, y = Lissajous(3, 2).point(0)
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, 0.0)

    def test_hypotrochoid_period(self):
        """Период спирографа: 2π · r / НОД(R, r)."""
        self.assertAlmostEqual(Hypotrochoid(7, 4).period(), 8 * math.pi)
        self.assertAlmostEqual(Hypotrochoid(6, 4).period(), 4 * math.pi)


if __name__ == "__main__":
    unittest.main()
