from backend.database import PostgreSQLDatabase
from collections import defaultdict, namedtuple
from itertools import count
import re
import time

# Определение именованного кортежа для хранения интервалов
Interval = namedtuple('Interval', ['week_num', 'week_day', 'lesson_interval', 'lesson_date'])


# Функция для получения студентов из других вузов
def fetch_other_students(db):
    query = '''
    SELECT id, full_name, university_name, faculty, oop_group_2023_2024, ck_program
    FROM students_ck
    WHERE ck_group IS NULL
    ORDER BY oop_group_2023_2024;
    '''
    result = db.execute_query(query)
    if result:
        return result[1]
    return []


# Функция для получения всех свободных интервалов из базы данных
def fetch_all_free_intervals(db):
    query = '''
    SELECT g.group_name, d.week_num, d.week_day, d.date
    FROM groups_vstu_and_others g
    JOIN learning_dates d ON TRUE  -- присоединяем все даты к каждой группе
    ORDER BY d.week_num, d.week_day, d.date;
    '''
    result = db.execute_query(query)
    if result:
        intervals = defaultdict(list)
        for row in result[1]:
            group_name, week_num, week_day, lesson_date = row
            intervals[group_name].append(Interval(week_num, week_day, '7-8', lesson_date))
        return intervals
    return defaultdict(list)


# Функция для проверки пересечения интервалов
def is_overlapping(interval1, interval2):
    start1, end1 = map(int, interval1.split('-'))
    start2, end2 = map(int, interval2.split('-'))
    return not (end1 <= start2 or end2 <= start1)


# Функция для получения последней нумерации групп для каждой программы
def fetch_last_group_numbers(db):
    query = '''
    SELECT ck_program, MAX(ck_group) as last_group_name
    FROM students_ck
    WHERE ck_group IS NOT NULL
    GROUP BY ck_program;
    '''
    result = db.execute_query(query)
    last_group_numbers = defaultdict(int)
    if result:
        for row in result[1]:
            program, last_group_name = row
            match = re.search(r'_(\d+)$', last_group_name)
            if match:
                last_group_numbers[program] = int(match.group(1))
    return last_group_numbers


# Функция для создания новых групп и добавления данных в новые таблицы
def create_new_groups(db, students_by_program, all_free_intervals, group_size_limit, max_lessons_per_group=5):
    used_intervals = defaultdict(set)  # Храним занятые интервалы по датам
    group_days = defaultdict(set)  # Храним занятые дни для каждой группы

    exempt_universities = {'кти', 'впи', 'иаис', 'сф'}
    last_group_numbers = fetch_last_group_numbers(db)

    # Обрабатываем каждую программу обучения отдельно
    for program, students in students_by_program.items():
        start_num = last_group_numbers[program] + 1
        group_counter = count(start_num)

        current_group = []
        for student in students:
            university_name = student[2].lower()
            faculty_name = student[3].lower()

            # Проверяем, если университет в списке исключений, то разделяем их по университетам
            if university_name in exempt_universities or faculty_name in exempt_universities:
                if len(current_group) + 1 > group_size_limit:
                    new_group_name = f"{program}_{next(group_counter)}"
                    process_group(db, new_group_name, current_group, all_free_intervals, used_intervals, group_days,
                                  max_lessons_per_group, exempt_universities)
                    current_group = []

                current_group.append(student)
            else:
                # Если университет не в списке исключений, объединяем в одну группу
                if len(current_group) + 1 > group_size_limit:
                    new_group_name = f"{program}_{next(group_counter)}"
                    process_group(db, new_group_name, current_group, all_free_intervals, used_intervals, group_days,
                                  max_lessons_per_group, exempt_universities)
                    current_group = []

                current_group.append(student)

        # Обрабатываем оставшихся студентов в последней группе
        if current_group:
            new_group_name = f"{program}_{next(group_counter)}"
            process_group(db, new_group_name, current_group, all_free_intervals, used_intervals, group_days,
                          max_lessons_per_group, exempt_universities)


# Функция для обработки группы студентов
def process_group(db, new_group_name, students, all_free_intervals, used_intervals, group_days, max_lessons_per_group,
                  exempt_universities):
    # Добавляем новую группу в таблицу groups_vstu_and_others
    db.execute_query(
        '''
        INSERT INTO groups_vstu_and_others (group_name, faculty, course, program)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (group_name) DO NOTHING;
        ''',
        (new_group_name, students[0][3], 1, students[0][5])
    )

    lesson_count = 0
    university_name = students[0][2].lower()  # Преобразуем название университета в нижний регистр
    faculty_name = students[0][3].lower()

    for student in students:
        group_name = student[4].lower()

        # Добавляем студента в новую группу
        db.execute_query(
            '''
            UPDATE students_ck SET ck_group = %s WHERE id = %s
            ''',
            (new_group_name, student[0])
        )

        # Если вуз в списке исключений, не создаем расписание
        if university_name in exempt_universities or faculty_name in exempt_universities:
            continue

        for interval in all_free_intervals[group_name]:
            if lesson_count >= max_lessons_per_group:
                break

            if interval.lesson_date not in used_intervals:
                used_intervals[interval.lesson_date] = set()

            # Проверяем, пересекается ли текущий интервал с уже занятыми на ту же дату
            if not any(is_overlapping(interval.lesson_interval, used_interval) for used_interval in
                       used_intervals[interval.lesson_date]):
                # Проверяем, занимается ли группа в этот день
                if interval.lesson_date in group_days[new_group_name]:
                    continue

                used_intervals[interval.lesson_date].add(interval.lesson_interval)
                group_days[new_group_name].add(interval.lesson_date)
                db.execute_query(
                    '''
                    INSERT INTO lesson_intervals_for_ck (group_name, lesson_interval, lesson_date, is_busy)
                    VALUES (%s, %s, %s, FALSE)
                    ''',
                    (new_group_name, interval.lesson_interval, interval.lesson_date)
                    # Используем интервал 7-8 для этих студентов
                )
                lesson_count += 1


if __name__ == "__main__":
    t = time.time()
    db = PostgreSQLDatabase()
    db.connect()

    students = fetch_other_students(db)
    students_by_program = defaultdict(list)
    for student in students:
        students_by_program[student[5]].append(student)

    all_free_intervals = fetch_all_free_intervals(db)
    create_new_groups(db, students_by_program, all_free_intervals, group_size_limit=22)

    db.disconnect()
    print("--- %s seconds --- group_maker_for_other_universities" % (time.time() - t))
