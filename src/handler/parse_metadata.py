import asyncio
import httpx
import bs4
import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote


async def parse_url(base_url: str):
    async with httpx.AsyncClient() as client:
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
                        data += f"{param}: {', '.join([unquote(value) for value in values])},"

            resp = await client.get(base_url, timeout=1)
            if resp.status_code >= 400:
                return data
            else:
                soup = bs4.BeautifulSoup(resp.content, features="html.parser")
                title = soup.find("title")
                if title:
                    data += f",{title.get_text().replace('  ', '').replace('  ', '').strip()}"

                meta = set()
                for head in soup.find_all("meta"):
                    cur = (
                        head.get_text()
                        .replace("\n", "")
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
                                description["content"]
                                .replace("\n", "")
                                .replace("\r", "")
                                .replace("  ", "")
                                .strip()
                                .splitlines()
                            )
                        ]
                    )
                return data.replace("\n", "")
        except Exception:
            return data


async def get_metadata(url: str):
    return [url, await parse_url(url)]


async def main():
    websites = pd.read_csv("new_links.csv", sep=";")

    data_list: list[dict] = await asyncio.gather(
        *[get_metadata(url) for url in websites["link"]]
    )

    df = pd.DataFrame(columns=["link", "metadata"], data=data_list)
    websites = websites.merge(df, on="link", how="left")
    print(websites)
    websites.to_csv("metadata.csv", sep=";", index=False, encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
