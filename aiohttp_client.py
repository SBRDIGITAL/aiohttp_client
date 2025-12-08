from asyncio import run
from typing import Literal, Optional, Union, Dict, List, Any

from aiohttp import FormData, ClientSession, CookieJar, hdrs



class AiohttpClient:
    """
    ## Универсальный асинхронный `HTTP`-клиент поверх `aiohttp`.

    Поддерживает отправку запросов с `JSON`-телом, формами, бинарными данными
    и файлами, а также автоматический выбор способа чтения ответа.
    
    Attributes:
        base_url (str): Базовый URL API.
        session (Optional[ClientSession]): Асинхронная сессия для выполнения запросов.
    """
    def __init__(self, base_url: str = ""):
        """
        ## Инициализирует клиент с указанным базовым URL.

        Args:
            base_url (str): Базовый URL API, добавляемый ко всем путям.
        """
        self.base_url = base_url
        self.session: Optional[ClientSession] = None

    async def __aenter__(self):
        """
        ## Вход в асинхронный контекстный менеджер.

        Returns:
            AiohttpClient: Текущий экземпляр клиента с активной сессией.
        """
        self.session = ClientSession(
            base_url=self.base_url,
            cookie_jar=CookieJar(unsafe=True)
        )
        return self

    async def __aexit__(self, *args):
        """
        ## Выход из асинхронного контекстного менеджера.

        Args:
            *args: Параметры исключения, если произошла ошибка в блоке `with`.
        """
        if self.session:
            await self.session.close()

    async def __request(self,
        method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
        path: str,
        json: Optional[Union[Dict, List]] = None,
        data: Optional[Union[Dict, FormData, bytes]] = None,
        files: Optional[Dict[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        ## Выполняет HTTP-запрос с учётом формата данных.

        Args:
            method (str): HTTP-метод ("GET", "POST" и т.д.).
            path (str): Путь к ресурсу относительно `base_url`.
            json (dict | list | None): JSON-данные для отправки.
            data (dict | FormData | bytes | None): Данные формы или сырые байты.
            files (Dict[str, bytes] | None): Файлы для загрузки.
            headers (Dict[str, str] | None): Дополнительные заголовки запроса.
            params (Dict[str, str] | None): Query-параметры строки запроса.

        Returns:
            Any: Содержимое ответа, статус-код и заголовки.

        Raises:
            RuntimeError: Если сессия ещё не была инициализирована.
        """
        if not self.session:
            raise RuntimeError("Session not started")

        # Обработка файлов
        if files:
            data = FormData()
            for name, content in files.items():
                data.add_field(name, content, filename=name)

        # Отправка запроса
        async with self.session.request(
            method=method,
            url=path,
            json=json,
            data=data,
            headers=headers,
            params=params
        ) as response:
            # Определение типа контента
            content_type = response.headers.get(hdrs.CONTENT_TYPE, "")
            # Обработка JSON
            if "application/json" in content_type:
                return await response.json(), response.status, response.headers

            # Обработка файлов и бинарных данных
            if any(x in content_type for x in ["octet-stream", "pdf", "image", "text"]):
                content = await response.read()
                return content, response.status, response.headers

            # Обработка текста
            return await response.text(), response.status, response.headers

    async def get(self, path: str, **kwargs):
        """
        ## Выполняет HTTP `GET`-запрос.

        Используется в основном для получения данных.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            Any: Результат метода `request`.
        """
        return await self.__request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs):
        """
        ## Выполняет HTTP `POST`-запрос.

        Обычно используется для создания или сохранения данных.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            Any: Результат метода `request`.
        """
        return await self.__request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs):
        """
        ## Выполняет HTTP `PUT`-запрос.

        Применяется для полного обновления объекта.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            Any: Результат метода `request`.
        """
        return await self.__request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs) -> Any:
        """
        ## Выполняет HTTP `PATCH`-запрос.

        Используется для частичного обновления объекта.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            Any: Результат метода `request`.
        """
        return await self.__request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs):
        """
        ## Выполняет HTTP `DELETE`-запрос.

        Используется для удаления ресурса.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            Any: Результат метода `request`.
        """
        return await self.__request("DELETE", path, **kwargs)


# Экспортируемый интерфейс модуля
__all__ = [
    "AiohttpClient",
    ]


if __name__ == "__main__":
    from logging import getLogger
    logger = getLogger(__name__)

    # Пример использования
    async def main():
        base_url =  "https://jsonplaceholder.typicode.com"  # Замените на ваш базовый URL

        async with AiohttpClient(base_url=base_url) as client:
            # Выполнение GET-запроса с params
            params = {'userId': '1'}  # Пример query-параметров
            content, status, headers = await client.get(path='/posts', params=params)
            logger.info('GET запрос с params')
            logger.info(f'Content: {content}')
            logger.info(f'Status: {status}')
            logger.info(f'Headers: {headers}')

            # Выполнение GET-запроса
            content, status, headers = await client.get(path='/posts/1')
            logger.info('GET запрос')
            logger.info(f'Content: {content}')
            logger.info(f'Status: {status}')
            logger.info(f'Headers: {headers}')

            # Выполнение POST-запроса
            data = {'title': 'foo', 'body':'bar', 'userId':1}  # Замените на ваши данные
            content, status, headers = await client.post(
                path='/posts/', json=data,
                headers={'Content-type':'application/json; charset=UTF-8'}
            )
            logger.info('POST запрос')
            logger.info(f'Content: {content}')
            logger.info(f'Status: {status}')
            logger.info(f'Headers: {headers}')

            # Выполнение PATCH-запроса
            data = {'title': 'updated title'}  # Замените на ваши данные
            content, status, headers = await client.patch(
                path='/posts/1', json=data,
                headers={'Content-type': 'application/json; charset=UTF-8'}
            )
            logger.info('PATCH запрос')
            logger.info(f'Content: {content}')
            logger.info(f'Status: {status}')
            logger.info(f'Headers: {headers}')

            # Выполнение PUT-запроса
            # Замените на ваши данные
            data = {'id': 1, 'title': 'updated title', 'body': 'updated body', 'userId': 1}  
            content, status, headers = await client.put(
                path='/posts/1', json=data,
                headers={'Content-type': 'application/json; charset=UTF-8'}
            )
            logger.info('PUT запрос')
            logger.info(f'Content: {content}')
            logger.info(f'Status: {status}')
            logger.info(f'Headers: {headers}')

            # Выполнение DELETE-запроса
            content, status, headers = await client.delete(path='/posts/1')
            logger.info('DELETE запрос')
            logger.info(f'Content: {content}')  # Обычно для DELETE запросов контент пустой
            logger.info(f'Status: {status}')
            logger.info(f'Headers: {headers}')

    run(main())  # Запуск асинхронной функции