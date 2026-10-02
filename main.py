"""Точка входа в программу «Полярная роза»."""

from src.app import App


def main():
    """Создать приложение и запустить главный цикл."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
