import logging
import json
import time
import pika
from typing import Callable


class RabbitMQ:
    instance = None

    def __init__(self, log: logging.Logger, host: str = "localhost", port: int = 5672):
        self.log = log
        self.host = host
        self.port = port

        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port)
        )
        self.channel = self.conn.channel()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if cls.instance is None:
            cls.instance = super(RabbitMQ, cls).__new__(cls)
        return cls.instance

    def declare_queue(self, queue: str):
        return self.channel.queue_declare(queue)

    def start_consuming(self, queue: str, handler: Callable, prefetch_count: int = 1):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.channel.basic_consume(queue=queue, on_message_callback=handler)
        return self.channel.start_consuming()
