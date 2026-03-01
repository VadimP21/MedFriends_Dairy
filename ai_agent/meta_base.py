"""Модуль содержит базовый метакласс для реализации паттерна Singleton."""

from typing import Dict, Any
from threading import Lock


class MetaBaseSingleton(type):
    """
    Потокобезопасный метакласс для реализации паттерна Singleton.

    Гарантирует, что у класса будет только один экземпляр.
    При повторном вызове конструктора возвращает ранее созданный экземпляр.

    Пример использования:
        class MyClass(metaclass=MetaBaseSingleton):
            def __init__(self, value):
                self.value = value

        # Оба объекта будут ссылаться на один и тот же экземпляр
        a = MyClass(10)
        b = MyClass(20)  # Вернет тот же объект, value останется 10
        assert a is b  # True
    """

    # Хранилище созданных экземпляров для каждого класса
    _instances: Dict[type, object] = {}

    # Блокировка для потокобезопасности
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        Переопределяет вызов конструктора класса.

        Args:
            *args: Позиционные аргументы конструктора
            **kwargs: Именованные аргументы конструктора

        Returns:
            Существующий или новый экземпляр класса
        """
        # Быстрая проверка без блокировки (для оптимизации)
        if cls not in cls._instances:
            # Блокируем для потокобезопасности
            with cls._lock:
                # Проверяем еще раз после захвата блокировки
                if cls not in cls._instances:
                    # Создаем новый экземпляр
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance

        return cls._instances[cls]

    @classmethod
    def clear_instance(cls, cls_to_clear: type) -> None:
        """
        Очищает сохраненный экземпляр для указанного класса.
        Полезно для тестирования или переинициализации.

        Args:
            cls_to_clear: Класс, экземпляр которого нужно очистить
        """
        with cls._lock:
            if cls_to_clear in cls._instances:
                del cls._instances[cls_to_clear]

    @classmethod
    def clear_all_instances(cls) -> None:
        """Очищает все сохраненные экземпляры (для тестирования)."""
        with cls._lock:
            cls._instances.clear()

    @classmethod
    def instance_exists(cls, cls_to_check: type) -> bool:
        """
        Проверяет, существует ли экземпляр для указанного класса.

        Args:
            cls_to_check: Класс для проверки

        Returns:
            True если экземпляр уже создан, иначе False
        """
        return cls_to_check in cls._instances


class AsyncMetaBaseSingleton(MetaBaseSingleton):
    """
    Асинхронная версия метакласса Singleton.
    Поддерживает асинхронную инициализацию через __ainit__.
    """

    async def __acall__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        Асинхронный вызов конструктора.
        Ожидает, что у класса есть метод __ainit__ для асинхронной инициализации.

        Пример:
            class AsyncClass(metaclass=AsyncMetaBaseSingleton):
                async def __ainit__(self, value):
                    self.value = value
                    await self.some_async_setup()
        """
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    # Создаем экземпляр без вызова __init__
                    instance = cls.__new__(cls)

                    # Вызываем асинхронную инициализацию, если она есть
                    if hasattr(instance, '__ainit__'):
                        await instance.__ainit__(*args, **kwargs)
                    else:
                        # Иначе обычный __init__
                        instance.__init__(*args, **kwargs)

                    cls._instances[cls] = instance

        return cls._instances[cls]