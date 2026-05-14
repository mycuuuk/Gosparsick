import requests
# from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
import datetime
from purchases_parsing import logger

# ch = UserAgent().firefox
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


# Дает обрабатываем html текст лежащий по ссылке
def get_response_and_soup_text(url: str, entry_index=0) -> BeautifulSoup:
    # time.sleep(0.05)
    try:
        r = requests.get(url, headers=headers, timeout=7)
        if r.status_code == 404:
            if entry_index == 50:
                text = "2 часа нет ответа на запрос по ссылке " + url
                print(text)
            print("Иду спать на минуту")
            time.sleep(10)
            entry_index += 1
            return get_response_and_soup_text(url, entry_index)
    except requests.exceptions.HTTPError as error:
        print("Request error", error.response.status_code)
        file = open("log.txt", "a")
        file.write("\n Request error  " + str(error))
        file.write("     " + str(datetime.datetime.now()))
        file.close()
        return None
    except requests.exceptions.Timeout:
        if entry_index == 50:
            text = "2 часа нет ответа на запрос по ссылке " + url
            logger.log_write(text)
        logger.log_write("Иду спать на минуту")
        time.sleep(10)
        entry_index += 1
        return get_response_and_soup_text(url, entry_index)
    except requests.exceptions.RequestException as e:
        if entry_index == 50:
            text = "2 часа нет ответа на запрос по ссылке " + url
            logger.log_write(text)
        logger.log_write("Иду спать на минуту")
        time.sleep(10)
        entry_index += 1
        return get_response_and_soup_text(url, entry_index)
    soup = BeautifulSoup(r.text, "lxml")
    return soup
