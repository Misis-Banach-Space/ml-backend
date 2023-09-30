import requests
import re
import ast
from bs4 import BeautifulSoup
from utils.logging import get_logger


log = get_logger(__name__)


def get_soup(domain):
    try:
        url = f"https://be1.ru/stat/{domain}"
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        return soup
    except Exception as e:
        log.error(str(e))
        return None


def get_yandex_requests_data(soup, url: str):
    try:
        data_table = []
        table = soup.find("table", attrs={"class": "table main"})
        table_body = table.find("tbody")

        rows = table_body.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            data_table.append([ele for ele in cols if ele])  # Get rid of empty values

        for i in range(len(data_table)):
            data_1 = [data_table[i][1], url + data_table[i][3], data_table[i][4]]
            data_table[i] = data_1
        return data_table
    except Exception as e:
        log.error(str(e))
        return {}


def clear_str(my_str):
    return my_str.replace("\n", "").replace("\t", "").replace("\r", "")


def get_stats(soup):
    try:
        matches = re.findall(
            r"google\.visualization\.arrayToDataTable\((.*?)\)", clear_str(str(soup))
        )
        dict_list = []
        for i, match in enumerate(matches):
            if match != "data":
                try:
                    match = match.replace("//", "")
                    match = re.sub(r"/\*.*?\*/", "", match)
                    list_data = ast.literal_eval(match)
                    dict_data = {item[0]: item[1:] for item in list_data}
                    dict_list.append(dict_data)
                except:
                    domain_names = re.findall(r'"([\w.-]+\.[\w.-]+)"', match)
        return dict_list, domain_names
    except Exception as e:
        log.error(str(e))
        return ()


def get_stats_report(url: str):
    domain = re.findall(r"([\w.-]+\.[\w.-]+)", url)[0]
    soup = get_soup(domain)
    if not soup:
        return {"title": "", "description": ""}
    try:
        data_table = get_yandex_requests_data(soup, url)
        dict_list, domain_names = get_stats(soup)

        data = {
            "title": soup.find(id="set_title").text,
            "description": soup.find(id="set_description").text,
            "vozrast": soup.find(id="set_vozrast").text,
            "page_size": soup.find(id="set_page_size").text,
            "page_load_time": soup.find(id="set_page_load_time").text,
            "ip": soup.find(id="set_site_ip").text,
            "yandex_iks": soup.find(id="set_iks").text.replace("\n", ""),
            "competitiors": domain_names,
            "yandex_request": data_table,
        }

        for el in dict_list:
            if "Year" in el:
                if el["Year"][0] == "Количество запросов":
                    el["Title"] = el.pop("Year")
                    data["requests"] = el
                elif el["Year"][0] == "Количество заходов":
                    el["Title"] = el.pop("Year")
                    data["visits_by_month"] = el
            elif "Country" in el:
                el["Title"] = el.pop("Country")
                data["visits_by_country"] = el

        return data
    except Exception as e:
        log.error(str(e))
        return {
            "title": soup.find(id="set_title").text,
            "description": soup.find(id="set_description").text,
        }
