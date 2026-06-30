"""RabbitMQ publisher for web-triggered background tasks."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

import pika


EXCHANGE = "tasks"
QUEUE = "tasks_q"
ROUTING_KEY = "tasks"


def _open_channel():
    """Open a RabbitMQ connection and declare durable AMQP entities."""
    rabbitmq_url = os.environ["RABBITMQ_URL"]
    params = pika.URLParameters(rabbitmq_url)
    conn = pika.BlockingConnection(params)
    channel = conn.channel()

    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="direct",
        durable=True
    )
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(
        exchange=EXCHANGE,
        queue=QUEUE,
        routing_key=ROUTING_KEY
    )

    return conn, channel


def publish_task(
    kind: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None
) -> None:
    """Publish a persistent JSON task message to RabbitMQ."""
    body = json.dumps(
        {
            "kind": kind,
            "ts": datetime.now(timezone.utc).isoformat(),
            "payload": payload or {},
        },
        separators=(",", ":")
    ).encode("utf-8")

    conn, channel = _open_channel()
    try:
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers=headers or {},
                content_type="application/json",
            ),
            mandatory=False,
        )
    finally:
        conn.close()
