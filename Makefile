up:
	docker compose -f docker-compose.dev.yml up --build

down:
	docker compose -f docker-compose.dev.yml up --build

revision:
	docker exec fastapi_severyanochka alembic revision --autogenerate -m "$(message)"

migrate:
	docker exec fastapi_severyanochka alembic upgrade heads