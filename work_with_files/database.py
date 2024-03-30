import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def create_table(self, table_name, columns):
        with self.conn:
            self.conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

    def insert_data(self, table_name, data):
        with self.conn:
            self.conn.execute(f"INSERT INTO {table_name} VALUES {data}")

    def select_data(self, table_name, condition=None):
        with self.conn:
            if condition:
                return self.conn.execute(f"SELECT * FROM {table_name} WHERE {condition}").fetchall()
            else:
                return self.conn.execute(f"SELECT * FROM {table_name}").fetchall()

    def update_data(self, table_name, data, condition=None):
        with self.conn:
            if condition:
                self.conn.execute(f"UPDATE {table_name} SET {data} WHERE {condition}")
            else:
                self.conn.execute(f"UPDATE {table_name} SET {data}")

    def delete_data(self, table_name, condition=None):
        with self.conn:
            if condition:
                self.conn.execute(f"DELETE FROM {table_name} WHERE {condition}")
            else:
                self.conn.execute(f"DELETE FROM {table_name}")

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
