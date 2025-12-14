import os
import json
import time
from dotenv import load_dotenv
import pika
import redis

# OpenTelemetry imports
from opentelemetry import trace, propagate
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# -------------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------------
load_dotenv()

# -------------------------------------------------------------------
# OpenTelemetry setup
# -------------------------------------------------------------------
resource = Resource.create({
    "service.name": "worker-service",
    "deployment.environment": os.getenv("OTEL_DEPLOYMENT_ENVIRONMENT", "unknown"),
})

trace.set_tracer_provider(
    TracerProvider(resource=resource)
)

otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    insecure=True,
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)

# -------------------------------------------------------------------
# RabbitMQ + Valkey config
# -------------------------------------------------------------------
RABBITMQ_URL = os.getenv("RABBITMQ_BROKER_URL")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME")

valkey = redis.from_url(os.getenv("VALKEY_URL"), decode_responses=True)
PROCESSED_COUNT_KEY = os.getenv("VALKEY_PROCESSED_COUNT_KEY")


# -------------------------------------------------------------------
# Message processing
# -------------------------------------------------------------------
def process_message(ch, method, properties, body):
    # Extract trace context from headers
    context = propagate.extract(properties.headers or {})

    with tracer.start_as_current_span(
        "worker.process_task",
        context=context,
    ):
        data = json.loads(body)
        print(f"[Worker] Processing task: {data}")

        # Simulate work
        time.sleep(1)

        # Update metric
        valkey.incr(PROCESSED_COUNT_KEY)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def run_worker():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=process_message,
    )

    print("[Worker] Started and waiting for tasks...")
    channel.start_consuming()


if __name__ == "__main__":
    run_worker()
