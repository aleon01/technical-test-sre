from fastapi import FastAPI, Response
import random
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import PlainTextResponse
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.semconv.attributes import http_attributes
from opentelemetry.trace import Status, StatusCode
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] trace_id=%(otelTraceID)s span_id=%(otelSpanID)s %(message)s"
)
LoggingInstrumentor().instrument()

app = FastAPI()

provider = TracerProvider()

otlp_exporter = OTLPSpanExporter(
    endpoint = "otel-collector-opentelemetry-collector.tec-test-ns.svc.cluster.local:4317",
    insecure = True
)

processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("controller.app.trace")

# Métricas Prometheus
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total de requests HTTP",
    ["route", "code", "method"]
)

REQUEST_ERRORS = Counter(
    "http_request_errors_total",
    "Total de errores HTTP",
    ["route", "method"]
)
REQUEST_TIME = Histogram(
    "http_request_duration_seconds",
    "Duración de las solicitudes HTTP",
    ["route", "code", "method"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5)
)

@app.get("/health")
def health():
    logger = logging.getLogger(__name__)
    with tracer.start_as_current_span("controller.health") as span:
        span.set_attribute(http_attributes.HTTP_REQUEST_METHOD, "GET")
        span.set_attribute(http_attributes.HTTP_ROUTE, "/health")
        span.set_attribute(http_attributes.HTTP_RESPONSE_STATUS_CODE, "200")
        logger.info("Processing health")
        return {"status": "ok"}


@app.get("/pay")
def pay(delay: int = 50, fail: int = 2, response: Response = None):
    logger = logging.getLogger(__name__)
    with tracer.start_as_current_span("controller.pay") as span:
        span.set_attribute(http_attributes.HTTP_REQUEST_METHOD, "GET")
        span.set_attribute(http_attributes.HTTP_ROUTE, "/pay")
    
        logger.info(f"Processing pay with delay={delay}ms")
        start = time.time()
        try:
            time.sleep(delay / 1000) # delay en ms convertido a segundos
            if random.randint(1, 100) <= fail:

                response.status_code = 500
                span.set_attribute(http_attributes.HTTP_RESPONSE_STATUS_CODE, "500")
                span.set_status(Status(StatusCode.ERROR))
                logger.error("Pay failed")
                REQUEST_COUNT.labels("/pay", "500", "GET").inc()
                REQUEST_ERRORS.labels("/pay", "GET").inc()
                return {"status": "payment_error"}
            
            span.set_attribute(http_attributes.HTTP_RESPONSE_STATUS_CODE, "200")
            span.set_status(Status(StatusCode.OK))
            logger.info("Pay successful")
            REQUEST_COUNT.labels("/pay", "200", "GET").inc()
            return {"status": "payment_ok"}
        finally:
            duration = time.time() - start
            REQUEST_TIME.labels("/pay", str(response.status_code),"GET").observe(duration)

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
