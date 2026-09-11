"""
Asynchronous event publishing via RabbitMQ.

When an itinerary is created, this service publishes an `itinerary.created`
event to a topic exchange instead of calling recommendation-service
directly. recommendation-service (or any future subscriber — a
notifications service, an analytics pipeline, etc.) can consume it without
itinerary-service knowing or caring who's listening. That decoupling is
the actual point of choosing async messaging here instead of another
synchronous REST call.

This is deliberately best-effort: if the broker is unreachable, we log a
warning and let the request succeed anyway. An itinerary is still valid
and useful even if nobody hears about it right away — we'd rather degrade
gracefully than fail a user-facing request because of a side-channel.
"""

import json
import logging

import pika

from app.config import settings

logger = logging.getLogger("itinerary-service.events")


def publish_itinerary_created(itinerary: dict) -> None:
    message = {
        "event": "itinerary.created",
        "itinerary_id": itinerary["id"],
        "user_id": itinerary["user_id"],
        "destination_id": itinerary["destination_id"],
        "title": itinerary["title"],
    }

    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
        channel = connection.channel()
        channel.exchange_declare(exchange=settings.events_exchange, exchange_type="topic", durable=True)
        channel.basic_publish(
            exchange=settings.events_exchange,
            routing_key="itinerary.created",
            body=json.dumps(message).encode("utf-8"),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
        connection.close()
        logger.info("Published itinerary.created for itinerary_id=%s", itinerary["id"])
    except Exception as exc:  # noqa: BLE001 — broker downtime must never break the request
        logger.warning("Could not publish itinerary.created event: %s", exc)
