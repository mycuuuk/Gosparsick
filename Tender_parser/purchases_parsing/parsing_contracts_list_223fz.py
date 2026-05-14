from purchases_parsing import internet_request
from purchases_parsing import parsing_contract_223fz as parse
from purchases_parsing import zakupki_url_interfaces
from purchases_parsing import logger

from fz223_db.chekings import db_contract_is_in_base


# формирует урл из структуры поиска (надо будет делать, когда будет глобальный список запросов)
def get_url_from_request_parameters(req_text: str, start_date: str, finish_date: str) -> str:
    req_text = req_text.split(" ")
    url = "https://zakupki.gov.ru/epz/contractfz223/search/results.html?searchString="
    for t in req_text:
        url += t + "+"
    url += "&morphology=on&search-filter=Дате+размещения" \
           "&statuses_0=on" \
           "&statuses_1=on" \
           "&statuses=0%2C1" \
           "&currencyId=-1" \
           "&contract223DateFrom="  + start_date + \
           "&contract223DateTo=" + finish_date +  \
           "&sortBy=BY_UPDATE_DATE" \
           "&sortDirection=false" \
           "&recordsPerPage=_50" \
           "&showLotsInfoHidden=false" \
           "&pageNumber=1"

    logger.log_write(url)
    return url


def put_list_info_to_db(url: str):
    page_counter = 1

    page_flag = 0
    first_on_page = ""
    # находим отдельные заказы
    while(True):
        soup = internet_request.get_response_and_soup_text(url)
        if soup:
            # Ищем все ссылки, которые содержат нужный pfid
            links = soup.find_all('a', href=True)

            # Фильтруем ссылки по нужному паттерну
            filtered_links = [link['href'] for link in links if
                              'https://zakupki.gov.ru/223/contract/public/contract/print-form/show.html?pfid=' in link[
                                  'href']]
            if not filtered_links:
                page_flag = 1
            i = 0
            # Проходим по всем ссылкам
            for link in filtered_links:
                # Парсим HTML с помощью BeautifulSoup
                if i == 0:
                    if first_on_page == link:
                        logger.log_write("выходим по номеру " + str(first_on_page))
                        return
                    first_on_page = link
                    i = 1
                if not db_contract_is_in_base(link):
                    try:
                        parse.parse_and_put_to_db(link)
                    except EOFError:
                        print("ERROR", EOFError)

            page_counter += 1
            url = zakupki_url_interfaces.make_page_url_by_num(url, page_counter)
        else:
            break

        if page_flag == 1:
            break

    return
