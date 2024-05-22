from backend.database import PostgreSQLDatabase
from collections import defaultdict, namedtuple
from itertools import count

# Определение именованного кортежа для хранения интервалов
Interval = namedtuple('Interval', ['week_num', 'week_day', 'lesson_interval', 'lesson_date'])

# Функция для получения данных о студентах из базы данных
def fetch_students(db):
    query = '''
    SELECT id, full_name, university_name, faculty, oop_group_2023_2024, ck_program
    FROM students
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
    FROM lesson_intervals li
    JOIN groups g ON li.group_name = g.group_name
    JOIN dates d ON li.lesson_date = d.date
    WHERE li.is_busy = FALSE
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
def create_new_groups(db, students_by_program, all_free_intervals):
    group_size_limit = 20
    max_lessons_per_group = 8  # Ограничение на количество занятий
    used_intervals = defaultdict(set)  # Храним занятые интервалы по датам
    group_days = defaultdict(set)  # Храним занятые дни для каждой группы

    for program, students in students_by_program.items():
        group_counter = count(1)
        new_group_students = []
        new_group_name = f"{program}_{next(group_counter)}"

        i = 0
        while i < len(students):
            student = students[i]
            new_group_students.append(student)
            group_name = student[4].lower()

            # Добавляем всех одногруппников
            while i + 1 < len(students) and students[i + 1][4].lower() == group_name:
                i += 1
                new_group_students.append(students[i])

            if len(new_group_students) >= group_size_limit:
                # Добавляем новую группу в таблицу groups
                db.execute_query(
                    '''
                    INSERT INTO groups (group_name, faculty, course, program)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (group_name) DO NOTHING;
                    ''',
                    (new_group_name, new_group_students[0][3], 1, program)
                )

                # Распределяем занятия для новой группы
                lesson_count = 0
                for student in new_group_students:
                    free_intervals = all_free_intervals[group_name]

                    # Добавляем студента в новую группу
                    db.execute_query(
                        '''
                        INSERT INTO new_student_groups (student_id, new_group_name)
                        VALUES (%s, %s)
                        ''',
                        (student[0], new_group_name)
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
                                INSERT INTO new_lesson_intervals (group_name, lesson_interval, lesson_date, is_busy)
                                VALUES (%s, %s, %s, FALSE)
                                ''',
                                (new_group_name, interval.lesson_interval, interval.lesson_date)
                            )
                            lesson_count += 1

                # Начинаем новую группу
                new_group_name = f"{program}_{next(group_counter)}"
                new_group_students = []

            i += 1

        # Добавляем последнюю группу, если она не пустая
        if new_group_students:
            db.execute_query(
                '''
                INSERT INTO groups (group_name, faculty, course, program)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (group_name) DO NOTHING;
                ''',
                (new_group_name, new_group_students[0][3], 1, program)
            )

            lesson_count = 0
            for student in new_group_students:
                free_intervals = all_free_intervals[group_name]

                db.execute_query(
                    '''
                    INSERT INTO new_student_groups (student_id, new_group_name)
                    VALUES (%s, %s)
                    ''',
                    (student[0], new_group_name)
                )

                for interval in free_intervals:
                    if lesson_count >= max_lessons_per_group:
                        break

                    if interval.lesson_date not in used_intervals:
                        used_intervals[interval.lesson_date] = set()

                    if not any(is_overlapping(interval.lesson_interval, used_interval) for used_interval in
                               used_intervals[interval.lesson_date]):
                        if interval.lesson_date in group_days[new_group_name]:
                            continue

                        used_intervals[interval.lesson_date].add(interval.lesson_interval)
                        group_days[new_group_name].add(interval.lesson_date)
                        db.execute_query(
                            '''
                            INSERT INTO new_lesson_intervals (group_name, lesson_interval, lesson_date, is_busy)
                            VALUES (%s, %s, %s, FALSE)
                            ''',
                            (new_group_name, interval.lesson_interval, interval.lesson_date)
                        )
                        lesson_count += 1


if __name__ == "__main__":
    db = PostgreSQLDatabase()
    db.connect()
    db.truncate_table('new_student_groups')
    db.truncate_table('new_lesson_intervals')
    students = fetch_students(db)
    students_by_program = defaultdict(list)

    for student in students:
        students_by_program[student[5]].append(student)

    all_free_intervals = fetch_all_free_intervals(db)
    create_new_groups(db, students_by_program, all_free_intervals)

    db.disconnect()
