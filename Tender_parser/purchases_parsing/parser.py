import pandas as pd
import requests
# import config
from plotly.graph_objects import Figure

import fz223_db.creation
from purchases_parsing import logger
from purchases_parsing import parsing_contracts_list_44fz
from purchases_parsing import parsing_contracts_list_223fz

from tender_db import data_base_creation, data_base_selections, mnn_selections, nkmi_selections
from fz223_db import creation as ffz223_creation
from fz223_db import selection as ffz223_selection

from medtechproducts_db import db_selections as product_selections
from pdf_generator.MyPdf import MyPdf, create_pie_fig
from pdf_generator.fig import create_volume_by_month_bar_fig

month_arr = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]


def codewords_list(search_text: str) -> list:
    code_words = search_text.split(";")
    for i in range(len(code_words)):
        code_words[i] = code_words[i].strip()
    return code_words


def parsing_by_code_words(code_word: str, year_start: int, year_finish: int):
    logger.log_write(code_word)
    curr_parsing_year = year_start
    while curr_parsing_year <= year_finish:
        for i in range(len(month_arr)):
            if i < (len(month_arr) - 1):
                parsing_contracts_list_44fz.put_list_info_to_db(
                    parsing_contracts_list_44fz.get_url_from_request_parameters(
                        code_word, "01." + month_arr[i] + "." + str(curr_parsing_year),
                                   "01." + month_arr[i + 1] + "." + str(curr_parsing_year)))
                parsing_contracts_list_223fz.put_list_info_to_db(
                    parsing_contracts_list_223fz.get_url_from_request_parameters(
                        code_word, "01." + month_arr[i] + "." + str(curr_parsing_year),
                                   "01." + month_arr[i + 1] + "." + str(curr_parsing_year)))
            if i == len(month_arr) - 1:
                parsing_contracts_list_44fz.put_list_info_to_db(
                    parsing_contracts_list_44fz.get_url_from_request_parameters(
                        code_word, "01." + month_arr[i] + "." + str(curr_parsing_year),
                                   "01." + month_arr[0] + "." + str(curr_parsing_year + 1)))
                parsing_contracts_list_223fz.put_list_info_to_db(
                    parsing_contracts_list_223fz.get_url_from_request_parameters(
                        code_word, "01." + month_arr[i] + "." + str(curr_parsing_year),
                                   "01." + month_arr[0] + "." + str(curr_parsing_year + 1)))
        curr_parsing_year += 1


def parsing_by_ktru(ktru: str, year_start: int, year_finish: int):
    logger.log_write(ktru)
    curr_parsing_year = year_start
    while curr_parsing_year <= year_finish:
        for i in range(len(month_arr)):
            url = ''
            if i < (len(month_arr) - 1):
                url = f"https://zakupki.gov.ru/epz/contract/search/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&fz44=on&contractCurrencyID=-1&budgetLevelsIdNameHidden=%7B%7D&contractDateFrom=01." + \
                      month_arr[i] + f".{str(curr_parsing_year)}&contractDateTo=01." + month_arr[
                          i + 1] + f".{str(curr_parsing_year)}&ktruCodeNameList=" + ktru + "&sortBy=UPDATE_DATE&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false"
            if i == len(month_arr) - 1:
                url = f"https://zakupki.gov.ru/epz/contract/search/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&fz44=on&contractCurrencyID=-1&budgetLevelsIdNameHidden=%7B%7D&contractDateFrom=01." + \
                      month_arr[i] + f".{str(curr_parsing_year)}&contractDateTo=01." + month_arr[
                          0] + f".{str(curr_parsing_year + 1)}&ktruCodeNameList=" + ktru + "&sortBy=UPDATE_DATE&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false"
            logger.log_write(url)
            parsing_contracts_list_44fz.put_list_info_to_db(url)

        curr_parsing_year += 1


class PlotData:
    def __init__(self, fig: Figure, title='', description=''):
        self.__fig = fig
        self.__title = title
        self.__description = description
        # self.__toc = toc

    def get_fig(self) -> Figure:
        return self.__fig

    def get_title(self) -> str:
        return self.__title

    def get_description(self) -> str:
        return self.__description

    # def get_toc(self):
    #     return self.__toc


class PlotsDataStorage:
    def __init__(self):
        self.__data: list = []
        self.__main_part_length: int = 0

    def add_data(self, data: PlotData):
        if type(data) == PlotData:
            self.__data.append(data)
            return True
        else:
            return False

    def add_data(self, fig: Figure, title: str = '', description: str = '') -> bool:
        self.__data.append(PlotData(fig, title, description))
        return True

    def length(self) -> int:
        return len(self.__data)

    def __getitem__(self, i: int):  # real signature unknown; restored from __doc__
        if len(self.__data) > i:
            return self.__data[i]
        else:
            return None

    def get_all_titles(self) -> list:
        titles = []
        for data in self.__data:
            titles.append(data.get_title())
        return titles

    def main_part_stated(self):
        self.__main_part_length = len(self.__data)

    def main_part_lenght(self) -> int:
        return self.__main_part_length


