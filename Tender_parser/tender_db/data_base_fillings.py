import sqlite3
from tender_db.data_base_common import DB_NAME


def db_add_customer(customer: tuple, customer_regnum: int, legalform: tuple, legalform_code: int):
    dbconnection = sqlite3.connect(DB_NAME)
    try:
        dbobject = dbconnection.cursor()

        dbobject.execute("INSERT OR IGNORE INTO LegalForms VALUES(?, ?);", legalform)
        dbobject.execute("INSERT OR IGNORE INTO Customers VALUES(?, ?, ?, ?, ?, ?, ?, ?);", customer)

        dbconnection.commit()
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    finally:
        if (dbconnection):
            dbconnection.close()


def db_add_product(product: tuple, country: tuple, okei: tuple, mnn: tuple, countryCode: int, OKEIcode: int, mnn_code: str):
    dbconnection = sqlite3.connect(DB_NAME)
    try:
        dbobject = dbconnection.cursor()

        dbobject.execute("INSERT OR IGNORE INTO Countries VALUES(?, ?);", country)
        dbobject.execute("INSERT OR IGNORE INTO OKEI VALUES(?, ?, ?);", okei)

        dbobject.execute("INSERT OR IGNORE INTO MNN VALUES(?, ?, ?);", mnn)

        dbobject.execute("INSERT INTO Products VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", product)

        dbconnection.commit()
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    finally:
        if (dbconnection):
            dbconnection.close()


def db_add_contract(id: str, contract: tuple):
    dbconnection = sqlite3.connect(DB_NAME)
    try:
        dbobject = dbconnection.cursor()
        dbobject.execute("INSERT OR IGNORE INTO Contracts VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", contract)
        dbconnection.commit()
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False

    finally:
        if (dbconnection):
            dbconnection.close()


