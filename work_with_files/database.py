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
            print("Error while connecting to PostgreSQL:", error)

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
            print("Error while executing query:", error)

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            print("Disconnected from PostgreSQL")
        else:
            print("No connection to PostgreSQL")
