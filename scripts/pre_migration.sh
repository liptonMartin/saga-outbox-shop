#!/bin/bash

# Функция для запроса значения с дефолтом
read_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    local input

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        if [ -z "$input" ]; then
            input="$default"
        fi
    else
        read -p "$prompt: " input
    fi

    export "$var_name=$input"
}

echo "========================================="
echo "Настройка подключения к PostgreSQL"
echo "========================================="

read_with_default "Введите хост PostgreSQL" "localhost" "POSTGRES_HOST"
read_with_default "Введите порт PostgreSQL" "5432" "POSTGRES_PORT"
read_with_default "Введите имя пользователя PostgreSQL" "postgres" "POSTGRES_USER"

read -s -p "Введите пароль PostgreSQL: " POSTGRES_PASSWORD
echo
export POSTGRES_PASSWORD="$POSTGRES_PASSWORD"

read -p "Введите имя базы данных PostgreSQL: " POSTGRES_DB
export POSTGRES_DB="$POSTGRES_DB"

echo "========================================="
echo "Переменные окружения установлены:"
echo "POSTGRES_HOST=$POSTGRES_HOST"
echo "POSTGRES_PORT=$POSTGRES_PORT"
echo "POSTGRES_USER=$POSTGRES_USER"
echo "POSTGRES_PASSWORD=********"
echo "POSTGRES_DB=$POSTGRES_DB"
echo "========================================="
echo ""
echo "✅ Переменные доступны в текущей сессии терминала"