"""Temporary worker entry point for Module 6 Docker Compose verification."""

import time


def main():
    """Keep the worker container running until RabbitMQ logic is added."""
    print("Worker service started. Waiting for Step 4 RabbitMQ implementation.")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
