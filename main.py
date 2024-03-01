from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from api.routers import router as main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path('static/users/').mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory='static'))

origins = [
    'http://localhost',
    'http://localhost:8080',
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(main_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
