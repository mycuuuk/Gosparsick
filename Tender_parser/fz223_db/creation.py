import sqlite3
import pandas as pd
from fz223_db.common import DB_NAME


def db_initialise():
    dbconnection = sqlite3.connect(DB_NAME)
    try:
        dbobject = dbconnection.cursor()

        dbobject.execute("""CREATE TABLE IF NOT EXISTS Products(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT,
                    startDate DATE,
                    productName TEXT,
                    okpd2 TEXT,
                    quantity INT,
                    unitPrice FLOAT,
                    country TEXT,
                    organization TEXT,
                    organizationFull TEXT,
                    organizationINN TEXT,
                    contractPrice FLOAT,
                    contractName TEXT
                )
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