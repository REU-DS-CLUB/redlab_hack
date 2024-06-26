"""
Входная точка для приложения FastAPI
"""
import uvicorn
from fastapi import FastAPI
from handlers.handlers import handlers

app = FastAPI()
app.include_router(handlers)


def start():
    uvicorn.run(app='main:app',
                host="0.0.0.0",
                port=8000,
                workers=4,
                env_file='../.env'
                )


if __name__ == '__main__':
    start()
