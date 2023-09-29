import json
import time
import pika
from pydantic import BaseModel, Json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", port=5672)
)

channel = connection.channel()

channel.queue_declare(queue="rpc_queue")


class TestModel(BaseModel):
    msg: str


def on_request(ch, method, props, body: bytes):
    decoded_body = json.loads(body)
    print(decoded_body)

    model = TestModel(**decoded_body)
    print(model.model_dump_json())
    time.sleep(3)
    model.msg = "changed"
    print(model.model_dump_json())

    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=model.model_dump_json(),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="rpc_queue", on_message_callback=on_request)


print(" [x] Awaiting RPC requests")
channel.start_consuming()
