import psycopg2
from colorama import init, Fore, Style

init()


class PostgreSQLDatabase:
    def __init__(self):
        self.host = 'localhost'
        self.port = 5433
        self.user = 'postgres'
        self.password = 'postgres'
        self.database = 'postgres'
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
            print(f"{Fore.CYAN}Connected to PostgreSQL{Style.RESET_ALL}")
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
            print(f"{Fore.CYAN}Disconnected from PostgreSQL{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTRED_EX}No connection to PostgreSQL{Style.RESET_ALL}")

    def truncate_table(self, table_name):
        try:
            query = f"TRUNCATE TABLE {table_name} CASCADE;"
            self.execute_query(query)
            print(f"{Fore.CYAN}All data {Fore.RED}deleted{Fore.CYAN} from the table {Fore.MAGENTA}{table_name}{Style.RESET_ALL}")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"{Fore.RED}Error while truncating table {table_name}: {error} {Style.RESET_ALL}")
