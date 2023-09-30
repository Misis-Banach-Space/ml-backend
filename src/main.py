import asyncio
from service.rabbit import RabbitMQ
from utils.logging import get_logger


log = get_logger(__name__)


def main():
    rabbit_mq = RabbitMQ(get_logger("RabbitMQ"), host="localhost")
    rabbit_mq.declare_queue("url_queue")

    from handler.process import process_url_request

    log.info("listening for requests")
    rabbit_mq.start_consuming("url_queue", process_url_request)


if __name__ == "__main__":
    asyncio.run(main())
