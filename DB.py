import mysql.connector

class DB:
    def __init__(self, host='localhost', user='root', password='', database='electronicReport', port=3306):
        self.conn = mysql.connector.connect(host=host, user=user, password=password, database=database, port=port)
        self.cursor = self.conn.cursor()

    def execute(self, query, values=None):
        self.cursor.execute(query, values)
        self.conn.commit()

    def select(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def insert(self, table, data):
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute(query, tuple(data.values()))

    def update(self, table, data, condition):
        columns = ', '.join([f"{key}=%s" for key in data.keys()])
        query = f"UPDATE {table} SET {columns} WHERE {condition}"
        self.execute(query, tuple(data.values()))
