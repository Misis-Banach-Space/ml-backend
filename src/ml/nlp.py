import pymorphy3
import re
import pandas as pd
from collections import Counter
import numpy as np

topics_and_keywords = {
    "Бухгалтерские услуги": 0,
    "Грузоперевозки и транспортные услуги": 0,
    "Создание и продвижение сайтов": 0,
    "Юридические услуи": 0,
    "Бытовая техника": 0,
    "Доставка воды": 0,
    "Доставка готовых блюд и продуктов": 0,
    "Кулинария": 0,
    "Домашние животные": 0,
    "Канцелярские товары": 0,
    "Здоровое питание": 0,
    "Медицина": 0,
    "Парфюмерия и косметика": 0,
    "Покупка и аренда": 0,
    "Дополнительное образование и курсы": 0,
    "Школа и вуз": 0,
    "Одежда и обувь": 0,
    "Билеты": 0,
    "Зарубежный туризм": 0,
    "Прокат автомобилей": 0,
    "Российский туризм": 0,
    "Подарки и цветы": 0,
    "Работа": 0,
    "Игры": 0,
    "Кино": 0,
    "Книги": 0,
    "Музыка": 0,
    "Охота": 0,
    "Рестораны": 0,
    "Рыбалка": 0,
    "Танцы": 0,
    "Театры": 0,
    "Телевидение": 0,
    "Сельскохозяйственное оборудование и техника": 0,
    "Беременность и роды": 0,
    "Свадьба": 0,
    "Товары для детей": 0,
    "Спорт": 0,
    "Дизайн интерьера": 0,
    "Мебель": 0,
    "Ремонт": 0,
    "Товары для дома": 0,
    "Доступ в интернет и мобильня связь": 0,
    "Авто": 0,
    "Мото": 0,
    "Банки и кредиты": 0,
    "Инвестиции": 0,
    "Форекс": 0,
    "Компьютерная техника": 0,
    "Принтеры и МФУ": 0,
    "Смартфоны и гаджеты": 0,
    "Фото, видео и аудиотехника": 0,
}


def Lemmatization(text):
    morph = pymorphy3.MorphAnalyzer()
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    words = text.split()
    return [morph.parse(w)[0].normal_form for w in words]


def freq(x):
    freq = {}
    for i in x:
        freq[i] = x.count(i)
    return freq


def get_theme(text: str) -> str:
    cur = Lemmatization(text)
    # print(cur)
    df = pd.read_csv("./keywords.csv", sep=",")

    cnt = 0
    for key in topics_and_keywords.keys():
        topics_and_keywords[key] = df["a"][cnt]
        cnt += 1

    pred_topic = []
    for i in cur:
        for j in topics_and_keywords.keys():
            if i in topics_and_keywords[j].split(" "):
                pred_topic.append(j)

    if len(pred_topic) != 0:
        res = {
            k: v
            for k, v in sorted(
                freq(pred_topic).items(), key=lambda item: item[1], reverse=True
            )
        }
        print(res)
        print(f"Предварительная тема: {list(res.keys())[0]}")
        return list(res.keys())[0]
    else:
        return "unmatched"


if __name__ == "__main__":
    # df = pd.read_csv('metadata2.csv', sep=';')
    # ds_theme = [get_theme(str(meta)) for meta in df['metadata']]
    # print(ds_theme)
    # df['theme'] = ds_theme
    # df.to_csv('meta_all.csv')
    text = 'шоп, ру, магазин, мф, Аде, каталог, мфу, днс, арфе, лазерные'
    get_theme(text)