class PlotDataStorageFiller:
    def __init__(self, storage: PlotsDataStorage):
        self.__storage = storage

    def fill_main_diograms_data_to_storage(self, code_words: list, year_start: int, year_finish: int):
        df_pie = data_base_selections.db_product_price_country_df(code_words, year_start, year_finish)

        if df_pie.empty:
            return

        self.__storage.add_data(create_pie_fig(df_pie, year_start=year_start, year_finish=year_finish))

        df_bar_country = data_base_selections.db_product_price_by_country_by_month(code_words,
                                                                                   year_start=year_start,
                                                                                   year_finish=year_finish)
        if not df_bar_country.empty:
            fig = create_volume_by_month_bar_fig(df_bar_country, legend_inside=False)
            self.__storage.add_data(fig, title="Объем закупок РФ/Импорт")

        self.__storage.main_part_stated()

    def fill_ktru_data_to_storage(self, code_words: list, year_start: int, year_finish: int):
        ktru_list = product_selections.db_ktru_nums_by_code_words(code_words)

        for ktru in ktru_list:
            df_ktru = data_base_selections.db_product_price_by_country_by_month(ktru_code=ktru,
                                                                                year_start=year_start,
                                                                                year_finish=year_finish)
            if not df_ktru.empty:
                self.__storage.add_data(create_volume_by_month_bar_fig(df_ktru, legend_inside=False),
                                 title=f"Объем закупок РФ/Импорт для КТРУ номер {ktru}",
                                 description="Описание: " + product_selections.db_ktru_title_by_num(ktru) + ",  Сумма: " + str(df_ktru['value'].sum()) + " Рублей")

    def fill_customers_data_to_storage(self, code_words: list, year_start: int, year_finish: int):
        file = open("gov_customers.txt", "r")
        gov_customers = file.read().strip().split("\n")
        for customer in gov_customers:
            df_customer = data_base_selections.db_product_price_by_country_by_month(code_words,
                                                                                    customer_inn=customer,
                                                                                    year_start=year_start,
                                                                                    year_finish=year_finish)
            if not df_customer.empty:
                self.__storage.add_data(create_volume_by_month_bar_fig(df_customer, legend_inside=False),
                                       title=f"Объем закупок РФ/Импорт для "
                                             f"{data_base_selections.db_get_customer_short_name_by_inn(customer)}",
                                       description="Описание: " + f"ИНН - {customer}" + ",  Сумма: " + str(df_customer['value'].sum()) + " Рублей")

        file.close()

    def fill_regions_data_to_storage(self, code_words: list, year_start: int, year_finish: int):
        regions_codes_names_df = data_base_selections.db_get_regions()
        for k, region_num in enumerate(regions_codes_names_df["code"].to_list()):
            df_region = data_base_selections.db_product_price_by_country_by_month(code_words,
                                                                                  region_code=region_num,
                                                                                  year_start=year_start,
                                                                                  year_finish=year_finish)
            if not df_region.empty:
                fig = create_volume_by_month_bar_fig(df_region, legend_inside=False)
                self.__storage.add_data(fig,
                                       title=f"Объем закупок РФ/Импорт для {regions_codes_names_df['name'].to_list()[k]}",
                                       description= "Сумма: " + str(df_region['value'].sum()) + " Рублей")

    def fill_mnn_data_to_storage(self, code_words: list, year_start: int, year_finish: int):
        mnn_list, mnn_names = mnn_selections.db_mnn_codes_by_code_words(code_words)

        i = 0
        for mnn in mnn_list:
            df_mnn = data_base_selections.db_product_price_by_country_by_month(mnnExternalCode=mnn,
                                                                                year_start=year_start,
                                                                                year_finish=year_finish)
            if not df_mnn.empty:
                self.__storage.add_data(create_volume_by_month_bar_fig(df_mnn, legend_inside=False),
                                 title=f"Объем закупок РФ/Импорт для МНН: {mnn_names[i]}",
                                 description="Внешний код МНН: " + mnn + ",  Сумма: " + str(df_mnn['value'].sum()) + " Рублей")
            i += 1


def fill_data_storage(storage: PlotsDataStorage,
                      code_words: list,
                      year_start: int,
                      year_finish: int,
                      ktru_plots: int,
                      customers_plots: int,
                      regions_plots: int,
                      mnn_plots: int):

    filler = PlotDataStorageFiller(storage)

    # Основная часть
    filler.fill_main_diograms_data_to_storage(code_words, year_start, year_finish)

    if ktru_plots != 0:
        filler.fill_ktru_data_to_storage(code_words, year_start, year_finish)

    if customers_plots != 0:
        filler.fill_customers_data_to_storage(code_words, year_start, year_finish)

    if regions_plots != 0:
        filler.fill_regions_data_to_storage(code_words, year_start, year_finish)

    if mnn_plots != 0:
        filler.fill_mnn_data_to_storage(code_words, year_start, year_finish)


