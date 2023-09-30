import pika
import json
import time
from model.schema import UrlRequest, UrlResponse
from service.parse_analysis import get_stats_report
from service.parse_metadata import get_metadata
from utils.logging import get_logger

# from handler.parse_metadata import parse_url

log = get_logger(__name__)


def process_url_request(channel, method, props, body: bytes):
    body = json.loads(body)
    log.debug(body)
    u = UrlRequest(**body)

    # here comes ML
    time.sleep(5)
    stats = get_stats_report(u.url)
    metadata = get_metadata(u.url)

    channel.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=UrlResponse(
            id=u.id, url=u.url, stats=stats, category="затычка", theme="ml"
        ).model_dump_json(),
    )
    channel.basic_ack(delivery_tag=method.delivery_tag)
