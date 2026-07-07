Миграции накатываются с помощью библиотеки `yoyo-migrations`. В каждом сервисе своя база данных, поэтому для каждого
сервиса есть свой yoyo.ini файл и свои миграции. Однако процесс написания миграций и накатывания остается универсальным.

0. Для создания миграций в новом сервисе используйте

```bash
yoyo init --database postgresql://user:password@localhost/mydb ./migrations
```

1. Убедитесь, что в текущей сессии терминала проброшены следующие переменные окружения:

```bash
export POSTGRES_USER=
export POSTGRES_PASSWORD=
export POSTGRES_HOST=
export POSTGRES_DB=
export POSTGRES_PORT=
```

Если вы используете Windows, то вместо `export` необходимо использовать `$env:VAR_NAME=`

2. Для создания новой миграции используйте

```bash
yoyo new ./migrations -m "Create users table"
```

3. Заполните созданную миграцию в ./migrations

4. Примените миграции

```bash
yoyo apply
```

5. Для отмены миграций используйте

```bash
yoyo rollback
```
