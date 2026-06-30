"""RabbitMQ consumer for Module 6 background worker tasks."""

# pylint: disable=import-error

from __future__ import annotations

import json
import os
import time
from typing import Any

import pika

from etl import incremental_scraper, load_data, query_data


EXCHANGE = "tasks"
QUEUE = "tasks_q"
ROUTING_KEY = "tasks"
RETRY_SECONDS = 5


def _open_channel():
    """Open RabbitMQ connection and declare durable task routing."""
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
    channel.basic_qos(prefetch_count=1)

    return conn, channel


def handle_scrape_new_data(payload: dict[str, Any]) -> None:
    """Scrape new records and load applicant data idempotently."""
    del payload
    scrape_summary = incremental_scraper.scrape_new_records()
    inserted_count, skipped_count = load_data.load_data()
    print(
        "scrape_new_data completed: "
        f"{scrape_summary}; "
        f"{inserted_count} inserted, {skipped_count} skipped"
    )


def handle_recompute_analytics(payload: dict[str, Any]) -> None:
    """Recompute analytics by executing the dashboard queries."""
    del payload
    results = query_data.get_analysis_results()
    print(
        "recompute_analytics completed: "
        f"{len(results)} result sets generated"
    )


def _handle_task(message: dict[str, Any]) -> None:
    """Route a task message to the correct background action."""
    task_kind = message.get("kind")
    payload = message.get("payload", {})

    if task_kind == "scrape_new_data":
        handle_scrape_new_data(payload)
        return

    if task_kind == "recompute_analytics":
        handle_recompute_analytics(payload)
        return

    raise ValueError(f"Unsupported task kind: {task_kind}")


# pylint: disable=broad-exception-caught
def _on_message(channel, method, properties, body) -> None:
    """Process one RabbitMQ message and acknowledge it after success."""
    del properties

    try:
        message = json.loads(body.decode("utf-8"))
        _handle_task(message)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as error:
        print(f"Task failed: {error}")
        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False
        )


def main() -> None:
    """Start the RabbitMQ worker loop."""
    while True:
        try:
            _conn, channel = _open_channel()
            print("Worker is waiting for RabbitMQ tasks.")
            channel.basic_consume(
                queue=QUEUE,
                on_message_callback=_on_message
            )
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as error:
            print(f"RabbitMQ connection failed: {error}")
            time.sleep(RETRY_SECONDS)


if __name__ == "__main__":
    main()
