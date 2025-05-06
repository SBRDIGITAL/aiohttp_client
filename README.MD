# AiohttpClient

## Описание
`AiohttpClient` — это универсальный асинхронный клиент для работы с API, поддерживающий различные форматы данных. Он использует библиотеку `aiohttp` для выполнения HTTP-запросов и предоставляет удобный интерфейс для работы с RESTful API.

## Установка
Для использования `AiohttpClient`, убедитесь, что у вас установлен Python 3.7 или выше и библиотека `aiohttp`. Вы можете установить `aiohttp` с помощью pip:
```bash
pip install aiohttp
```

## Использование

### Инициализация клиента
Создайте экземпляр `AiohttpClient`, передав базовый URL вашего API:

```python
client = AiohttpClient(base_url="https://api.example.com")
```

### Асинхронный контекстный менеджер
`AiohttpClient` поддерживает асинхронный контекстный менеджер, что позволяет автоматически управлять сессией:
```python
async with AiohttpClient(base_url="https://api.example.com") as client:
    # Ваш код здесь
```

### Выполнение запросов
Класс предоставляет методы для выполнения различных HTTP-запросов:
- **GET**: Получение данных
- **POST**: Создание новых данных
- **PUT**: Полное обновление данных
- **PATCH**: Частичное обновление данных
- **DELETE**: Удаление данных

---

#### Пример использования

```python
import asyncio

async def main():
    async with AiohttpClient(base_url="https://jsonplaceholder.typicode.com") as client:
        # Выполнение GET-запроса
        content, status, headers = await client.get(path='/posts/1')
        print(f'GET запрос: {content}, Статус: {status}, Заголовки: {headers}')

        # Выполнение POST-запроса
        data = {'title': 'foo', 'body': 'bar', 'userId': 1}
        content, status, headers = await client.post(path='/posts/', json=data)
        print(f'POST запрос: {content}, Статус: {status}, Заголовки: {headers}')

        # Выполнение PATCH-запроса
        patch_data = {'title': 'updated title'}
        content, status, headers = await client.patch(path='/posts/1', json=patch_data)
        print(f'PATCH запрос: {content}, Статус: {status}, Заголовки: {headers}')

        # Выполнение PUT-запроса
        put_data = {'id': 1, 'title': 'updated title', 'body': 'updated body', 'userId': 1}
        content, status, headers = await client.put(path='/posts/1', json=put_data)
        print(f'PUT запрос: {content}, Статус: {status}, Заголовки: {headers}')

        # Выполнение DELETE-запроса
        content, status, headers = await client.delete(path='/posts/1')
        print(f'DELETE запрос: {content}, Статус: {status}, Заголовки: {headers}')

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Объяснение структуры README:
- **Описание**: Краткое введение в то, что такое `AiohttpClient`.
- **Установка**: Инструкции по установке необходимых зависимостей.
- **Использование**: Примеры и объяснения, как инициализировать клиент и выполнять запросы.
- **Пример использования**: Полный пример кода, демонстрирующий, как использовать клиент.
