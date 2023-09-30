# Херня с селениумом, не завелось нормально

import asyncio
import bs4
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options


async def get_metadata(url: str):
    try:
        options = Options()
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(10)
        driver.get(url)

        page_source = driver.page_source
        soup = bs4.BeautifulSoup(page_source, "html.parser")

        metadata: list[bs4.element.Tag] = soup.find_all("meta")

        def check_meta_tag(meta_tag: dict[str, str], key: str):
            data = ""
            if key in meta_tag.keys():
                if (
                    "description" in meta_tag[key]
                    or "title" in meta_tag[key]
                    or "name" in meta_tag[key]
                ):
                    data += f"{meta_tag['content']}"
            return data

        data = set()
        for meta in metadata:
            attrs = meta.attrs
            cur = ""
            for key in ["name", "property"]:
                cur += check_meta_tag(attrs, key)
                if cur != "":
                    data.add(cur)

        print(" ".join([t for t in data]))

        driver.quit()
    except TimeoutException as e:
        raise e


async def main():
    websites = pd.read_csv("list.csv", sep=",", encoding="utf-8")
    for website in websites["web"]:
        try:
            await get_metadata(website)
        except TimeoutException:
            print(f"{website} timeout!")


if __name__ == "__main__":
    asyncio.run(main())
