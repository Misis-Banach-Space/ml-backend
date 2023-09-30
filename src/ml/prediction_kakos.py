import pymorphy3
import re

import sklearn

from joblib import load

morph = pymorphy3.MorphAnalyzer()


def Lemmatization(text):
  text = text.lower()
  text = re.sub(r'[^\w\s]', '', text)
  words = text.split()
  return [morph.parse(w)[0].normal_form for w in words]



def Tokenizer(txt, min_token_size = 5):
    txt = txt.replace(',', ' ')
    txt = re.sub(r'(?<=[а-я])(?=[А-Я])', ' ', txt)
    txt = txt.lower()
    txt = re.sub(r'[^\w\s]', '', txt)
    all_tokens = re.findall(r'\b\w+\b', txt)
    all_tokens = Lemmatization(' '.join(all_tokens))
    return [token for token in all_tokens if len(token) >= min_token_size]



categories = ['Авто', 'Банки и кредиты', 'Беременность и роды', 'Билеты',
                  'Бухгалтерские услуги', 'Бытовая техника',
                  'Грузоперевозки и транспортные услуги', 'Дизайн интерьера',
                  'Домашние животные', 'Дополнительное образование и курсы',
                  'Доставка воды', 'Доставка готовых блюд и продуктов',
                  'Доступ в интернет и мобильная связь', 'Зарубежный туризм',
                  'Здоровое питание', 'Игры', 'Инвестиции', 'Канцелярские товары',
                  'Кино', 'Книги', 'Компьютерная техника', 'Кулинария', 'Мебель',
                  'Медицина', 'Мото', 'Музыка', 'Одежда и обувь', 'Охота',
                  'Парфюмерия и косметика', 'Подарки и цветы', 'Покупка и аренда',
                  'Принтеры и МФУ', 'Прокат автомобилей', 'Работа', 'Ремонт',
                  'Рестораны', 'Российский туризм', 'Рыбалка', 'Свадьба',
                  'Сельскохозяйственное оборудование и техника',
                  'Смартфоны и гаджеты', 'Создание и продвижение сайтов', 'Спорт',
                  'Танцы', 'Театры', 'Телевидение', 'Товары для детей',
                  'Товары для дома', 'Форекс', 'Фото, видео и аудиотехника',
                  'Школа и вуз', 'Юридические услуги']


#from joblib import load
kakos = load('kakos_pipeline.joblib')


def make_predict(texts ):
  prediction = kakos.predict(texts)
  prediction = [categories[i] for i in prediction]
  return prediction
 

if __name__ == "__main__":
  texts = ['Сельскохозяйственный трактор на продажу', 'Курсы по английскому языку', 'Турнир по футболу']
  print(make_predict(texts)) # вывод: ['Школа и вуз', 'Школа и вуз', 'Школа и вуз']
  