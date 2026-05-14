import sqlite3
import pandas as pd
from tender_db.data_base_common import DB_NAME


def db_initialise():
    dbconnection = sqlite3.connect(DB_NAME)
    try:
        dbobject = dbconnection.cursor()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS LegalForms(
            code INTEGER PRIMARY KEY,
            singularName TEXT
        )
        """)
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS Customers(
            regNum INTEGER PRIMARY KEY,
            fullName TEXT,
            shortName TEXT,
            inn TEXT,
            kpp TEXT,
            OKPO TEXT,
            customerCode TEXT,
            legalFormCode INT,
            FOREIGN KEY (legalFormCode) REFERENCES LegalForms(code)     
        )
        """)
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS OKEI(
                    code TEXT PRIMARY KEY,
                    nationalCode TEXT,
                    fullName TEXT
                )
                """)
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS Countries(
                    countryCode INTEGER PRIMARY KEY,
                    countryFullName TEXT
                )
                """)
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS Contracts(
                    id TEXT PRIMARY KEY,
                    publishDay INT,
                    publishMonth INT,
                    publishYear INT,
                    customerRegNum INT,
                    protocolDate TEXT,
                    documentBase TEXT,
                    priceRUR INT,
                    link TEXT,
                    suppliersInfo TEXT,
                    
                    FOREIGN KEY (customerRegNum) REFERENCES Customers(regNum)
                )
                """)
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS MNN(
                                    mnnExternalCode TEXT PRIMARY KEY,
                                    mnnDrugCode TEXT,
                                    mnnName TEXT
                                )
                                """)
        dbconnection.commit()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS Products(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            contractId TEXT,
                            KTRUcode TEXT,
                            KTRUname TEXT,
                            prodtype TEXT,
                            OKEIcode TEXT,
                            quantity INT,
                            priceRUR INT,
                            sumRUR INT,
                            countryCode INT,
                            medicalProductCode INT,
                            medicalProductName TEXT,
                            mnnExternalCode TEXT,
                            
                            FOREIGN KEY (countryCode) REFERENCES Countries(countryCode)
                            FOREIGN KEY (OKEIcode) REFERENCES OKEI(code)
                            FOREIGN KEY (contractId) REFERENCES Contracts(id)
                        )
                        """)
        dbconnection.commit()

        dbobject.execute("""INSERT OR IGNORE INTO MNN VALUES("", "", "")                                
                                """)
        dbconnection.commit()

        dbobject.execute("""DROP TABLE IF EXISTS Regions
                    """)
        dbconnection.commit()

        df = pd.read_csv("RusRegions.csv", dtype=str)
        df.to_sql("Regions", dbconnection)


    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    finally:
        if (dbconnection):
            dbconnection.close()

if __name__ == "__main__":
    db_initialise()
