import pyodbc
 # CONFIG
text_file = open("DataBase.config", "r")
BOT_CONFIG = text_file.readlines()
text_file.close()
server_addr = str(BOT_CONFIG[0]).strip()
database = str(BOT_CONFIG[1]).strip()
username = str(BOT_CONFIG[2]).strip()
password = str(BOT_CONFIG[3]).strip()
driver = str(BOT_CONFIG[4]).strip()

conn = pyodbc.connect(
    'DRIVER={' + driver + '};SERVER=' + server_addr + ';DATABASE=' + database + ';UID=' + username + ';PWD='
    + password)
cursor = conn.cursor()
print('SQL SERVER CONNECTION - SUCCEEDED')


class mssql:
    """Instantiate SQL methods """

    def __init__(self):
        pass

    def update(self, query, *params):
        global cursor, conn
        try:
            cursor.execute(query, *params)
            conn.commit()
        except Exception as e:
            print(e)
            conn.close()
            conn = pyodbc.connect(
                'DRIVER={' + driver + '};SERVER=' + server_addr + ';DATABASE=' + database
                + ';UID=' + username + ';PWD=' + password)
            cursor = conn.cursor()
            self.update(query, *params)

    def select(self, query, *params):
        global cursor, conn
        try:
            cursor.execute(query, *params)
            return cursor
        except Exception as e:
            print(e)
            conn.close()
            conn = pyodbc.connect(
                'DRIVER={' + driver + '};SERVER=' + server_addr + ';DATABASE=' + database + ';UID='
                + username + ';PWD=' + password)
            cursor = conn.cursor()
            self.select(query, *params)