from openpyxl import load_workbook
from openpyxl.utils import coordinate_to_tuple, get_column_letter
from database import Database
import time
start_time = time.time()
# Загрузка файла Excel
workbook = load_workbook(filename='ОН_ФЭВТ_1 курс.xlsx')

# Получение активного листа
sheet = workbook.active


def move_work_zone_down():
    global work_zone
    top_row, top_col = coordinate_to_tuple(work_zone[0][0].coordinate)
    bottom_row, bottom_col = coordinate_to_tuple(work_zone[-1][-1].coordinate)
    top_row += 3
    bottom_row += 3
    top_cell = f"{get_column_letter(top_col)}{top_row}"
    bottom_cell = f"{get_column_letter(bottom_col)}{bottom_row}"
    work_zone = sheet[top_cell:bottom_cell]


def move_work_zone_right():
    global work_zone
    top_row, top_col = coordinate_to_tuple(work_zone[0][0].coordinate)
    bottom_row, bottom_col = coordinate_to_tuple(work_zone[-1][-1].coordinate)
    top_col += 4
    bottom_col += 4
    top_cell = f"{get_column_letter(top_col)}{top_row}"
    bottom_cell = f"{get_column_letter(bottom_col)}{bottom_row}"
    work_zone = sheet[top_cell:bottom_cell]


def move_work_zone_up():
    global work_zone
    top_row, top_col = coordinate_to_tuple(work_zone[0][0].coordinate)
    bottom_row, bottom_col = coordinate_to_tuple(work_zone[-1][-1].coordinate)
    top_row = 7
    bottom_row = 9
    top_cell = f"{get_column_letter(top_col)}{top_row}"
    bottom_cell = f"{get_column_letter(bottom_col)}{bottom_row}"
    work_zone = sheet[top_cell:bottom_cell]


def get_current_group_name() -> str:
    global work_zone
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


db = Database('../identifier.sqlite')
db.connect()

# Определение "рабочей зоны" (тут группа ячеек 4 на 3, в которой вся инфа для 1 пары 1 группы)
work_zone = sheet['H7':'K9']

# Вывод содержимого "рабочей зоны" для 1 недели
# Цикл для прохода по одной группе
for number_group in range(10):
    # Название группы (Например прин-166)
    group_name = get_current_group_name()
    print(f'Название группы: {group_name}')
    # Цикл для прохода по всей неделе
    for week_day in range(1, 6+1):
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
            print(f'Есть ли занятие: {has_lesson}')
            print("_________________________")

            move_work_zone_down()
    move_work_zone_up()
    move_work_zone_right()
print(time.time()-start_time)