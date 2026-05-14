import sqlalchemy
import mysql.connector
import pandas as pd
from tender_db.data_base_common import DBInfo
from sqlalchemy.exc import SQLAlchemyError


# def where_request_part_for_code_words(code_frases: list) -> str:
#     query_text = """ WHERE ("""
#     k = 0
#     for code_frase in code_frases:
#         k += 1
#         code_words_untreated = code_frase.strip().split(" ")
#
#         code_words = []
#         for code_word in code_words_untreated:
#             if len(code_word.strip()) >= 2:
#                 code_words.append(code_word.lower().strip())
#
#         # Формируем параметры запроса (WHERE)
#
#         query_text += """("""
#         for i in range(len(code_words)):
#             if i != 0:
#                 query_text += " AND "
#             query_text += f"""LOWER(Products.KTRUname) LIKE '%{code_words[i]}%'"""
#
#         query_text += """)"""
#
#         query_text += """ OR """
#
#         query_text += """("""
#         for i in range(len(code_words)):
#             if i != 0:
#                 query_text += " AND "
#             query_text += f"""LOWER(Products.name) LIKE '%{code_words[i]}%'"""
#
#         query_text += """)"""
#         if k != len(code_frases):
#             query_text += """ OR """
#
#     query_text += """)"""
#     return query_text
def where_request_part_for_code_words(code_frases: list) -> str:
    query_parts = []

    for code_frase in code_frases:
        code_words = [word.lower().strip() for word in code_frase.strip().split(" ") if len(word.strip()) >= 2]

        conditions = ["LOWER(Products.KTRUname) LIKE '%%{}%%'".format(word) for word in code_words]
        part1 = " AND ".join(conditions)

        conditions = ["LOWER(Products.name) LIKE '%%{}%%'".format(word) for word in code_words]
        part2 = " AND ".join(conditions)

        query_parts.append(f"(({part1}) OR ({part2}))")

    return " WHERE (" + " OR ".join(query_parts) + ")"


def db_product_price_country_df(code_words: list, year_start: int, year_finish: int) -> pd.DataFrame:
    database_url = f"mysql+pymysql://{DBInfo.USER}:{DBInfo.PASSWORD}@{DBInfo.HOST}:{DBInfo.PORT}/{DBInfo.NAME}"
    engine = sqlalchemy.create_engine(database_url)

    try:
        with engine.connect() as dbconnection:
            df = pd.read_sql(f"""SELECT
                                    SUM(Products.sumRUR) as value,
                                    C2.countryFullName as name
                                FROM Products
                                    INNER JOIN Contracts C on Products.contractId = C.id
                                    INNER JOIN Countries C2 on C2.countryCode = Products.countryCode
                                {where_request_part_for_code_words(code_words)}
                                AND C.publishYear <= {year_finish} AND C.publishYear >= {year_start} 
                                GROUP BY C2.countryFullName""", dbconnection)
    except SQLAlchemyError as error:
        print("SQLAlchemy error:", error)
    except Exception as error:
        print("SQL query error in db_product_price_country_df:", error)
    finally:
        return df


def db_product_price_month_year_df(code_words: list, year_start: int, year_finish: int) -> pd.DataFrame:
    database_url = f"mysql+pymysql://{DBInfo.USER}:{DBInfo.PASSWORD}@{DBInfo.HOST}:{DBInfo.PORT}/{DBInfo.NAME}"
    engine = sqlalchemy.create_engine(database_url)

    try:
        with engine.connect() as dbconnection:
            df = pd.read_sql(f"""SELECT
                                    SUM(Products.sumRUR) as value,
                                    C.publishMonth as month,
                                    C.publishYear as year
                                FROM Products
                                INNER JOIN Contracts C on Products.contractId = C.id
                                {where_request_part_for_code_words(code_words)} 
                                AND year <= {year_finish} AND year >= {year_start} 
                                GROUP BY C.publishYear, C.publishMonth
                                ORDER BY C.publishYear, C.publishMonth
                                """, dbconnection)
    except SQLAlchemyError as error:
        print("SQLAlchemy error:", error)
    except Exception as error:
        print("SQL query error in db_product_price_month_year_df:", error)
    finally:
        return df


