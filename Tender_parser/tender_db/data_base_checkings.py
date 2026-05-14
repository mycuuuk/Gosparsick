import sqlite3
from tender_db.data_base_common import DB_NAME


def db_contract_is_in_base(id: str) -> bool:
    dbconnection = sqlite3.connect(DB_NAME)
    isin = False
    try:
        dbobject = dbconnection.cursor()
        contr = dbobject.execute(f"""SELECT id
                                    FROM Contracts
                                    WHERE id = {id}""")
        if dbobject.fetchone() is None:
            isin = False
        else:
            isin = True
        dbconnection.commit()
    except sqlite3.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    finally:
        if (dbconnection):
            dbconnection.close()
        return isin