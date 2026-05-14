from purchases_parsing import internet_request
from purchases_parsing import parsing_contract_44fz as parse
from purchases_parsing import zakupki_url_interfaces
from purchases_parsing import logger

from tender_db.data_base_checkings import db_contract_is_in_base


# формирует урл из структуры поиска (надо будет делать, когда будет глобальный список запросов)
def get_url_from_request_parameters(req_text: str, start_date: str, finish_date: str) -> str:
    req_text = req_text.split(" ")
    url = "https://zakupki.gov.ru/epz/contract/search/results.html?searchString="
    for t in req_text:
        url += t + "+"
    url += "&morphology=on&search-filter=Дате+размещения" \
           "&fz44=on" \
           "&contractStageList_0=on" \
           "&contractStageList_1=on" \
           "&contractStageList_2=on" \
           "&contractStageList_3=on" \
           "&contractStageList=0%2C1%2C2%2C3" \
           "&contractCurrencyID=-1" \
           "&budgetLevelsIdNameHidden={}" \
           "&publishDateFrom=" + start_date + \
           "&publishDateTo=" + finish_date + \
           "&sortBy=UPDATE_DATE" \
           "&pageNumber=1" \
           "&sortDirection=false" \
           "&recordsPerPage=_50" \
           "&showLotsInfoHidden=false"
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
            contracts = soup.find_all("div", class_="search-registry-entry-block box-shadow-search-input")
            if not contracts:
                page_flag = 1
            i = 0
            for contract in contracts:
                order_id = parse.get_contract_id(contract)
                # ord  = order_class.Order(main_order_part.get("тип"), main_order_part.get("номер"))
                if i == 0:
                    if first_on_page == order_id:
                        logger.log_write("выходим по номеру " + str(first_on_page))
                        return
                    first_on_page = order_id
                    i = 1
                if not db_contract_is_in_base(order_id):
                    try:
                        parse.put_contract_information_to_db(order_id)
                    except EOFError:
                        print("ERROR", EOFError)


            page_counter += 1
            url = zakupki_url_interfaces.make_page_url_by_num(url, page_counter)
        else:
            break

        if page_flag == 1:
            break

    return

