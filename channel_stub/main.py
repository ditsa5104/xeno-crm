from fastapi import FastAPI
from routers import send, health, metrics

app = FastAPI(title="Xeno Channel Stub", version="1.0")
app.include_router(send.router)
app.include_router(health.router)
app.include_router(metrics.router)
