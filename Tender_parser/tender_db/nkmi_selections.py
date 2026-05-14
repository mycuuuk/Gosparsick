import sqlite3
import pandas as pd
from tender_db.data_base_common import DB_NAME


def db_get_nkmi_data(nkmi: str, year_start: int, year_finish: int) -> pd.DataFrame:
    dbconnection = sqlite3.connect(DB_NAME)
    df = pd.DataFrame()
    try:
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
                                 WHERE medicalProductCode LIKE "%{nkmi}%"
                                 AND C.publishYear >= {year_start} 
                                 AND C.publishYear <= {year_finish}
                                    """, dbconnection)
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    except:
        print("SQL querry error in db_get_nkmi_data")
    finally:
        if (dbconnection):
            dbconnection.close()
        return df
