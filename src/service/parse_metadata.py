import asyncio
import httpx
import bs4
import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote


async def parse_url(base_url: str):
    headers = {"user-agent": "Chrome/117.0.0.0"}
    async with httpx.AsyncClient(headers=headers) as client:
        try:
            data = ""
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

            resp = await client.get(base_url, timeout=5)
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

                meta = set()
                for head in soup.find_all("meta"):
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
                    # print(description.get_text())
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


def get_title(url: str):
    headers = {"user-agent": "Chrome/117.0.0.0"}
    with httpx.Client(headers=headers) as client:
        resp = client.get(url, timeout=5)
        soup = bs4.BeautifulSoup(resp.content, features="html.parser")
        print(soup.find_all("body"))


async def get_metadata(url: str):
    return [url, await parse_url(url)]


async def main():
    get_title("https://www.dns-shop.ru/catalog/17a8df6816404e77/lazernye-mfu")
    # websites = pd.read_csv("new_links.csv", sep=";", encoding="utf-8")

    # data_list: list[dict] = await asyncio.gather(
    #     *[get_metadata(url) for url in websites["link"]]
    # )
    # print(data_list[0])
    # df = pd.DataFrame(columns=["link", "metadata"], data=data_list)
    # websites = websites.merge(df, on="link", how="left")
    # print(websites["metadata"].head())
    # websites.to_csv("metadata.csv", sep=";", index=False, encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
