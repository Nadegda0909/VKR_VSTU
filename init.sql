create table public.groups
(
    group_name varchar(100) not null
        primary key,
    faculty    varchar(100) not null,
    course     integer      not null,
    program    varchar(100) not null
);

create table public.dates
(
    date     date    not null
        constraint dates_pk
            primary key,
    week_day integer not null
        constraint week_day_check
            check ((week_day >= 1) AND (week_day <= 6)),
    week_num integer not null
        constraint week_num_check
            check ((week_num >= 1) AND (week_num <= 2))
);

create table public.lessons
(
    lesson_id    serial
        primary key,
    group_name   varchar(100) not null
        references public.groups,
    lesson_order integer      not null
        constraint lessons_lesson_order_check
            check ((lesson_order >= 1) AND (lesson_order <= 6)),
    is_busy      boolean      not null,
    lesson_date  date         not null
        constraint lessons_date_fk
            references public.dates
);

create table public.students
(
    id                  serial
        primary key,
    full_name           varchar(255),
    university_name     varchar(255),
    faculty             varchar(255),
    oop_group_2023_2024 varchar(255),
    ck_program          varchar(255),
    ck_group            varchar(255)
);

create table public.lesson_intervals
(
    id              serial
        constraint lesson_intervals_pk
            primary key,
    group_name      varchar(100) not null
        constraint lesson_groups_group_name_fkey
            references public.groups,
    lesson_interval varchar(3)   not null,
    lesson_date     date         not null
        constraint lesson_groups_lesson_date_fkey
            references public.dates,
    is_busy         boolean      not null
);

create table public.new_lesson_intervals
(
    id              serial
        primary key,
    group_name      varchar(100) not null,
    lesson_interval varchar(3)   not null,
    lesson_date     date         not null
        constraint new_lesson_intervals_dates_date_fk
            references public.dates,
    is_busy         boolean      not null
);