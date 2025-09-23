from fastapi import FastAPI, Response
import random
import time
from prometheus_client import Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import PlainTextResponse

app = FastAPI()

# Métricas Prometheus
REQUEST_TIME = Histogram(
    "http_request_duration_seconds",
    "Duración de las solicitudes HTTP",
    ["route", "code", "method"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5)
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/pay")
def pay(delay: int = 50, fail: int = 2, response: Response = None):
    start = time.time()
    try:
        time.sleep(delay / 1000) # delay en ms convertido a segundos
        if random.randint(1, 100) <= fail:
            response.status_code = 500
            return {"status": "payment_error"}
        return {"status": "payment_ok"}
    finally:
        duration = time.time() - start
        REQUEST_TIME.labels("/pay", str(response.status_code),"GET").observe(duration)

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
