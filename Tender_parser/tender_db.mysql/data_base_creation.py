import sqlalchemy
import mysql.connector
import pandas as pd
from tender_db.data_base_common import DBInfo


def db_initialise():
    try:
        dbconnection = mysql.connector.connect(
            host=DBInfo.HOST,
            port=DBInfo.PORT,
            user=DBInfo.USER,
            password=DBInfo.PASSWORD,
            database=DBInfo.NAME
        )
        dbobject = dbconnection.cursor()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS LegalForms(
                code INT PRIMARY KEY,
                singularName TEXT
            )""")
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS Customers(
                regNum VARCHAR(255) PRIMARY KEY,
                fullName TEXT,
                shortName TEXT,
                inn TEXT,
                kpp TEXT,
                OKPO TEXT,
                customerCode TEXT,
                legalFormCode INT
                )""")
                # FOREIGN KEY (legalFormCode) REFERENCES LegalForms(code)
            # )""")
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS OKEI(
                code VARCHAR(255) PRIMARY KEY,
                nationalCode TEXT,
                fullName TEXT
            )""")
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS Countries(
                countryCode INT PRIMARY KEY,
                countryFullName TEXT
            )""")
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS Contracts(
                id VARCHAR(255) PRIMARY KEY,
                publishDay INT,
                publishMonth INT,
                publishYear INT,
                customerRegNum VARCHAR(255),
                protocolDate TEXT,
                documentBase TEXT,
                priceRUR INT,
                link TEXT,
                suppliersInfo TEXT
            )""")
                # FOREIGN KEY (customerRegNum) REFERENCES Customers(regNum)
            # )""")
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS MNN(
                mnnExternalCode VARCHAR(255) PRIMARY KEY,
                mnnDrugCode TEXT,
                mnnName TEXT
            )""")
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS Products(
                id INT PRIMARY KEY AUTO_INCREMENT,
                name TEXT,
                contractId VARCHAR(255),
                KTRUcode TEXT,
                KTRUname TEXT,
                prodtype TEXT,
                OKEIcode VARCHAR(255),
                quantity INT,
                priceRUR INT,
                sumRUR INT,
                countryCode INT,
                medicalProductCode INT,
                medicalProductName TEXT,
                mnnExternalCode VARCHAR(255)
            )""")
                # FOREIGN KEY (countryCode) REFERENCES Countries(countryCode),
                # FOREIGN KEY (OKEIcode) REFERENCES OKEI(code),
                # FOREIGN KEY (contractId) REFERENCES Contracts(id)
            # )""")
        dbconnection.commit()

        dbobject.execute("""INSERT INTO MNN (mnnExternalCode, mnnDrugCode, mnnName)
                                SELECT '', '', ''
                                FROM DUAL
                                WHERE NOT EXISTS (
                                SELECT 1 FROM MNN WHERE mnnExternalCode = ''
                            )""")
        dbconnection.commit()

        # Удаление таблицы Regions, если она существует
        dbobject.execute("""DROP TABLE IF EXISTS Regions""")
        dbconnection.commit()

        if dbconnection.is_connected():
            dbconnection.close()

        database_url = f"mysql+pymysql://{DBInfo.USER}:{DBInfo.PASSWORD}@{DBInfo.HOST}:{DBInfo.PORT}/{DBInfo.NAME}"
        engine = sqlalchemy.create_engine(database_url)
        dbconnection = engine.connect()

        # Загрузка данных из CSV в таблицу Regions
        df = pd.read_csv("RusRegions.csv", dtype=str)
        df.to_sql("Regions", dbconnection, if_exists='replace', index=False)

    except mysql.connector.Error as error:
        print("MySQL error", error)


if __name__ == "__main__":
    db_initialise()
