from backend.database import PostgreSQLDatabase
from collections import defaultdict, namedtuple
from itertools import count
import time

# Определение именованного кортежа для хранения интервалов
Interval = namedtuple('Interval', ['week_num', 'week_day', 'lesson_interval', 'lesson_date'])


# Функция для получения данных о студентах из базы данных
def fetch_students(db):
    query = '''
    SELECT id, full_name, university_name, faculty, oop_group_2023_2024, ck_program
    FROM students_ck
    WHERE university_name = 'ВолгГТУ' AND LOWER(faculty) NOT LIKE '%иаис%'
    ORDER BY oop_group_2023_2024;
    '''
    result = db.execute_query(query)
    if result:
        return result[1]
    return []


# Функция для получения всех свободных интервалов из базы данных
def fetch_all_free_intervals(db):
    query = '''
    SELECT g.group_name, d.week_num, d.week_day, li.lesson_interval, li.lesson_date
    FROM lesson_intervals_for_vstu li
    JOIN groups_vstu_and_others g ON li.group_name = g.group_name
    JOIN learning_dates d ON li.lesson_date = d.date
    WHERE li.is_busy = FALSE
    ORDER BY d.week_num, d.week_day, li.lesson_interval, li.lesson_date;
    '''
    result = db.execute_query(query)
    if result:
        intervals = defaultdict(list)
        for row in result[1]:
            group_name, week_num, week_day, lesson_interval, lesson_date = row
            if lesson_interval in ['1-2', '3-4', '5-6']:  # Используем только эти интервалы
                intervals[group_name].append(Interval(week_num, week_day, lesson_interval, lesson_date))
        return intervals
    return defaultdict(list)


# Функция для проверки пересечения интервалов
def is_overlapping(interval1, interval2):
    start1, end1 = map(int, interval1.split('-'))
    start2, end2 = map(int, interval2.split('-'))
    return not (end1 <= start2 or end2 <= start1)


# Функция для создания новых групп и добавления данных в новые таблицы
def create_new_groups(db, students_by_program, all_free_intervals, group_size_limit, max_lessons_per_group=5):
    used_intervals = defaultdict(set)  # Храним занятые интервалы по датам
    group_days = defaultdict(set)  # Храним занятые дни для каждой группы

    # Обрабатываем каждую программу обучения отдельно
    for program, students in students_by_program.items():
        group_counter = count(1)
        original_groups = defaultdict(list)

        # Группируем студентов по их исходным группам
        for student in students:
            original_groups[student[4]].append(student)

        current_group = []
        # Обрабатываем каждую исходную группу
        for original_group, group_students in original_groups.items():
            # Проверяем, можно ли добавить студентов в текущую группу без превышения лимита
            if len(current_group) + len(group_students) <= group_size_limit:
                current_group.extend(group_students)
            else:
                # Создаем новую группу и обрабатываем текущую группу студентов
                new_group_name = f"{program}_{next(group_counter)}"
                process_group(db, new_group_name, current_group, all_free_intervals, used_intervals, group_days,
                              max_lessons_per_group)
                current_group = group_students

        # Обрабатываем оставшихся студентов в последней группе
        if current_group:
            new_group_name = f"{program}_{next(group_counter)}"
            process_group(db, new_group_name, current_group, all_free_intervals, used_intervals, group_days,
                          max_lessons_per_group)


# Функция для обработки группы студентов
def process_group(db, new_group_name, students, all_free_intervals, used_intervals, group_days, max_lessons_per_group):

    lesson_count = 0
    for student in students:
        group_name = student[4].lower()
        free_intervals = all_free_intervals[group_name]

        # Обновляем студента, присваивая ему новую группу
        db.execute_query(
            '''
            UPDATE students_ck
            SET ck_group = %s
            WHERE id = %s;
            ''',
            (new_group_name, student[0])
        )

        for interval in free_intervals:
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
                )
                lesson_count += 1


def run():
    t = time.time()
    db = PostgreSQLDatabase()
    db.connect()
    minims = []
    all_free_intervals = fetch_all_free_intervals(db)
    for group_limit in range(20, 25 + 1):
        db.truncate_table('lesson_intervals_for_ck')
        students = fetch_students(db)
        students_by_program = defaultdict(list)
        for student in students:
            students_by_program[student[5]].append(student)
        create_new_groups(db, students_by_program, all_free_intervals, group_limit)
        minims.append(db.execute_query('''
        SELECT MIN(group_size) AS min_group_size
        FROM (
            SELECT ck_group, COUNT(id) AS group_size
            FROM students_ck
            GROUP BY ck_group
        ) AS group_counts;
        '''))
    # Находим наилучший лимит размера группы
    best_limit = minims.index(max(minims))
    db.truncate_table('lesson_intervals_for_ck')
    students = fetch_students(db)
    students_by_program = defaultdict(list)
    for student in students:
        students_by_program[student[5]].append(student)
    create_new_groups(db, students_by_program, all_free_intervals, 20 + best_limit)
    db.disconnect()
    print("--- %s seconds --- group_maker" % (time.time() - t))


if __name__ == "__main__":
    run()
