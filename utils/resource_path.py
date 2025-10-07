import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Возвращает корректный путь к ресурсу (для .exe и при разработке).
    """
    if getattr(sys, "_MEIPASS", False):
        # когда приложение запущено как exe
        base_path = sys._MEIPASS
    else:
        # когда запускаем из исходников
        base_path = os.path.abspath(os.path.dirname(__file__))
        base_path = os.path.join(
            base_path, os.pardir
        )  # подняться на уровень выше (к корню проекта)
    return os.path.abspath(os.path.join(base_path, relative_path))
