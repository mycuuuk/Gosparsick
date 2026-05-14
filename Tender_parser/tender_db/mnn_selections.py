import sqlite3
import pandas as pd
from tender_db.data_base_common import DB_NAME


def where_request_part_for_code_words(code_frases: list) -> str:
    query_text = """ WHERE ("""
    k = 0
    for code_frase in code_frases:
        k+=1
        code_words_untreated = code_frase.strip().split(" ")

        code_words = []
        for code_word in code_words_untreated:
            if len(code_word.strip()) >= 2:
                code_words.append(code_word.upper().strip())

        # Формируем параметры запроса (WHERE)

        query_text += """("""
        for i in range(len(code_words)):
            if i != 0:
                query_text += " AND "
            query_text += f"""(MNN.mnnName LIKE "%{code_words[i]}%")"""

        query_text += """)"""

        if k != len(code_frases):
            query_text += """ OR """

    query_text += """)"""
    return query_text


def db_mnn_codes_by_code_words(code_words: list) -> (list, list):
    dbconnection = sqlite3.connect(DB_NAME)
    nums = []
    names = []
    if not code_words:
        where = ""
    else:
        where = where_request_part_for_code_words(code_words)

    try:
        df = pd.read_sql(f"""SELECT
                                mnnExternalCode,
                                mnnName
                            FROM MNN
                            {where} AND mnnExternalCode != ''
                            """, dbconnection)
        if not df.empty:
            nums = df["mnnExternalCode"].tolist()
            names = df['mnnName'].tolist()
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    except:
        print("SQL querry error in db_mnn_codes_by_code_words")
    finally:
        if (dbconnection):
            dbconnection.close()
        return nums, names