# если не дан ИНН, то построит для всех, если ktru_code, то для ktru
def db_product_price_by_country_by_month(code_words=None, year_start=0, year_finish=0, customer_inn='', ktru_code='',
                                         region_code='', mnnExternalCode = '') -> pd.DataFrame:
    if code_words is None:
        code_words = []
    dbconnection = mysql.connector.connect(
        host=DBInfo.HOST,
        port=DBInfo.PORT,
        user=DBInfo.USER,
        password=DBInfo.PASSWORD,
        database=DBInfo.NAME
    )
    df = pd.DataFrame()
    resDict_array = []

    if len(customer_inn) > 0:
        if not code_words:
            return pd.DataFrame()
        where = f'{where_request_part_for_code_words(code_words)} AND C3.inn = "{customer_inn}"'
    elif len(ktru_code) > 0:
        where = f'AND KTRUcode = "{ktru_code}"'
    elif len(region_code) > 0:
        where = f'{where_request_part_for_code_words(code_words)} AND substr(C3.inn, 0, 3) = "{region_code}"'
    elif len(mnnExternalCode) > 0:
        where = f'AND mnnExternalCode = "{mnnExternalCode}"'
    else:
        if not code_words:
            return pd.DataFrame()
        where = f'{where_request_part_for_code_words(code_words)}'

    if year_start > 0:
        where += f" AND C.publishYear >= {year_start}"
    if year_finish > 0:
        where += f" AND C.publishYear <= {year_finish} "

    try:
        dbobject = dbconnection.cursor()
        dbobject.execute(f"""SELECT
                                 SUM(Products.sumRUR) as value,
                                 CASE 
                                    WHEN C2.countryFullName LIKE "%%Росс%%"
                                    THEN 'Российская Федерация'
                                    ELSE 'Импорт или не указана'
                                 END as country,
                                 CONCAT(CAST(C.publishMonth AS CHAR), '.', CAST(C.publishYear AS CHAR)) as date,
                                 C.publishMonth as month,
                                 C.publishYear as year
                             FROM Products
                                 INNER JOIN Contracts C on Products.contractId = C.id
                                 INNER JOIN Countries C2 on C2.countryCode = Products.countryCode
                                 INNER JOIN Customers C3 on C.customerRegNum = C3.regNum
                             {where}
                             GROUP BY country, date
                             ORDER BY C.publishYear, C.publishMonth			
        """)
        res_array = dbobject.fetchall()
        for res in res_array:
            resDict_array.append(dict(zip([c[0] for c in dbobject.description], res)))
        df = pd.DataFrame(resDict_array)
    except mysql.connector.Error as error:
        print("MySQL error", error)
        dbconnection = False
    except:
        print("SQL querry error in db_product_price_by_country_by_month")
    finally:
        if (dbconnection):
            dbconnection.close()
        return df


# Сейчас не используется
def db_product_price_by_country_for_ktru(ktru_code: str) -> pd.DataFrame:
    database_url = f"mysql+pymysql://{DBInfo.USER}:{DBInfo.PASSWORD}@{DBInfo.HOST}:{DBInfo.PORT}/{DBInfo.NAME}"
    engine = sqlalchemy.create_engine(database_url)

    try:
        with engine.connect() as dbconnection:
            df = pd.read_sql(f"""SELECT
                                SUM(Products.sumRUR) as value,
                                    C2.countryFullName as name
                                FROM Products
                                    INNER JOIN Contracts C on Products.contractId = C.id
                                    INNER JOIN Countries C2 on C2.countryCode = Products.countryCode
                                WHERE KTRUcode = "{ktru_code}"
                                GROUP BY C2.countryFullName
                                """, dbconnection)
    except SQLAlchemyError as error:
        print("SQLAlchemy error:", error)
    except Exception as error:
        print("SQL query error in db_product_price_by_country_for_ktru:", error)
    finally:
        return df


