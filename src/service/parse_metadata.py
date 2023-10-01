import asyncio
import httpx
import bs4
import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote

import csv
import json
from urllib.parse import urljoin

from translate import Translator
import urllib.parse
import re
from transliterate import translit
from autocorrect import Speller

# from utils.logging import logging

# log = logging.basicConfig(__name__)

from deep_translator import GoogleTranslator
import urllib.parse
import re
from transliterate import translit
from autocorrect import Speller



def get_words_from_url(url):
    url = re.sub(r'\d+', '', url)
    url_parse = urllib.parse.urlparse(url)
    domain = url_parse.netloc.split('.')
    words = url_parse.path.split('/')
    words.extend(domain)
    return words

def split_word(word):
    symbols = ['-', '/', '%', ' ', '.', '_']
    for symbol in symbols:
        words = word.split(symbol)
        if len(words) > 1:
            return words
    return [word]


def transliterate_words(words):
    transliterated_words = set()
    spell = Speller(lang='ru')
    for word in words:
        parts = split_word(word)
        for part in parts:
            if part != '':
                transliteration = translit(part, 'ru')
                if re.match("^[а-яА-Я]+$", transliteration):
                    transliterated_words.add(spell(transliteration))
    return transliterated_words





def parse_url(base_url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
    }
    with httpx.Client(headers=headers) as client:
        try:
            data = ""
            words = get_words_from_url(base_url)
            transliterated_words = transliterate_words(words)
            data += ', '.join([words for words in transliterated_words])
            query_args = parse_qs(urlparse(base_url).query)
            if len(query_args):
                for param, values in query_args.items():
                    if (
                        "text" in param
                        or "tag" in param
                        or "display" in param
                        or "search" in param
                    ):
                        data += f"{', '.join([unquote(value) for value in values])}"

            resp = client.get(base_url, timeout=5)
            print(base_url)
            if resp.status_code >= 400:
                return (
                    data.replace("\n", " ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .strip()
                    .encode("utf-8")
                    .decode("utf-8")
                )
            else:
                soup = bs4.BeautifulSoup(resp.content, features="html.parser")
                title = soup.find("title")
                if title:
                    data += f"{title.get_text()},"

                meta_tags = set()
                meta = soup.find("meta")
                if meta:
                    for head in meta_tags:
                        cur = (
                            head.get_text()
                            .replace("\n", " ")
                            .replace("\r", "")
                            .replace("  ", "")
                            .strip()
                        )
                        if cur:
                            meta.add(cur)
                    data += ",".join([tag for tag in meta])

                description = soup.find("meta", {"name": "description"})
                if description:
                    data += ",".join(
                        [
                            s
                            for s in set(
                                description.text.replace("\n", " ")
                                .replace("\r", "")
                                .replace("  ", "")
                                .strip()
                                .splitlines()
                            )
                        ]
                    )
                h1 = set()
                for head in soup.find_all("h1"):
                    cur = (
                        head.text.replace("\n", " ")
                        .replace("\r", "")
                        .replace("  ", "")
                        .strip()
                    )
                    if cur:
                        h1.add(cur)
                data += ",".join([tag for tag in h1])
                h2 = set()
                for head in soup.find_all("h2"):
                    cur = (
                        head.text.replace("\n", " ")
                        .replace("\r", "")
                        .replace("  ", "")
                        .strip()
                    )
                    if cur:
                        h2.add(cur)
                data += ",".join([tag for tag in h2])
                h3 = set()
                for head in soup.find_all("h3"):
                    cur = (
                        head.text.replace("\n", " ")
                        .replace("\r", "")
                        .replace("  ", "")
                        .strip()
                    )
                    if cur:
                        h3.add(cur)
                data += ",".join([tag for tag in h3])
                tags = ['div', 'p', 'span']
                result = ""
                for tag in tags:
                    elements = soup.find_all(tag)
                    for element in elements:
                        if len(element.text) > 300:
                            result += element.text + " "
                            result = re.sub(r'\s+', ' ', result)
                    if len(result) > 1000:
                        break
                result = result[:500]
                result = re.sub(r'[^\w\s.,;:!?-]', '', result)
                data += result
                return (
                    data.replace("\n", " ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .strip()
                    .encode("utf-8")
                    .decode("utf-8")
                )
        except Exception as e:
            return (
                str(e)
                .replace("\n", " ")
                .replace("\r", "")
                .replace("\t", "")
                .strip()
                .encode("utf-8")
                .decode("utf-8")
            )



def get_metadata(url: str):
    return [url, parse_url(url)]


async def main():
    websites = pd.read_csv("list2.csv", sep=",", encoding="utf-8")

    data_list: list[dict] = [[url, parse_url(url)] for url in websites["link"]]
    df = pd.DataFrame(columns=["link", "metadata"], data=data_list)
    websites = websites.merge(df, on="link", how="left")
    websites.to_csv("metadata.csv", sep=";", index=False, encoding="utf-8")
    print(websites.head())
    # url = 'https://www.dns-shop.ru/catalog/17a8df6816404e77/lazernye-mfu/'
    # print(parse_url(url))


if __name__ == "__main__":
    asyncio.run(main())
