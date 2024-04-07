import sqlite3


class database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.sql = self.conn.cursor()

    def execute(self, query):
        self.sql.execute(query)
        return self.sql.fetchall()


db = database("diseases_info.db")
disease = 'грипп'
quer = f"SELECT * FROM diseases WHERE disease = '{disease}'"

print(type(db.execute(quer)))

p = db.execute(quer)
