import requests
import re
from datetime import datetime
import pickle
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from random import randint
import time
import dateutil.parser

PICKLE_FILENAME = "data_list.pkl"


def to_pickle(mylist):
    with open(PICKLE_FILENAME, "wb") as f:
        pickle.dump(mylist, f)


def from_pickle():
    with open(PICKLE_FILENAME, "rb") as f:
        mynewlist = pickle.load(f)
    return mynewlist


def get_html(url):
    res = requests.get(url).text
    # with open(f"htmls/{time.time()}.html", "w", encoding="utf8") as f:
    # f.write(res)
    return res

def get_html_carousell(url):
### add these to my get request headers
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-SG,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
}
    
    res = requests.get(url, headers=headers).text
    return res


def gsearch(query, results=None):
    num = ""
    if results:
        num = f"&num={results}"
    return get_html(
        f"https://www.google.com/search?q={query}+carousell+site%3Ahttps%3A%2F%2Fwww.carousell.sg%2Fp%2F"
        + num
    )


def get_valid_urls(html):
    return re.findall(r"https://www.carousell.sg/p/[^&\s]+-\d{7,}", html)


def format_date(date_str):
    return datetime.strptime(date_str, "%Y/%m/%d").date()


def get_name_date_price(html):
    try:
        if "This listing is no longer available" in html:
            print("Listing is no longer available")
            return
        photo_url = re.findall(
            r"https://media.karousell.com/media/photos/products/[0-9]{4}/[0-9]{1,}/[0-9]{1,}",
            html,
        )
        date = "/".join(photo_url[0].split("/")[6:9])
        # Date will be parsed in JS
        # date = format_date(date_str)
        price_str = re.findall(r"S\$<!-- -->.+?</p><div>", html)
        price = price_str[0].strip("S$<!-- -->").rstrip("</p><div>").replace(",", "")
        name_str = re.findall(r'"name":".+?","offers"', html)
        name = name_str[0][8:-10]
        sold_str = re.findall(r'<button[^>]*><div[^>]*>Sold<\/div><\/button>', html)
        reserved_str = re.findall(r'<button[^>]*><div[^>]*>Reserve<\/div><\/button>', html)
        status = "S" if sold_str else ("R" if reserved_str else "L")
    except IndexError:
        return
    else:
        return {
            "name": name, 
            "date": date, 
            "price": price,
            "status": status,
        }


def iso_to_date(iso_str):
    parsed = dateutil.parser.isoparse(iso_str)
    return str(parsed.strftime("%Y/%m/%d"))

def gen_plot(data_list):
    data_list.sort(key=lambda x: format_date(x[1]))
    x_values = [format_date(x[1]) for x in data_list]
    y_values = [float(x[2]) for x in data_list]
    ax = plt.gca()
    formatter = mdates.DateFormatter("%Y/%m/%d")
    ax.xaxis.set_major_formatter(formatter)
    locator = mdates.DayLocator()
    ax.xaxis.set_major_locator(locator)
    plt.xticks(x_values)
    plt.title(data_list[0][0])
    plt.xlabel("Date")
    plt.ylabel("Price (S$)")
    plt.plot(x_values, y_values)
    plt.gcf().autofmt_xdate()
    plt.show()


def get_car_data(car_urls, keywords=[], delay=False):
    # print(car_urls)
    data_list = []
    for url in car_urls:
        strict_fail = any([kw.lower() not in url for kw in keywords])
        if strict_fail:
            print(f"Skipped {url} [STRICT MODE]")
            continue
        html = get_html(url)
        if delay:
            time.sleep(randint(2, 8))
        data = get_name_date_price(html)
        if not data:
            print(f"Skipped {url} [INVALID URL]")
            continue
        data += tuple([url])
        data_list.append(data)
        # print("{}\n{}\n${}\n{}\n".format(*data))
    return data_list


def main(query="er2se", strict=True, results=None, delay=False):
    # with open("gsearch.html", "r", encoding="utf8") as f:
    #     html = f.read()
    # with open("car.html", "r", encoding="utf8") as f:
    #     res = f.read()
    html = gsearch(query, results)
    car_urls = get_valid_urls(html)
    keywords = []
    if strict:
        keywords = query.split()
    data_list = get_car_data(car_urls, keywords, delay)
    # to_pickle(data_list)
    # gen_plot(data_list)
    return data_list


def debug():
    data_list = from_pickle()
    gen_plot(data_list)


if __name__ == "__main__":
    # main()
    debug()
