import asyncio
import re
import pymorphy3
from service.rabbit import RabbitMQ
from utils.logging import get_logger

morph = pymorphy3.MorphAnalyzer()
log = get_logger(__name__)


def Lemmatization(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    words = text.split()
    return [morph.parse(w)[0].normal_form for w in words]


def Tokenizer(txt, min_token_size=5):
    txt = txt.replace(",", " ")
    txt = re.sub(r"(?<=[а-я])(?=[А-Я])", " ", txt)
    txt = txt.lower()
    txt = re.sub(r"[^\w\s]", "", txt)
    all_tokens = re.findall(r"\b\w+\b", txt)
    all_tokens = Lemmatization(" ".join(all_tokens))
    return [token for token in all_tokens if len(token) >= min_token_size]


def main():
    rabbit_mq = RabbitMQ(get_logger("RabbitMQ"), host="localhost")
    rabbit_mq.declare_queue("url_queue")

    from handler.process import process_url_request

    log.info("listening for requests")
    rabbit_mq.start_consuming("url_queue", process_url_request)


if __name__ == "__main__":
    asyncio.run(main())
