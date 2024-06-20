import csv
import os
import time

from colorama import init, Fore, Style
from backend.database import PostgreSQLDatabase

init()


def load_csv_to_database(csv_file, table_name, db):
    try:
        db.connect()

        # Создание таблицы, если она не существует
        create_table_query = """
            CREATE TABLE IF NOT EXISTS {} (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(255),
            university_name VARCHAR(255),
            faculty VARCHAR(255),
            oop_group_2023_2024 VARCHAR(255),
            ck_program VARCHAR(255),
            ck_group VARCHAR(255)
        );
        """.format(table_name)
        db.execute_query(create_table_query)

        db.truncate_table(table_name)

        # Загрузка данных из CSV файла
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Пропускаем заголовок CSV файла
            for row in reader:
                full_name = row[2]
                university_or_branch_1 = row[3]
                university_or_branch_2 = row[4]
                oop_group_2023_2024 = row[6].lower().replace(' ', '')
                ck_program = row[7].lower()

                # Проверка наличия группы в таблице groups
                check_group_query = """
                    SELECT COUNT(*)
                    FROM groups_vstu_and_others
                    WHERE group_name = %s
                """
                group_exists = db.execute_query(check_group_query, (oop_group_2023_2024,))[1][0][0] > 0

                # Если группы нет, добавляем ее
                if not group_exists:
                    insert_group_query = """
                        INSERT INTO groups_vstu_and_others (group_name, faculty, program)
                        VALUES (%s, %s, %s)
                    """
                    db.execute_query(insert_group_query, (oop_group_2023_2024, university_or_branch_2, ck_program))

                # Вставка данных в таблицу students
                insert_query = """
                    INSERT INTO {} (full_name, university_name, faculty, oop_group_2023_2024, ck_program)
                    VALUES (%s, %s, %s, %s, %s)
                """.format(table_name)
                db.execute_query(insert_query, (full_name, university_or_branch_1, university_or_branch_2,
                                                oop_group_2023_2024, ck_program))

        print(f"{Fore.GREEN}Данные успешно загружены из CSV файла в таблицу.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Произошла ошибка: {e}{Style.RESET_ALL}")
    finally:
        db.disconnect()


def find_csv_files(directory):
    csv_files = []
    # Рекурсивно обходим все файлы и подпапки в указанной директории
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv") and not file.startswith("~$"):
                csv_files.append(os.path.join(root, file))
    return csv_files[0]


def run(path: str = '.'):
    t = time.time()
    csv_file = find_csv_files(path)
    table_name = "students_ck"
    # Создаем объект класса PostgreSQLDatabase
    db = PostgreSQLDatabase()
    load_csv_to_database(csv_file, table_name, db)
    print("--- %s seconds --- group_parser" % (time.time() - t))


# Пример использования
if __name__ == "__main__":
    run()