def db_get_customer_short_name_by_inn(customer_inn: str) -> str:
    name = ''
    database_url = f"mysql+pymysql://{DBInfo.USER}:{DBInfo.PASSWORD}@{DBInfo.HOST}:{DBInfo.PORT}/{DBInfo.NAME}"
    engine = sqlalchemy.create_engine(database_url)

    try:
        with engine.connect() as dbconnection:
            df = pd.read_sql(f"""SELECT
                                    shortName
                                FROM Customers
                                WHERE inn LIKE "%%{customer_inn}%%"
                                    """, dbconnection)
        if not df.empty:
            name = df.to_dict()
            name = name["shortName"][0]
    except SQLAlchemyError as error:
        print("SQLAlchemy error:", error)
    except Exception as error:
        print("SQL query error in db_get_customer_short_name_by_inn:", error)
    finally:
        return df

def db_get_ktru_dataframe(codewords: list, year_start: int, year_finish: int) -> pd.DataFrame:
    database_url = f"mysql+pymysql://{DBInfo.USER}:{DBInfo.PASSWORD}@{DBInfo.HOST}:{DBInfo.PORT}/{DBInfo.NAME}"
    engine = sqlalchemy.create_engine(database_url)

    try:
        with engine.connect() as dbconnection:
            df = pd.read_sql(f""" SELECT
                                KTRUcode as Код,
                                KTRUname as Наименование,
                                SUM(sumRUR) as Сумма,
                                SUM(quantity) as Количество,
                                SUM(ktru_rus_val.value) СуммаРоссийскогоПроизводства,
                                100 * SUM(ktru_rus_val.value) / SUM(sumRUR) as ПроцентРоссийскогоПроизводства
                             FROM Products
                                 INNER JOIN Contracts C on Products.contractId = C.id
                                 LEFT JOIN (SELECT
                                        KTRUcode ktru,
                                        SUM(sumRUR) value
                                    FROM Products
                                    INNER JOIN Contracts C on Products.contractId = C.id
                                    INNER JOIN Countries C2 on C2.countryCode = Products.countryCode
                                    {where_request_part_for_code_words(codewords)} AND 
                                    C2.countryFullName LIKE "%%Росс%%"
                                    AND C.publishYear >= {year_start} 
                                    AND C.publishYear <= {year_finish}
                                    GROUP BY ktru) ktru_rus_val on ktru_rus_val.ktru = Products.KTRUcode
                            {where_request_part_for_code_words(codewords)}
                            AND C.publishYear >= {year_start} 
                            AND C.publishYear <= {year_finish}
                            GROUP BY KTRUcode, KTRUname     
                    """, dbconnection)
    except SQLAlchemyError as error:
        print("SQLAlchemy error:", error)
    except Exception as error:
        print("SQL query error in db_get_ktru_dataframe:", error)
    finally:
        return df


def db_get_regions() -> pd.DataFrame:
    database_url = f"mysql+pymysql://{DBInfo.USER}:{DBInfo.PASSWORD}@{DBInfo.HOST}:{DBInfo.PORT}/{DBInfo.NAME}"
    engine = sqlalchemy.create_engine(database_url)

    try:
        with engine.connect() as dbconnection:
            df = pd.read_sql(f""" SELECT
                                    code,
                                    name
                                  FROM Regions 
                        """, dbconnection)
    except SQLAlchemyError as error:
        print("SQLAlchemy error:", error)
    except Exception as error:
        print("SQL query error in db_get_regions:", error)
    finally:
        return df


