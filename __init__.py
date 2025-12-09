""" Содержит асинхронный клиент для работы с HTTP запросами. """

from .aiohttp_client import AiohttpClient


# Экспортируемый интерфейс модуля
__all__ = [
    "AiohttpClient",
]