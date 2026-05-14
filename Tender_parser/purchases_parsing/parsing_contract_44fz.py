from bs4 import BeautifulSoup

from tender_db import data_base_fillings as fillDB
from tender_db import data_base_creation as createDB
from purchases_parsing import internet_request

html = """your HTML"""


def _parse_int_or_default(value: str, default: int = 0) -> int:
    if value is None:
        return default
    text = str(value).strip().replace(",", ".")
    if not text:
        return default
    try:
        return int(float(text))
    except Exception:
        return default


def get_contract_id(soup: BeautifulSoup) -> str:
    # номер
    reestrNum = str(soup)[str(soup).find("reestrNumber=") + 13:]
    reestrNum = reestrNum[:reestrNum.find('"')]

    return reestrNum


# Возвращает customer_regnum
def put_customer_to_db(customer: BeautifulSoup) -> int:
    regNum = customer.find("regNum".lower())

    if regNum is not None:
        try:
            regNum = int(regNum.text)
        except:
            regNum = 0
    else:
        regNum = 0

    fullName = customer.find("fullName".lower())
    if fullName is not None:
        fullName = fullName.text
    else:
        fullName = ""

    shortName = customer.find("shortName".lower())
    if shortName is not None:
        shortName = shortName.text
    else:
        shortName = ""

    inn = customer.find("inn".lower())
    if inn is not None:
        inn = inn.text
    else:
        inn = ""

    kpp = customer.find("kpp")
    if kpp is not None:
        kpp = kpp.text
    else:
        kpp = ""

    legalForm = customer.find("legalForm".lower())
    code = 0
    singularName = "UNRESOLVED"
    if legalForm is not None:
        code = legalForm.find("code".lower())
        if code is not None:
            try:
                code = int(code.text)
            except:
                code = 0
        else:
            code = 0
        singularName = legalForm.find("singularName".lower())
        if singularName is not None:
            singularName = singularName.text
        else:
            singularName = ""

    OKPO = customer.find("OKPO".lower())
    if OKPO is not None:
        OKPO = OKPO.text
    else:
        OKPO = ""

    customerCode = customer.find("customerCode".lower())
    if customerCode is not None:
        customerCode = customerCode.text
    else:
        customerCode = ""

    fillDB.db_add_customer((regNum, fullName, shortName, inn, kpp, OKPO, customerCode, code), regNum,
                           (code, singularName), code)

    return regNum


