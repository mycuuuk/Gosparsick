import mysql.connector
from tender_db.data_base_common import DBInfo


def db_contract_is_in_base(id: str) -> bool:
    dbconnection = mysql.connector.connect(
        host=DBInfo.HOST,
        port=DBInfo.PORT,
        user=DBInfo.USER,
        password=DBInfo.PASSWORD,
        database=DBInfo.NAME
    )
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
    except mysql.connector.Error as error:
        print("SQLite3 error", error)
        dbconnection = False
    finally:
        if (dbconnection):
            dbconnection.close()
        return isin
