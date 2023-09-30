import pika
import json
from model.schema import UrlRequest, UrlResponse
from service.parse_analysis import get_stats_report
from service.parse_metadata import get_metadata
from ml.nlp import get_theme
from utils.logging import get_logger

from ml.prediction_kakos import make_predict

log = get_logger(__name__)


def process_url_request(channel, method, props, body: bytes):
    body = json.loads(body)
    log.debug(body)
    u = UrlRequest(**body)

    stats = get_stats_report(u.url)
    metadata = get_metadata(u.url)
    print(f"metadata: {metadata}")
    theme = get_theme(metadata[1])
    if not theme:
        theme = make_predict(metadata[1])

    channel.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=UrlResponse(
            id=u.id, url=u.url, stats=stats, category="затычка", theme=theme
        ).json(),
    )
    channel.basic_ack(delivery_tag=method.delivery_tag)
