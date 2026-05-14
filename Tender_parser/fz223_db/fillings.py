import sqlite3
from fz223_db.common import DB_NAME


def db_add_contract(product: dict):  # Ключи продуктс должны совпадать с названиями столбцов в таблице
    dbconnection = sqlite3.connect(DB_NAME)
    try:
        dbobject = dbconnection.cursor()
        columns = ', '.join(product.keys())
        placeholders = ', '.join(['?'] * len(product))
        sql = f'INSERT INTO Products ({columns}) VALUES ({placeholders})'
        dbobject.execute(sql, tuple(product.values()))
        dbconnection.commit()
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False

    finally:
        if (dbconnection):
            dbconnection.close()
