from bs4 import BeautifulSoup
import re

from fz223_db import fillings as fillDB
from purchases_parsing import internet_request


# Функция для извлечения числовых значений (удаление единиц измерения)
def extract_number(text):
    # Убираем все символы, кроме цифр и точки
    text = text.replace(',', '')  # Убираем запятую, если она присутствует
    text = text.replace(' ', '')  # Убираем запятую, если она присутствует
    match = re.search(r'\d+(\.\d+)?', text)  # Ищем число с возможной десятичной точкой
    return float(match.group()) if match else None


def parse_and_put_to_db(link: str):
    # Парсим HTML с помощью BeautifulSoup
    soup = internet_request.get_response_and_soup_text(link)

    try:
    # Извлекаем информацию о заказчике и ИНН
        organization = soup.find(string=re.compile("Сокращенное наименование организации:")).find_next('td').get_text(
            strip=True)
    except:
        organization = ""

    try:
        organization_full = soup.find(string=re.compile("Полное наименование организации:")).find_next('td').get_text(
            strip=True)
    except:
        organization_full = ""

    try:
        contract_name = soup.find(string=re.compile("Предмет договора:")).find_next('td').get_text(
            strip=True)
    except:
        contract_name = ""

    date = soup.find(string=re.compile("Дата начала исполнения договора:"))
    if not date:
        date = soup.find(string=re.compile("Дата заключения договора:"))
        if not date:
            date = soup.find(string=re.compile("Дата"))

    if date:
        date = date.find_next('td').get_text(strip=True)
    else:
        date = ""

    try:
        inn = soup.find(string=re.compile("ИНН/КПП:")).find_next('td').get_text(strip=True).split('/')[0].strip()
    except:
        inn = ""

    try:
        contract_price_text = soup.find(string=re.compile("Цена договора:")).find_next('td').get_text(strip=True).split(' ')[0].strip()
        contract_price = extract_number(contract_price_text)
    except:
        contract_price = 0

    # Извлекаем информацию о товарах
    tables = soup.find_all('table', class_='item-information')
    table = None
    for tab in tables:
        if tab.text.find("Наименование товаров, работ, услуг") >= 0:
            table = tab
            break

    if table:
        rows = table.find_all('tr')[1:]  # Пропускаем заголовок
    else:
        rows = []

    for row in rows:
        columns = row.find_all('td')
        if len(columns) > 6:
            # Извлекаем наименование товара
            product_name = columns[1].get_text(strip=True)

            okpd2 = columns[2].get_text(strip=True)

            # Извлекаем количество (только число)
            quantity_text = columns[3].get_text(strip=True)
            quantity = extract_number(quantity_text)
            if quantity == 0:
                quantity = 1

            # Извлекаем цену (только число)
            unit_price_text = columns[4].get_text(strip=True)
            unit_price = extract_number(unit_price_text)

            # Страна происхождения
            country = columns[5].get_text(strip=True)

            # Добавляем данные о товаре и заказчике в список
            fillDB.db_add_contract({
                'organization': organization,
                'organizationFull': organization_full,
                'organizationINN': inn,
                'productName': product_name.lower(),
                'okpd2': okpd2,
                'quantity': quantity,
                'unitPrice': unit_price,
                'country': country,
                'startDate': date,
                'link': link,
                'contractPrice': contract_price,
                'contractName': contract_name.lower(),
            })
