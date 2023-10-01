import pika
import json
from model.schema import UrlRequest, UrlResponse
from service.parse_analysis import get_stats_report
from service.parse_metadata import get_metadata
from ml.nlp import get_theme
from utils.logging import get_logger
from ml.prediction_kakos import make_predict

log = get_logger(__name__)

category_theme = {
    "Бизнес": ["Бухгалтерские услуги", "Грузоперевозки и транспортные услуги", "Создание и продвижение сайтов", "Юридические услуи"],
    "Бытовая техника": ["Бытовая техника"],
    "Еда и напитки": ["Доставка воды", "Доставка готовых блюд и продуктов", "Кулинария"],
    "Животные": ["Домашние животные"],
    "Канцелярские товары": ["Канцелярские товары"],
    "Красота и здоровье": ["Здоровое питание", "Медицина", "Парфюмерия и косметика"],
    "Недвижимость": ["Покупка и аренда"],
    "Образование": ["Дополнительное образование и курсы", "Школа и вуз"],
    "Одежда, обувь и аксессуары": ["Одежда и обувь"],
    "Отдых и путешествия": ["Билеты", "Зарубежный туризм", "Прокат автомобилей", "Российский туризм"],
    "Подарки и цветы": ["Подарки и цветы"],
    "Работа": ["Работа"],
    "Развлечения и досуг": ["Игры", "Кино", "Книги", "Музыка", "Охота", "Рестораны", "Рыбалка", "Танцы", "Театры", "Телевидение"],
    "Сельскохозяйственное оборудование и техника": ["Сельскохозяйственное оборудование и техника"],
    "Семья и дети": ["Беременность и роды", "Свадьба", "Товары для детей"],
    "Спорт": ["Спорт"],
    "Строительство, обустройство и ремонт": ["Дизайн интерьера", "Мебель", "Ремонт", "Товары для дома"],
    "Телеком": ["Доступ в интернет и мобильня связь"],
    "Транспорт": ["Авто", "Мото"],
    "Финансы": ["Банки и кредиты", "Инвестиции", "Форекс"],
    "Электроника": ["Компьютерная техника", "Принтеры и МФУ", "Смартфоны и гаджеты", "Фото, видео и аудиотехника"]
}

def get_category_by_theme(theme):
    for category, themes in category_theme.items():
        if theme in themes:
            return category
    return "" 

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
    category = get_category_by_theme(theme)
    channel.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=UrlResponse(
            id=u.id, url=u.url, stats=stats, category=category, theme=theme
        ).json(),
    )
    channel.basic_ack(delivery_tag=method.delivery_tag)
