from backend.database import PostgreSQLDatabase
from collections import defaultdict, namedtuple
from group_maker import fetch_all_free_intervals, is_overlapping

# Определение именованного кортежа для хранения интервалов
Interval = namedtuple('Interval', ['week_num', 'week_day', 'lesson_interval', 'lesson_date'])


# Функция для получения всех сформированных групп из базы данных
def fetch_all_groups(db):
    query = '''
    SELECT new_group_name
    FROM new_student_groups
    GROUP BY new_group_name
    '''
    result = db.execute_query(query)
    if result:
        return [row[0] for row in result[1]]
    return []


# Функция для создания расписания для уже сформированных групп
def create_schedule_for_groups(db, all_free_intervals):
    max_lessons_per_group = 4  # Ограничение на количество занятий
    used_intervals = defaultdict(set)  # Храним занятые интервалы по датам
    group_days = defaultdict(set)  # Храним занятые дни для каждой группы

    groups = fetch_all_groups(db)
    for group in groups:
        lesson_count = 0
        for interval_group, intervals in all_free_intervals.items():
            for interval in intervals:
                if lesson_count >= max_lessons_per_group:
                    break

                if interval.lesson_date not in used_intervals:
                    used_intervals[interval.lesson_date] = set()

                # Проверяем, пересекается ли текущий интервал с уже занятыми на ту же дату
                if not any(is_overlapping(interval.lesson_interval, used_interval) for used_interval in
                           used_intervals[interval.lesson_date]):
                    # Проверяем, занимается ли группа в этот день
                    if interval.lesson_date in group_days[group]:
                        continue

                    used_intervals[interval.lesson_date].add(interval.lesson_interval)
                    group_days[group].add(interval.lesson_date)
                    db.execute_query(
                        '''
                        INSERT INTO new_lesson_intervals (group_name, lesson_interval, lesson_date, is_busy)
                        VALUES (%s, %s, %s, FALSE)
                        ''',
                        (group, interval.lesson_interval, interval.lesson_date)
                    )
                    lesson_count += 1


if __name__ == "__main__":
    db = PostgreSQLDatabase()
    db.connect()
    db.truncate_table('new_lesson_intervals')

    all_free_intervals = fetch_all_free_intervals(db)
    create_schedule_for_groups(db, all_free_intervals)

    db.disconnect()
