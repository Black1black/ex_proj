# Веб-сокет Чат

Этот проект представляет собой чат, реализованный с использованием веб-сокетов. Проект включает в себя функциональность определения онлайна пользователей и расстояния между собеседниками (С помощью PostGIS).
Авторизация с использованием jwt токенов - access (Если продолжу этот проект - планирую хранить в redis) и refresh (Уже реализовано хранение в PostgreSQL)

Это не полноценный проект, а простой пример для портфолио

Порт для запуска Flower  браузере - 5555
## Используемые технологии

- **Redis** - для кэширования и сообщения между сервисами.
- **PostGIS** - расширение к PostgreSQL для работы с географическими данными.
- **MongoDB** - база данных NoSQL для хранения сообщений и других данных.
- **MinIO** - система хранения объектов, совместимая с Amazon S3.
- **Docker** - для контейнеризации приложения.
- **FastAPI** - для создания RESTful API.
- **Celery** - для выполнения фоновых задач.
- **Flower** - для мониторинга задач Celery.
- **WebSocket** - для обеспечения работы чата в режиме реального времени.
- **Redis PubSub** - для обмена сообщениями в режиме реального времени между разными экземплярами приложения.


## Запуск проекта


1. Соберите Docker-образы:

   ```bash
   docker-compose build
   ```

2. Запустите проект:

   ```bash
   docker-compose up
   ```

3.  Создание бакетов s3
    ```
    В логах будет указан порт веб-интерфейса MinIO (каждый раз формируется динамически). После запуска, введите в браузере `http://localhost:<MINIOPORT> и создайте два бакета: mbuck и pbuck.```

## Замечания:
    Почемуто-то в этой версии FastAPI не удаётся отправить файл через swagger, но при тестировании через postman всё работает корректно

