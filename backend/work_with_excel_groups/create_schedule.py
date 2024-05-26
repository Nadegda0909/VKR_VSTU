from backend.database import PostgreSQLDatabase
from collections import defaultdict, namedtuple
import time

# Определение именованного кортежа для хранения интервалов
Interval = namedtuple('Interval', ['week_num', 'week_day', 'lesson_interval', 'lesson_date'])


# Функция для получения всех новых групп из базы данных
def fetch_new_groups(db):
    query = '''
    SELECT DISTINCT ck_group
    FROM students
    WHERE ck_group IS NOT NULL;
    '''
    result = db.execute_query(query)
    if result:
        return [row[0] for row in result[1]]
    return []


# Функция для получения всех свободных интервалов из базы данных
def fetch_all_free_intervals(db):
    query = '''
    SELECT g.group_name, d.week_num, d.week_day, li.lesson_interval, li.lesson_date
    FROM lesson_intervals li
    JOIN groups g ON li.group_name = g.group_name
    JOIN dates d ON li.lesson_date = d.date
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


# Функция для обработки группы студентов
def process_group(db, new_group_name, free_intervals, used_intervals, group_days, max_lessons_per_group):
    if not free_intervals:
        print(f"Error: No free intervals found for group {new_group_name}")
        return

    lesson_count = 0
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


# Функция для создания расписания для новых групп
def create_schedule_for_new_groups(db, new_groups, all_free_intervals, max_lessons_per_group=5):
    used_intervals = defaultdict(set)
    group_days = defaultdict(set)

    for new_group_name in new_groups:
        lesson_count = 0

        free_intervals = []
        query = '''
        SELECT DISTINCT s.oop_group_2023_2024
        FROM students s
        WHERE s.ck_group = %s;
        '''
        original_groups = db.execute_query(query, (new_group_name,))
        if original_groups:
            for original_group in original_groups[1]:
                free_intervals.extend(all_free_intervals[original_group[0].lower()])

        if free_intervals:
            process_group(db, new_group_name, free_intervals, used_intervals, group_days, max_lessons_per_group)
        else:
            print(f"Warning: No free intervals found for new group {new_group_name}")


if __name__ == "__main__":
    t = time.time()
    db = PostgreSQLDatabase()
    db.connect()

    all_free_intervals = fetch_all_free_intervals(db)
    new_groups = fetch_new_groups(db)
    db.truncate_table('new_lesson_intervals')
    create_schedule_for_new_groups(db, new_groups, all_free_intervals)

    db.disconnect()
    print("--- %s seconds --- create_schedule" % (time.time() - t))
