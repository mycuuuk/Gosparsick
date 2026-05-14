import sqlite3
import os
import pandas as pd

from medtechproducts_db.db_common import DB_NAME


def where_request_part_for_code_words(code_frases: list) -> str:
    query_text = """ WHERE ("""
    k = 0
    for code_frase in code_frases:
        k+=1
        code_words_untreated = code_frase.strip().split(" ")

        code_words = []
        for code_word in code_words_untreated:
            if len(code_word.strip()) >= 2:
                code_words.append(code_word.lower().strip())
            #     code_words.append(code_word[0].strip().upper() + code_word[1:].strip().lower())
            #     code_words.append(code_word.strip().upper())

        # Формируем параметры запроса (WHERE)

        query_text += """("""
        for i in range(len(code_words)):
            if i != 0:
                query_text += " AND "
            query_text += f"""(LOWER(Zakupki_ktru.title) LIKE "%{code_words[i]}%" 
                        OR LOWER(Zakupki_ktru.title) LIKE "%{str(code_words[i][0]).upper() + code_words[i][1:]}%" 
                        OR LOWER(Zakupki_ktru.title) LIKE "%{code_words[i].upper()}%")"""

        query_text += """)"""

        if k != len(code_frases):
            query_text += """ OR """

    query_text += """)"""
    return query_text


def db_ktru_nums_by_code_words(code_words: list) -> list:
    if not os.path.exists(DB_NAME):
        return []

    dbconnection = sqlite3.connect(DB_NAME)
    nums = []
    if not code_words:
        where = ""
    else:
        where = where_request_part_for_code_words(code_words)

    try:
        df = pd.read_sql(f"""SELECT
                                num
                            FROM Zakupki_ktru
                            {where}
                            """, dbconnection)
        if not df.empty:
            nums = df["num"].tolist()
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    except Exception as error:
        print(f"SQL query error in db_ktru_nums_by_code_words: {error}")
    finally:
        if (dbconnection):
            dbconnection.close()
        return nums


def db_ktru_title_by_num(code: str) -> str:
    if not os.path.exists(DB_NAME):
        return ''

    dbconnection = sqlite3.connect(DB_NAME)
    title = ''
    try:
        df = pd.read_sql(f"""SELECT
                                title
                            FROM Zakupki_ktru
                            WHERE num = "{code}"
                            """, dbconnection)
        if not df.empty:
            title = df["title"].tolist()[0]
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    except Exception as error:
        print(f"SQL query error in db_ktru_title_by_num: {error}")
    finally:
        if (dbconnection):
            dbconnection.close()
        return title


def db_ktru_list_by_nkmi(nkmi: str) -> list:
    if not os.path.exists(DB_NAME):
        return []

    dbconnection = sqlite3.connect(DB_NAME)
    ktru = []
    try:
        df = pd.read_sql(f"""SELECT
                                Zakupki_ktru.num as ktru
                            FROM Ktru_classifications
                            INNER JOIN Zakupki_ktru ON Zakupki_ktru.zakupki_id = ktru_id
                            INNER JOIN Classificator_items ON Classificator_items.id = classificator_item_id
                            WHERE Classificator_items.id LIKE "%{nkmi}%"
                                """, dbconnection)
        ktru = df["ktru"].tolist()
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    except Exception as error:
        print(f"SQL query error in db_ktru_list_by_nkmi: {error}")
    finally:
        if (dbconnection):
            dbconnection.close()
        return ktru


if __name__ == "__main__":
    print(db_ktru_nums_by_code_words(["трубка дыхательная"]))
    # print(db_ktru_title_by_num("22.21.29.120-00000023"))

