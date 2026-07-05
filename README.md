## SAGA-outbox shop
Название проекта связано с паттернами архитектуры, используемые в приложении 
# Микросервисное приложение на Python
Подробные требования описаны в `docs/requirements.md`

Стек:

- Язык: Python 3.13
- Инфраструктура: Git, Docker, RabbitMQ, PostgreSQL
- Используемые библиотеки: FastAPI, asynpg, yoyo-migrations, pydantic, aio-pika

Архитектурные решения:

- Orchestration SAGA
- Outbox pattern
- Database per Service
- Repository - паттерн проектирования для работы с базой данных
