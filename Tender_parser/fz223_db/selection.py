import sqlite3
import pandas as pd
from fz223_db.common import DB_NAME


def db_gel_all_info_dataframe(codewords: list, year_start: int, year_finish: int) -> pd.DataFrame:
    dbconnection = sqlite3.connect(DB_NAME)
    df = pd.DataFrame()

    try:
        # Создаем шаблоны для LIKE условий
        contract_name_conditions = " OR ".join([f"p.contractName LIKE ?" for _ in codewords])
        product_name_conditions = " OR ".join([f"p.productName NOT LIKE ?" for _ in codewords])
        product_like_name_conditions = " OR ".join([f"p.productName LIKE ?" for _ in codewords])

        # Подготавливаем значения для условий
        contract_name_values = [f"%{word}%" for word in codewords]
        product_name_values = [f"%{word}%" for word in codewords]

        query = f"""
            WITH RelevantLinks AS (
                -- Выбираем все уникальные ссылки, где contractName содержит любое из искомых слов
                -- и productName не содержит ни одного из слов
                SELECT DISTINCT p.link
                FROM Products p
                WHERE ({contract_name_conditions}) AND ({product_name_conditions})
            )

            SELECT
                p.link AS Ссылка,
                p.startDate AS НачалоИсполнения,
                p.productName AS Наименование,
                p.okpd2 AS ОКПД2,
                p.quantity AS Количество,
                p.unitPrice AS ЦенаЗаЕдИзм,
                p.quantity * p.unitPrice AS Сумма,
                p.country AS СтранаПроисхождения,
                p.organization AS НаименованиеЗаказчика,
                p.organizationFull AS НаименованиеЗаказчикаПолное,
                p.organizationINN AS ИННЗаказчика,
                r.name AS РегионЗаказчика,  -- Подтягиваем название региона
                p.contractPrice AS СуммаКонтракта,
                p.contractName AS НаименованиеКонтракта
            FROM Products p
            LEFT JOIN Regions r ON SUBSTR(p.organizationINN, 1, 2) = r.code
            WHERE 
                (STRFTIME('%Y-%m-%d', SUBSTR(p.startDate, 7, 4) || '-' ||
                                       SUBSTR(p.startDate, 4, 2) || '-' ||
                                       SUBSTR(p.startDate, 1, 2))
                BETWEEN ? AND ?)
                AND (
                    ({product_like_name_conditions})  -- Берем строки, содержащие любое из слов в contractName
                    OR (
                        p.link NOT IN (SELECT link FROM RelevantLinks)  -- Берем строки без слов, но у которых нет ни одной строки с искомыми словами
                    )
                );
        """

        # Добавляем параметры в список
        params = (
                contract_name_values +  # Для RelevantLinks contractName
                product_name_values +  # Для RelevantLinks productName
                [f"{year_start}-01-01", f"{year_finish}-12-31"] +  # Для фильтра по дате
                contract_name_values  # Для основного условия contractName
        )

        # Плоский список параметров для выполнения запроса
        params = [item for sublist in params for item in (sublist if isinstance(sublist, list) else [sublist])]

        df = pd.read_sql(query, dbconnection, params=params)

    except sqlite3.Error as error:
        print("SQLite3 error:", error)
    except Exception as e:
        print("SQL query error in db_get_all_info_dataframe:", str(e))
    finally:
        if dbconnection:
            dbconnection.close()

    return df

