import mysql.connector
from tender_db.data_base_common import DBInfo


def db_add_customer(customer: tuple, customer_regnum: int, legalform: tuple, legalform_code: int):
    dbconnection = mysql.connector.connect(
        host=DBInfo.HOST,
        port=DBInfo.PORT,
        user=DBInfo.USER,
        password=DBInfo.PASSWORD,
        database=DBInfo.NAME
    )
    try:
        dbobject = dbconnection.cursor()
        dbobject.execute("INSERT IGNORE INTO LegalForms VALUES(%s, %s);", legalform)
        dbobject.execute("INSERT IGNORE INTO Customers VALUES(%s, %s, %s, %s, %s, %s, %s, %s);", customer)
        dbconnection.commit()
    except mysql.connector.Error as error:
        print("MySQL error", error)
        dbconnection = False
    finally:
        if dbconnection:
            dbconnection.close()


def db_add_product(product: tuple, country: tuple, okei: tuple, mnn: tuple, countryCode: int, OKEIcode: int, mnn_code: str):
    dbconnection = mysql.connector.connect(
        host=DBInfo.HOST,
        port=DBInfo.PORT,
        user=DBInfo.USER,
        password=DBInfo.PASSWORD,
        database=DBInfo.NAME
    )
    try:
        dbobject = dbconnection.cursor()
        dbobject.execute("INSERT IGNORE INTO Countries VALUES(%s, %s);", country)
        dbobject.execute("INSERT IGNORE INTO OKEI VALUES(%s, %s, %s);", okei)
        dbobject.execute("INSERT IGNORE INTO MNN VALUES(%s, %s, %s);", mnn)
        dbobject.execute("INSERT INTO Products VALUES(NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", product)
        dbconnection.commit()
    except mysql.connector.Error as error:
        print("MySQL error", error)
        dbconnection = False
    finally:
        if dbconnection:
            dbconnection.close()


def db_add_contract(id: str, contract: tuple):
    dbconnection = mysql.connector.connect(
        host=DBInfo.HOST,
        port=DBInfo.PORT,
        user=DBInfo.USER,
        password=DBInfo.PASSWORD,
        database=DBInfo.NAME
    )
    try:
        dbobject = dbconnection.cursor()
        dbobject.execute("INSERT IGNORE INTO Contracts VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", contract)
        dbconnection.commit()
    except mysql.connector.Error as error:
        print("MySQL error", error)
        dbconnection = False
    finally:
        if dbconnection:
            dbconnection.close()
