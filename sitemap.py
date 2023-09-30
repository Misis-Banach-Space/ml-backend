import pandas as pd
import urllib.request
import httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import requests

from usp.tree import sitemap_tree_for_homepage

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

log = logging.getLogger(__name__)


def get_sitemap(url):
    log.debug("getting xml")
    response = httpx.get(url=url, headers={"User-Agent": "Mozilla/5.0"}, timeout=100)
    if response.status_code >= 400:
        raise RuntimeError(f"status code is {response.status_code}")

    xml = BeautifulSoup(
        response.content,
        "lxml-xml",
        from_encoding=response.encoding,
    )
    if xml is None:
        raise ValueError("xml is none")

    return xml


def get_sitemap_type(xml):
    sitemapindex = xml.find_all("sitemapindex")
    sitemap = xml.find_all("urlset")

    if sitemapindex:
        return "sitemapindex"
    elif sitemap:
        return "urlset"
    else:
        return "sitemapindex"


def get_child_sitemaps(xml):
    sitemaps = xml.find_all("sitemap")
    log.debug(sitemaps)

    output = []

    for sitemap in sitemaps:
        output.append(sitemap.findNext("loc").text)
    return output


def sitemap_to_dataframe(xml, name=None, data=None, verbose=False):
    if xml:
        df = pd.DataFrame(columns=["loc", "sitemap_name"])
        urls = xml.find_all("url")
        for url in urls:
            if xml.find("loc"):
                loc = url.findNext("loc").text
                parsed_uri = urlparse(loc)
                domain = "{uri.netloc}".format(uri=parsed_uri)
            else:
                loc = ""
                domain = ""

            if name:
                sitemap_name = name
            else:
                sitemap_name = ""

            row = {
                "domain": domain,
                "loc": loc,
                "sitemap_name": sitemap_name,
            }

            if verbose:
                print(row)

            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            # df = df.append(row, ignore_index=True)
        return df
    return


def get_all_urls(url):
    log.info("starting")
    xml = get_sitemap(url)
    sitemap_type = get_sitemap_type(xml)
    log.debug(f"sitemap_type {sitemap_type}")

    if sitemap_type == "sitemapindex":
        sitemaps = get_child_sitemaps(xml)
    else:
        sitemaps = [url]

    df = pd.DataFrame(columns=["loc", "sitemap_name"])

    for sitemap in sitemaps:
        sitemap_xml = get_sitemap(sitemap)
        df_sitemap = sitemap_to_dataframe(sitemap_xml, name=sitemap)

        df = pd.concat([df, df_sitemap], ignore_index=True)

    return df


def wordpress_xml(url):
    response = httpx.get(url=url, headers={"User-Agent": "Mozilla/5.0"}, timeout=100)
    xml = BeautifulSoup(
        response.content,
        "html.parser",
        from_encoding=response.encoding,
    )
    log.debug(xml.text)
    parentBlock = xml.find_all("div")
    log.debug(parentBlock)
    df = pd.DataFrame(columns=["loc", "sitemap_name"])
    for block in parentBlock:
        childePage = requests.get(block.text)
        childeSoup = BeautifulSoup(childePage.text, "html.parser")
        childeBlock = childeSoup.find_all("a")
        log.debug(childeBlock.text)


if __name__ == "__main__":
    url = "https://tophotels.ru"
    tree = sitemap_tree_for_homepage(url)
    for page in tree.all_pages():
        print(page.url)
    # print(tree)
