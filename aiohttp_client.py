from asyncio import run
from typing import (
    Mapping,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    Any,
)

from aiohttp import FormData, ClientResponse, ClientSession, CookieJar



Method = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
ResponsePayload = Tuple[Any, int, Mapping[str, str]]



class AiohttpClient:
    """
    ## Универсальный асинхронный `HTTP`-клиент поверх `aiohttp`.

    Поддерживает отправку запросов с `JSON`-телом, формами, бинарными данными
    и файлами, а также автоматический выбор способа чтения ответа.
    
    Attributes:
        base_url (str): Базовый URL API.
        session (Optional[ClientSession]): Асинхронная сессия для выполнения запросов.
        allowed_methods (Tuple[Method, ...]): Допустимые HTTP-методы для запросов.
        json_content_types (Set[str]): Типы контента, обрабатываемые как JSON.
        binary_content_types (Set[str]): Точные типы контента, читаемые как байты.
        binary_main_types (Set[str]): Основные типы контента, читаемые как байты.
    """
    def __init__(
        self,
        base_url: str = "",
        allowed_methods: Optional[Sequence[Method]] = None,
        json_content_types: Optional[Set[str]] = None,
        binary_content_types: Optional[Set[str]] = None,
        binary_main_types: Optional[Set[str]] = None,
    ):
        """
        ## Инициализирует клиент с указанным базовым URL.

        Args:
            base_url (str): Базовый URL API, добавляемый ко всем путям.
            allowed_methods (Sequence[str] | None): Допустимые HTTP-методы
                для запросов. Можно расширить список для соответствия
                принципу Open/Closed.
            json_content_types (set[str] | None): Набор типов контента,
                обрабатываемых как JSON.
            binary_content_types (set[str] | None): Набор точных типов
                контента, которые читаются как байты.
            binary_main_types (set[str] | None): Набор основных типов
                контента (часть до «/»), которые читаются как байты.
        """
        self.base_url = base_url
        self.session: Optional[ClientSession] = None
        self.allowed_methods: Tuple[Method, ...] = tuple(
            allowed_methods or ("GET", "POST", "PUT", "PATCH", "DELETE")
        )
        self.json_content_types: Set[str] = json_content_types or {"application/json"}
        self.binary_content_types: Set[str] = binary_content_types or {
            "application/octet-stream",
            "application/pdf",
        }
        self.binary_main_types: Set[str] = binary_main_types or {"image", "text"}

    async def __aenter__(self) -> "AiohttpClient":
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

    async def __aexit__(self, *args) -> None:
        """
        ## Выход из асинхронного контекстного менеджера.

        Args:
            *args: Параметры исключения, если произошла ошибка в блоке `with`.
        """
        if self.session:
            await self.session.close()

    def _ensure_method_allowed(self, method: Method) -> None:
        """
        ## Проверяет, что HTTP-метод разрешён.

        Args:
            method (str): HTTP-метод запроса.

        Raises:
            ValueError: Если метод не входит в список `allowed_methods`.
        """
        if method not in self.allowed_methods:
            allowed = ", ".join(self.allowed_methods)
            raise ValueError(f"Method '{method}' is not allowed. Allowed: {allowed}")

    async def _read_response(self, response: ClientResponse) -> Any:
        """
        ## Возвращает содержимое ответа в зависимости от `Content-Type`.

        Args:
            response (ClientResponse): Ответ, полученный от `aiohttp`.

        Returns:
            Any: Декодированное содержимое ответа.
        """
        content_type = response.content_type
        if content_type in self.json_content_types:
            return await response.json()

        main_type, _, _ = content_type.partition("/")
        if content_type in self.binary_content_types or main_type in self.binary_main_types:
            return await response.read()

        return await response.text()

    async def __request(self,
        method: Method,
        path: str,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
        data: Optional[Union[Dict[str, Any], FormData, bytes]] = None,
        files: Optional[Dict[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> ResponsePayload:
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
            tuple[Any, int, Mapping[str, str]]: Содержимое ответа,
                статус-код и заголовки.

        Raises:
            RuntimeError: Если сессия ещё не была инициализирована.
        """
        if not self.session:
            raise RuntimeError("Session not started")

        self._ensure_method_allowed(method)

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
            content = await self._read_response(response)
            return content, response.status, response.headers

    async def get(self, path: str, **kwargs) -> ResponsePayload:
        """
        ## Выполняет HTTP `GET`-запрос.

        Используется в основном для получения данных.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            tuple[Any, int, Mapping[str, str]]: Результат метода `request`.
        """
        return await self.__request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> ResponsePayload:
        """
        ## Выполняет HTTP `POST`-запрос.

        Обычно используется для создания или сохранения данных.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            tuple[Any, int, Mapping[str, str]]: Результат метода `request`.
        """
        return await self.__request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> ResponsePayload:
        """
        ## Выполняет HTTP `PUT`-запрос.

        Применяется для полного обновления объекта.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            tuple[Any, int, Mapping[str, str]]: Результат метода `request`.
        """
        return await self.__request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs) -> ResponsePayload:
        """
        ## Выполняет HTTP `PATCH`-запрос.

        Используется для частичного обновления объекта.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            tuple[Any, int, Mapping[str, str]]: Результат метода `request`.
        """
        return await self.__request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> ResponsePayload:
        """
        ## Выполняет HTTP `DELETE`-запрос.

        Используется для удаления ресурса.

        Args:
            path (str): Путь к ресурсу.
            **kwargs: Дополнительные параметры, пробрасываемые в `request`.

        Returns:
            tuple[Any, int, Mapping[str, str]]: Результат метода `request`.
        """
        return await self.__request("DELETE", path, **kwargs)


# Экспортируемый интерфейс модуля
__all__ = [
    "AiohttpClient",
]


# Пример использования клиента в асинхронном контексте
if __name__ == "__main__":
    from logging import basicConfig, getLogger, INFO
    basicConfig(level=INFO)
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