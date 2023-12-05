web: gunicorn -w 3 -k uvicorn.workers.UvicornWorker main:app
release: alembic upgrade head