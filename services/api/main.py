import os
import json
from fastapi import FastAPI
from dotenv import load_dotenv
import pika
import redis

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagate import inject


# -------------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------------
load_dotenv()

# -------------------------------------------------------------------
# OpenTelemetry setup
# -------------------------------------------------------------------
resource = Resource.create({
    "service.name": os.getenv("APP_NAME", "fastapi-service"),
    "deployment.environment": os.getenv("OTEL_DEPLOYMENT_ENVIRONMENT", "unknown"),
})

trace.set_tracer_provider(
    TracerProvider(resource=resource)
)

otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    insecure=True,  # common for local/dev
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# -------------------------------------------------------------------
# FastAPI app
# -------------------------------------------------------------------
app = FastAPI(title=os.getenv("APP_NAME"))

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# -------------------------------------------------------------------
# RabbitMQ + Valkey config
# -------------------------------------------------------------------
RABBITMQ_URL = os.getenv("RABBITMQ_BROKER_URL")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME")

valkey = redis.from_url(os.getenv("VALKEY_URL"), decode_responses=True)
PROCESSED_COUNT_KEY = os.getenv("VALKEY_PROCESSED_COUNT_KEY")


def get_rabbitmq_channel():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    return connection, channel


# -------------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------------

@app.post("/task")
def push_task(payload: dict):
    connection, channel = get_rabbitmq_channel()

    headers = {}
    inject(headers)  # Inject trace context

    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=2,
            headers=headers,
        ),
    )

    connection.close()
    return {"status": "task queued"}


@app.get("/stats")
def stats():
    connection, channel = get_rabbitmq_channel()
    queue_state = channel.queue_declare(queue=QUEUE_NAME, passive=True)
    queue_length = queue_state.method.message_count
    connection.close()

    return {
        "valkey_keys_count": valkey.dbsize(),
        "queue_backlog_length": queue_length,
        "worker_processed_count": int(valkey.get(PROCESSED_COUNT_KEY) or 0),
    }