def put_product_to_db(contract_id: str, product: BeautifulSoup, contract_price: int, products_num: int):
    KTRU = product.find("KTRU".lower())
    KTRUcode = ""
    KTRUname = ""
    if KTRU is not None:
        KTRUcode = KTRU.find("code".lower())
        if KTRUcode is not None:
            KTRUcode = KTRUcode.text
        else:
            KTRUcode = "UNRESOLVED"
        KTRUname = KTRU.find("name".lower())
        if KTRUname is not None:
            KTRUname = KTRUname.text
        else:
            KTRUname = "UNRESOLVED"
    else:
        KTRU = product.find("okpd2".lower())
        if KTRU is not None:
            KTRUcode = KTRU.find("code".lower())
            if KTRUcode is not None:
                KTRUcode = KTRUcode.text
            else:
                KTRUcode = "UNRESOLVED"
            KTRUname = KTRU.find("name".lower())
            if KTRUname is not None:
                KTRUname = KTRUname.text
            else:
                KTRUname = "UNRESOLVED"

    product = BeautifulSoup(str(product).replace(str(product.find("KTRU".lower())), ""), "lxml")
    product = BeautifulSoup(str(product).replace(str(product.find("okpd2".lower())), ""), "lxml")
    name = product.find("name".lower()).text

    prodtype = product.find("type".lower())
    if prodtype is not None:
        prodtype = prodtype.text
    else:
        prodtype = "UNRESOLVED"

    OKEIcode = 0
    OKEInationalCode = "НЕТ"
    OKEIfullName = "Отсутствует"
    OKEIs = product.find_all("OKEI".lower())
    for OKEI in OKEIs:
        if OKEI.find("fullName".lower()) is not None:
            OKEIcode = OKEI.find("code".lower()).text
            if OKEI.find("nationalCode".lower()) is not None:
                OKEInationalCode = OKEI.find("nationalCode".lower()).text
            OKEIfullName = OKEI.find("fullName".lower()).text

    quantity = 1
    quantity_tag = product.find("quantity".lower())
    if quantity_tag:
        quantity = _parse_int_or_default(quantity_tag.text, default=1)
        if quantity == 0:
            quantity = 1

    priceRUR = 0
    price_rur_tag = product.find("priceRUR".lower())
    price_tag = product.find("price".lower())
    if price_rur_tag:
        priceRUR = _parse_int_or_default(price_rur_tag.text, default=0)
    elif price_tag:
        priceRUR = _parse_int_or_default(price_tag.text, default=0)

    sumRUR = priceRUR
    sum_rur_tag = product.find("sumRUR".lower())
    sum_tag = product.find("sum".lower())
    if sum_rur_tag:
        sumRUR = _parse_int_or_default(sum_rur_tag.text, default=priceRUR)
    elif sum_tag:
        sumRUR = _parse_int_or_default(sum_tag.text, default=priceRUR)

    # Для контрактов где только один товар бывают случаи когда не указано количество и сумма товаров.
    # Суммой является сумма контракта, тогда надо посчитать это самостоятельно из суммы контракта
    if quantity == 1 and products_num == 1 and sumRUR == priceRUR:
        if contract_price != 0:
            sumRUR = contract_price
        if priceRUR != 0:
            quantity = sumRUR / priceRUR

    originCountry = product
    countryCode = originCountry.find("countryCode".lower())
    if countryCode is not None:
        try:
            countryCode = int(countryCode.text)
        except:
            countryCode = 0
    else:
        countryCode = 0
    countryFullName = originCountry.find("countryFullName".lower())
    if countryFullName is not None:
        countryFullName = countryFullName.text
    else:
        countryFullName = "Не указана"

    medicalProductCode = 0
    medicalProductName = ""
    if product.find("medicalProductInfo".lower()):
        medicalProductInfo = product.find("medicalProductInfo".lower())
        medicalProductCode = medicalProductInfo.find("medicalProductCode".lower())
        if medicalProductCode is not None:
            try:
                medicalProductCode = int(medicalProductCode.text)
            except:
                medicalProductCode = 0
        else:
            medicalProductCode = 0
        medicalProductName = medicalProductInfo.find("medicalProductName".lower())
        if medicalProductName is not None:
            medicalProductName = medicalProductName.text
        else:
            medicalProductName = ""

    mnnExternalCode = ''
    mnnDrugCode = ''
    mnnName = ''
    if product.find("mnnsinfo".lower()):
        mnnExternalCode = product.find("mnnexternalcode".lower())
        mnnDrugCode = product.find("mnndrugcode".lower())
        mnnName = product.find("mnnname".lower())

        if mnnExternalCode is not None:
            mnnExternalCode = mnnExternalCode.text
        else:
            mnnExternalCode = ''

        if mnnDrugCode is not None:
            mnnDrugCode = mnnDrugCode.text
        else:
            mnnDrugCode = ''

        if mnnName is not None:
            mnnName = mnnName.text.upper()
        else:
            mnnName = ''

    fillDB.db_add_product((name.lower(), contract_id, KTRUcode, KTRUname.lower(), prodtype, OKEIcode, quantity,
                           priceRUR, sumRUR, countryCode, medicalProductCode,
                           medicalProductName.lower(), mnnExternalCode),
                          (countryCode, countryFullName),
                          (OKEIcode, OKEInationalCode, OKEIfullName),
                          (mnnExternalCode, mnnDrugCode, mnnName),
                          countryCode, OKEIcode, mnnExternalCode)

    return


def put_contract_information_to_db(reestrNum: str) -> int:
    url = "https://zakupki.gov.ru/epz/contract/printForm/viewXml.html?contractReestrNumber=" + reestrNum
    soup = internet_request.get_response_and_soup_text(url)

    publishYear = 0
    publishMonth = 0
    publishDay = 0
    publishDate = soup.find("publishDate".lower())
    if publishDate is not None:
        publishDate = publishDate.text
    else:
        publishDate = ""
    publishDate = publishDate.split("T")[0].split("-")
    if len(publishDate) == 3:
        publishYear = int(publishDate[0])
        publishMonth = int(publishDate[1])
        publishDay = int(publishDate[2])

    customer = soup.find("customer".lower())
    if customer is not None:
        customerRegNum = put_customer_to_db(customer)
    else:
        customerRegNum = 0

    protocolDate = soup.find("protocolDate".lower())
    if protocolDate is not None:
        protocolDate = protocolDate.text
    else:
        protocolDate = ""

    documentBase = soup.find("documentBase".lower())
    if documentBase is not None:
        documentBase = documentBase.text
    else:
        documentBase = ""

    priceInfo = soup.find("priceInfo".lower())
    # price = int(priceInfo.find("price".lower()).text) Если окажется, что с priceRUR есть проблема
    priceRUR = 0
    if priceInfo is not None:
        try:
            priceRUR = int(priceInfo.find("priceRUR".lower()).text.split(".")[0])
        except:
            priceRUR = 0

    link = "https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=" + reestrNum
    suppliersInfo = str(soup.find("suppliersInfo".lower()))

    fillDB.db_add_contract(reestrNum, (
    reestrNum, publishDay, publishMonth, publishYear, customerRegNum, protocolDate, documentBase,
    priceRUR, link, suppliersInfo))

    products = soup.find("products".lower())
    if products is not None:
        for product in products.find_all("product"):
            put_product_to_db(reestrNum, product, priceRUR, len(products))

    return 0


if __name__ == "__main__":
    createDB.db_initialise()

    reestrid = "1780204820022000081"
    print(put_contract_information_to_db(reestrid))
