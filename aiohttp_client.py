import asyncio
from typing import Optional, Union, Dict, List, Any

from aiohttp import FormData, ClientSession, hdrs



class AiohttpClient:
    """
    ## Универсальный клиент для работы с API поддерживающий разные форматы данных.
    """
    def __init__(self, base_url: str = ""):
        """
        ## Инициализация клиента.

        :param base_url: Базовый URL для API.
        """
        self.base_url = base_url
        self.session: Optional[ClientSession] = None

    async def __aenter__(self):
        """
        ## Вход в асинхронный контекстный менеджер.

        :return: Экземпляр `AiohttpClient`.
        """
        self.session = ClientSession(base_url=self.base_url)
        return self

    async def __aexit__(self, *args):
        """
        ## Выход из асинхронного контекстного менеджера.

        :param args: Аргументы исключения, если они есть.
        """
        if self.session:
            await self.session.close()

    async def request(
        self,
        method: str,
        path: str,
        json: Optional[Union[Dict, List]] = None,
        data: Optional[Union[Dict, FormData, bytes]] = None,
        files: Optional[Dict[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        ## Выполнение HTTP-запроса.

        :param method: HTTP-метод (GET, POST, PUT, DELETE).
        :param path: Путь к ресурсу.
        :param json: Данные в формате JSON для отправки.
        :param data: Данные для отправки (может быть словарем, FormData или байтами).
        :param files: Файлы для загрузки.
        :param headers: Заголовки запроса.
        :return: Кортеж (содержимое ответа, статус ответа, заголовки ответа).
        :raises RuntimeError: Если сессия не была инициализирована.
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
            headers=headers
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
        ## Выполнение HTTP `GET`-запроса.

        ### Используется для получения данных.
        
        :param path: Путь к ресурсу.
        :param kwargs: Дополнительные параметры для запроса.
        :return: Кортеж (содержимое ответа, статус ответа, заголовки ответа).
        """
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs):
        """
        ## Выполнение HTTP `POST`-запроса.

        ### Используется для сохранения и получения данных.

        :param path: Путь к ресурсу.
        :param kwargs: Дополнительные параметры для запроса.
        :return: Кортеж (содержимое ответа, статус ответа, заголовки ответа).
        """
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs):
        """
        ## Выполнение HTTP `PUT`-запроса.

        ### Используется для полного обновления объекта данных.
        
        :param path: Путь к ресурсу.
        :param kwargs: Дополнительные параметры для запроса.
        :return: Кортеж (содержимое ответа, статус ответа, заголовки ответа).
        """
        return await self.request("PUT", path, **kwargs)

    async def patch(self, path: str, **kwargs) -> Any:
        """
        ## Выполнение HTTP `PATCH`-запроса.

        ### Используется для частичного обновления объекта данных.

        :param path: Путь к ресурсу.
        :param kwargs: Дополнительные параметры для запроса.
        :return: Кортеж (содержимое ответа, статус ответа, заголовки ответа).
        """
        return await self.request("PATCH", path, **kwargs)

    async def delete(self, path: str, **kwargs):
        """
        ## Выполнение HTTP `DELETE`-запроса.

        ### Используется для удаления объекта данных.
        
        :param path: Путь к ресурсу.
        :param kwargs: Дополнительные параметры для запроса.
        :return: Кортеж (содержимое ответа, статус ответа, заголовки ответа).
        """
        return await self.request("DELETE", path, **kwargs)


# Пример использования
async def main():
    base_url =  "https://jsonplaceholder.typicode.com"  # Замените на ваш базовый URL

    async with AiohttpClient(base_url=base_url) as client:
        # Выполнение GET-запроса
        content, status, headers = await client.get(path='/posts/1')
        print('\nGET запрос')
        print(f'\nContent: {content}')
        print(f'\nStatus: {status}')
        print(f'\nHeaders: {headers}')

        # Выполнение POST-запроса
        data = {'title': 'foo', 'body':'bar', 'userId':1}  # Замените на ваши данные
        content, status, headers = await client.post(
            path='/posts/', json=data,
            headers={'Content-type':'application/json; charset=UTF-8'}
        )
        print('\n\n\n\n\nPOST запрос')
        print(f'\nContent: {content}')
        print(f'\nStatus: {status}')
        print(f'\nHeaders: {headers}')

        # Выполнение PATCH-запроса
        data = {'title': 'updated title'}  # Замените на ваши данные
        content, status, headers = await client.patch(
            path='/posts/1', json=data,
            headers={'Content-type': 'application/json; charset=UTF-8'}
        )
        print('\n\n\n\n\nPATCH запрос')
        print(f'\nContent: {content}')
        print(f'\nStatus: {status}')
        print(f'\nHeaders: {headers}')

        # Выполнение PUT-запроса
        # Замените на ваши данные
        data = {'id': 1, 'title': 'updated title', 'body': 'updated body', 'userId': 1}  
        content, status, headers = await client.put(
            path='/posts/1', json=data,
            headers={'Content-type': 'application/json; charset=UTF-8'}
        )
        print('\n\n\n\n\nPUT запрос')
        print(f'\nContent: {content}')
        print(f'\nStatus: {status}')
        print(f'\nHeaders: {headers}')

        # Выполнение DELETE-запроса
        content, status, headers = await client.delete(path='/posts/1')
        print('\n\n\n\n\nDELETE запрос')
        print(f'\nContent: {content}')  # Обычно для DELETE запросов контент пустой
        print(f'\nStatus: {status}')
        print(f'\nHeaders: {headers}')


if __name__ == "__main__":
    # Запуск асинхронной функции
    asyncio.run(main())