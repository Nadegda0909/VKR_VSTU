from openpyxl import load_workbook
from openpyxl.utils import coordinate_to_tuple, get_column_letter
from database import PostgreSQLDatabase
from colorama import init, Fore, Style

# Инициализация colorama (необходимо вызывать один раз в начале программы)
init()
# Загрузка файла Excel
workbook = load_workbook(filename='ОН_ФЭВТ_1 курс.xlsx')

# Получение активного листа
sheet = workbook.active

db = PostgreSQLDatabase(host="localhost",
                        port="5432",
                        user="sergey",
                        password="Serez_Groza_1337",
                        database="vkr")
db.connect()


def move_work_zone_down(work_zone):
    top_row, top_col = coordinate_to_tuple(work_zone[0][0].coordinate)
    bottom_row, bottom_col = coordinate_to_tuple(work_zone[-1][-1].coordinate)
    top_row += 3
    bottom_row += 3
    top_cell = f"{get_column_letter(top_col)}{top_row}"
    bottom_cell = f"{get_column_letter(bottom_col)}{bottom_row}"
    work_zone = sheet[top_cell:bottom_cell]


def move_work_zone_right(work_zone):
    top_row, top_col = coordinate_to_tuple(work_zone[0][0].coordinate)
    bottom_row, bottom_col = coordinate_to_tuple(work_zone[-1][-1].coordinate)
    top_col += 4
    bottom_col += 4
    top_cell = f"{get_column_letter(top_col)}{top_row}"
    bottom_cell = f"{get_column_letter(bottom_col)}{bottom_row}"
    work_zone = sheet[top_cell:bottom_cell]


def move_work_zone_up(work_zone):
    top_row, top_col = coordinate_to_tuple(work_zone[0][0].coordinate)
    bottom_row, bottom_col = coordinate_to_tuple(work_zone[-1][-1].coordinate)
    top_row -= 18 * 6
    bottom_row -= 18 * 6
    top_cell = f"{get_column_letter(top_col)}{top_row}"
    bottom_cell = f"{get_column_letter(bottom_col)}{bottom_row}"
    work_zone = sheet[top_cell:bottom_cell]


def move_to_second_week(work_zone):
    top_row, top_col = coordinate_to_tuple(work_zone[0][0].coordinate)
    bottom_row, bottom_col = coordinate_to_tuple(work_zone[-1][-1].coordinate)
    top_row = 116
    bottom_row = 118
    top_col = 8
    bottom_col = 11
    top_cell = f"{get_column_letter(top_col)}{top_row}"
    bottom_cell = f"{get_column_letter(bottom_col)}{bottom_row}"
    work_zone = sheet[top_cell:bottom_cell]


def get_current_group_name(work_zone) -> str:
    top_row, top_col = coordinate_to_tuple(work_zone[0][0].coordinate)
    top_row -= 1
    return str(sheet.cell(row=top_row, column=top_col).value).replace(" ", "").lower()


def check_cell_has_data(cell):
    if cell.value is not None:
        return True
    else:
        # Если ячейка объединена, проверяем, входит ли ее координата в список объединенных ячеек
        for merged_range in sheet.merged_cells.ranges:
            if cell.coordinate in merged_range:
                # Получаем координаты первой ячейки объединенной области
                first_cell_row, first_cell_col = merged_range.min_row, merged_range.min_col
                first_cell = sheet.cell(row=first_cell_row, column=first_cell_col)
                if first_cell.value is not None:
                    return True
        return False


def analyze_dates():
    ...


def analyze_worksheet():
    # Определение "рабочей зоны" (тут группа ячеек 4 на 3, в которой вся инфа для 1 пары 1 группы)
    work_zone = sheet['H7':'K9']

    # Словарь для групп (нужен для того, чтобы знать в какой колонке, какая группа)
    groups_dict = {}

    for num_week in range(1, 2 + 1):
        print(num_week)
        # Цикл для прохода по одной группе
        for number_group in range(10):
            # Название группы (Например прин-166)
            if groups_dict.get(number_group) is None:
                group_name = get_current_group_name(work_zone)
                groups_dict.update({number_group: group_name})
            else:
                group_name = groups_dict[number_group]
            print(Fore.GREEN + f'Название группы: {group_name}' + Style.RESET_ALL)
            # Добавить в бд название группы
            insert_query = ("INSERT INTO Groups (group_name) "
                            "SELECT %s "
                            "WHERE NOT EXISTS ("
                            "SELECT 1 FROM Groups WHERE group_name = %s);")
            db.execute_query(insert_query, (group_name, group_name))

            # Цикл для прохода по всей неделе
            for week_day in range(1, 6 + 1):
                print(f"День недели: {week_day}")
                # Цикл для прохода по одному дню
                for number_para in range(1, 6 + 1):
                    print(f'Номер пары: {number_para}')
                    # Цикл для прохода по одной паре
                    has_lesson = False
                    for row in work_zone:
                        # Цикл для прохода по одной строке
                        if has_lesson:
                            break
                        for cell in row:
                            if check_cell_has_data(cell):
                                has_lesson = True
                                break
                        #     print(f'Значение в ячейке: {cell.value}')
                        # print("-------")
                    insert_query = """
                    INSERT INTO Lessons (group_name, lesson_order, is_busy)
                    VALUES (%s, %s, %s);
                    """
                    db.execute_query(insert_query, (group_name, number_para, has_lesson))

                    print(f'Есть ли занятие: {has_lesson}')
                    print("_________________________")

                    move_work_zone_down(work_zone)
            move_work_zone_up(work_zone)
            move_work_zone_right(work_zone)
        move_to_second_week(work_zone)
