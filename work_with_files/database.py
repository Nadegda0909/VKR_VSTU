import psycopg2


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
            print("Error while connecting to PostgreSQL", error)

    def execute_query(self, query, args):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, args)
            self.connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while executing query:", error)