def create_pdf(chat_id: str, code_words: list, year_start: int, year_finish: int, ktru_plots: int, customers_plots: int,
               regions_plots: int, mnn_plots: int):
    storage = PlotsDataStorage()
    fill_data_storage(storage, code_words, year_start, year_finish, ktru_plots,
                      customers_plots, regions_plots, mnn_plots)

    pdf = MyPdf(toc=True, toc_titles=["Общие данные"] + storage.get_all_titles()[storage.main_part_lenght():])
    pdf.set_title_page('pdf_generator/title.jpg', f'Данные по закупкам с кодовыми словами {", ".join(map(str, code_words))}')

    pdf.set_font("DejaVu", '', 12)
    pdf.set_x(0)
    pdf.multi_cell(pdf.epw, pdf.font_size,
                   "Набор диаграмм сформирован автоматически и может содержать неточные данные", border=0, align="C")
    pdf.set_x(0)

    # заполняем основную часть
    pdf.add_toc_entry("Общие данные")
    for i in range(storage.main_part_lenght()):
        pdf.add_image_from_fig(storage[i].get_fig(),
                               title=storage[i].get_title(),
                               description=storage[i].get_description())

    for i in range(storage.main_part_lenght(), storage.length()):
        pdf.add_page(orientation='L')
        pdf.add_image_from_fig(storage[i].get_fig(),
                               title=storage[i].get_title(),
                               description=storage[i].get_description())
        pdf.add_toc_entry(storage[i].get_title())

    pdf.add_page()
    pdf.set_font("DejaVu", '', 12)
    pdf.set_x(0)
    pdf.multi_cell(pdf.epw, pdf.font_size,
                   "Данные используемые в отчете получены из информационной системы ЕИС в сфере закупок. "
                   "Отчет сформирован на основании публичных контрактов по 44-ФЗ.", border=0, align="C")
    pdf.set_x(0)
    pdf.output(name=f'{chat_id}.pdf')
    return f'{chat_id}.pdf'


def create_xlsx(chat_id: str, code_words: str, year_start: int, year_finish: int):
    writer = pd.ExcelWriter(f"./{chat_id}.xlsx", engine='xlsxwriter')

    df_44fz = data_base_selections.db_gel_all_info_dataframe(codewords_list(code_words), year_start, year_finish)
    df_44fz.to_excel(writer, sheet_name="44-ФЗ")

    df223fz = ffz223_selection.db_gel_all_info_dataframe(codewords_list(code_words), year_start, year_finish)
    df223fz.to_excel(writer, sheet_name="223-ФЗ")

    writer.close()
    return f"{chat_id}.xlsx"


def parse_all(chat_id: str, code_words: str, year_start: int, year_finish: int, ktru_plots: int, customers_plots: int,
              regions_plots: int, mnn_plots: int, parse_data: int):

    # nkmi_list = []
    # for code_word in codewords_list(code_words):
    #     if code_word.replace(' ', '').lower().find("нкми(") >= 0:
    #         nkmi = code_word.lower().replace(' ', '').replace(")", '').replace("нкми(", "")
    #         nkmi_list.append(nkmi.strip())
    #         ktru_list = product_selections.db_ktru_list_by_nkmi(nkmi)
    #         for ktru in ktru_list:
    #             parsing_by_ktru(ktru, year_start, year_finish)

    # df_nkmi = pd.DataFrame()
    # for nkmi in nkmi_list:
    #     df_nkmi = nkmi_selections.db_get_nkmi_data(nkmi, year_start, year_finish)
    #
    # if len(nkmi_list) > 0:
    #     df_nkmi.to_excel(f"{chat_id}.xlsx")
    #     text = "Данные собраны и обработанны, что бы получить результат дайте команду  /result"
    #     requests.post(f"https://api.telegram.org/bot{config.TOKEN}/sendMessage?chat_id={chat_id}&text={text}")
    #     return

    text = f"Процесс c кодовыми словами \n{code_words}\nзапущен"

    if parse_data == 1:
        for code_word in codewords_list(code_words):
            if len(code_word) > 3:
                parsing_by_code_words(code_word, year_start, year_finish)

        ktru_list = product_selections.db_ktru_nums_by_code_words(codewords_list(code_words))

        for ktru in ktru_list:
            parsing_by_ktru(ktru, year_start, year_finish)

    pdf_name = create_pdf(chat_id, codewords_list(code_words), year_start, year_finish, ktru_plots, customers_plots, regions_plots, mnn_plots)
    excel_name = create_xlsx(chat_id, code_words, year_start, year_finish)
    text = "Данные собраны и обработанны, что бы получить результат дайте команду  /result"
    return pdf_name, excel_name


if __name__ == "__main__":
    data_base_creation.db_initialise()
    fz223_db.creation.db_initialise()
    parse_all("корова", "корова", 2022, 2024)
    # parsing_by_ktru("22.21.29.120-00000015", 2019, 2021)
    pass
