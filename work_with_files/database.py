import psycopg2
from colorama import init, Fore, Style

init()


class PostgreSQLDatabase:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Connected to PostgreSQL")
        except (Exception, psycopg2.DatabaseError) as error:
            print(Fore.RED, "Error while connecting to PostgreSQL:", error, Style.RESET_ALL)

    def execute_query(self, query, args=None):
        try:
            cursor = self.connection.cursor()
            if args:
                cursor.execute(query, args)
            else:
                cursor.execute(query)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
                cursor.close()
                return columns, results
            else:
                self.connection.commit()
                cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(Fore.RED, "Error while executing query:", error, Style.RESET_ALL)

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            print("Disconnected from PostgreSQL")
        else:
            print("No connection to PostgreSQL")

    def truncate_table(self, table_name):
        try:
            query = f"TRUNCATE TABLE {table_name} CASCADE;"
            self.execute_query(query)
            print(f"All data deleted from the table {table_name}")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"{Fore.RED}Error while truncating table {table_name}: {error} {Style.RESET_ALL}")
