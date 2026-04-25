from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router
from app.core.logger import setup_logger
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
)
from app.middleware.logging_middleware import LoggingMiddleware


setup_logger()

app = FastAPI(title="FinChat API")

app.add_middleware(LoggingMiddleware)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "FinChat backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}