from fastapi import FastAPI

from src.entrypoints import api_v1 as v1

app = FastAPI(
    title="Simple Todo API",
    version="1.0",
    description="A very simple Todo API written by Dalean Barnett to demonstrate hosting APIs in Azure.",
)

app.include_router(v1.router)
