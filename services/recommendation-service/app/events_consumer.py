"""
Asynchronous event consumption via RabbitMQ.

Subscribes to the `itinerary.created` events published by itinerary-service
(see that service's app/events.py) instead of polling it. This is the
event-driven half of the architecture: itinerary-service doesn't know or
care that recommendation-service exists, and recommendation-service
doesn't have to make a synchronous call every time it wants to know "did
anything change recently?".

What we do with the event here is intentionally simple — log it and drop a
note in an in-process "recently active" set that a future feature (e.g.
"fresh picks since your last trip") could read. The point of this module
is to demonstrate the pattern correctly (durable queue, topic exchange,
graceful reconnect) rather than to justify a complex consumer.

Runs in a background thread started from the app's lifespan handler so it
never blocks request handling, and never crashes the service if the
broker is down at startup — it just retries quietly.
"""

import json
import logging
import threading
import time

import pika

from app.config import settings

logger = logging.getLogger("recommendation-service.events")

# In-process record of the most recent itinerary-created events seen,
# newest first. Not persisted — purely a demonstration hook / could seed a
# "trending" boost in the recommendation engine later.
recent_itinerary_events: list[dict] = []
_MAX_RECENT = 50

_stop_event = threading.Event()


def _handle_message(channel, method, properties, body):
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        logger.warning("Discarding malformed event payload")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    logger.info("Received event: %s", payload)
    recent_itinerary_events.insert(0, payload)
    del recent_itinerary_events[_MAX_RECENT:]
    channel.basic_ack(delivery_tag=method.delivery_tag)


def _consume_loop():
    while not _stop_event.is_set():
        try:
            connection = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
            channel = connection.channel()
            channel.exchange_declare(exchange=settings.events_exchange, exchange_type="topic", durable=True)
            channel.queue_declare(queue=settings.events_queue, durable=True)
            channel.queue_bind(
                exchange=settings.events_exchange, queue=settings.events_queue, routing_key="itinerary.created"
            )
            channel.basic_qos(prefetch_count=10)
            channel.basic_consume(queue=settings.events_queue, on_message_callback=_handle_message)

            logger.info("Listening for itinerary.created events on '%s'", settings.events_queue)
            while not _stop_event.is_set():
                connection.process_data_events(time_limit=1)
            connection.close()
            return
        except Exception as exc:  # noqa: BLE001 — broker downtime must never crash the service
            logger.warning("RabbitMQ consumer unavailable (%s) — retrying in 5s", exc)
            time.sleep(5)


def start_consumer_in_background() -> None:
    if not settings.consume_events:
        return
    thread = threading.Thread(target=_consume_loop, name="rabbitmq-consumer", daemon=True)
    thread.start()


def stop_consumer() -> None:
    _stop_event.set()
