## Запуск
Простой запуск - `docker compose up`

Запуск тестов - `docker-compose -f ./tests/docker-compose.yml up --abort-on-container-exit --exit-code-from pytest`