def db_gel_all_info_dataframe(codewords: list, year_start: int, year_finish: int) -> pd.DataFrame:
    database_url = f"mysql+pymysql://{DBInfo.USER}:{DBInfo.PASSWORD}@{DBInfo.HOST}:{DBInfo.PORT}/{DBInfo.NAME}"
    engine = sqlalchemy.create_engine(database_url)

    try:
        with engine.connect() as dbconnection:
            df = pd.read_sql(f"""SELECT
                                C.id as НомерКонтракта,
                                C.publishDay as ДеньПубликации,
                                C.publishMonth as МесяцПубликации,
                                C.publishYear as ГодПубликации,
                                LF.singularName as ФормаСобственности,
                                C.link as Ссылка,
                                C.protocolDate as ДатаЗаключенияКонтракта,
                                Products.name as Наименование,
                                KTRUcode as КодКТРУ,
                                KTRUname as НаименованиеКТРУ,
                                prodtype as Тип,
                                quantity as Количество,
                                O.fullName as ЕдиницыИзмерения,
                                Products.priceRUR as ЦенаЗаЕдИзм,
                                Products.sumRUR as Сумма,
                                medicalProductCode as НомерНКМИ,
                                medicalProductName as НаименованиеНКМИ,
                                C2.countryFullName as СтранаПроисхождения,
                                M.mnnName as МНН,
                                C3.fullName as Заказчик,
                                C3.inn as ИННЗаказчика,
                                R.name as РегионЗаказчика,
                                C.suppliersInfo as Поставщики
                             FROM Products
                                 INNER JOIN Contracts C on Products.contractId = C.id
                                 INNER JOIN Countries C2 on C2.countryCode = Products.countryCode
                                 INNER JOIN Customers C3 on C.customerRegNum = C3.regNum
                                 INNER JOIN OKEI O on O.code = Products.OKEIcode
                                 INNER JOIN Regions R on substr(C3.inn, 0, 3) = R.code
                                 INNER JOIN LegalForms LF on LF.code = C3.legalFormCode
                                 INNER JOIN MNN M on M.mnnExternalCode = Products.mnnExternalCode
                             {where_request_part_for_code_words(codewords)} 
                             AND C.publishYear >= {year_start} 
                             AND C.publishYear <= {year_finish}
                                """, dbconnection)
    except SQLAlchemyError as error:
        print("SQLAlchemy error:", error)
    except Exception as error:
        print("SQL query error in db_gel_all_info_dataframe:", error)
    finally:
        return df


def db_get_year_value_dataframe(codewords: list, year_start: int, year_finish: int) -> pd.DataFrame:
    database_url = f"mysql+pymysql://{DBInfo.USER}:{DBInfo.PASSWORD}@{DBInfo.HOST}:{DBInfo.PORT}/{DBInfo.NAME}"
    engine = sqlalchemy.create_engine(database_url)

    try:
        with engine.connect() as dbconnection:
            df = pd.read_sql(f"""SELECT
                                C.publishYear as Год,
                                SUM(sumRUR) as Сумма,
                                SUM(rus_val.value) as СуммаРоссийскогоПроизводства,
                                100 * SUM(rus_val.value) / SUM(sumRUR) as ПроцентРоссийскогоПроизводства,
                                SUM(quantity) as Количество,
                                SUM(rus_val.colvo) as количествоРоссийскогоПроизводства,
                                100 * SUM(rus_val.colvo) / SUM(quantity) as ПроцентКолВаРоссийскогоПроизводства    
                             FROM Products
                                 INNER JOIN Contracts C on Products.contractId = C.id
                                 LEFT JOIN (SELECT
                                                publishYear,
                                                SUM(sumRUR) as value,
                                                SUM(quantity) as colvo
                                            FROM Products
                                            INNER JOIN Contracts C on Products.contractId = C.id
                                            INNER JOIN Countries C2 on C2.countryCode = Products.countryCode
                                            {where_request_part_for_code_words(codewords)} 
                                             AND C.publishYear >= {year_start} 
                                             AND C.publishYear <= {year_finish}
                                            AND C2.countryFullName LIKE "%%Росс%%"
                                            GROUP BY C.publishYear) rus_val on rus_val.publishYear = C.publishYear
                            {where_request_part_for_code_words(codewords)} 
                             AND C.publishYear >= {year_start} 
                             AND C.publishYear <= {year_finish}
                            GROUP BY C.publishYear
                            ORDER BY C.publishYear;
                                """, dbconnection)
    except SQLAlchemyError as error:
        print("SQLAlchemy error:", error)
    except Exception as error:
        print("SQL query error in db_get_year_value_dataframe:", error)
    finally:
        return df


if __name__ == "__main__":
    df = db_product_price_by_country_by_month(["контур дыхательн"], 5902293788)
    print(df)
