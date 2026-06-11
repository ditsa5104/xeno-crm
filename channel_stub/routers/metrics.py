from fastapi import APIRouter
from simulator.metrics_store import metrics_store

router = APIRouter()


@router.get('/metrics')
def metrics():
    return metrics_store.snapshot()
