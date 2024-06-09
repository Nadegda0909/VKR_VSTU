create table public.groups_vstu_and_others
(
    group_name varchar(100) not null
        constraint groups_pkey
            primary key,
    faculty    varchar(100),
    course     integer,
    program    varchar(100) not null
);

create table public.learning_dates
(
    date     date    not null
        constraint learning_dates_pk
            primary key,
    week_day integer not null
        constraint week_day_check
            check ((week_day >= 1) AND (week_day <= 6)),
    week_num integer not null
        constraint week_num_check
            check ((week_num >= 1) AND (week_num <= 2))
);

create table public.lessons_for_vstu
(
    lesson_id    integer default nextval('lessons_lesson_id_seq'::regclass) not null
        constraint lessons_pkey
            primary key,
    group_name   varchar(100)                                               not null
        constraint lessons_group_name_fkey
            references public.groups_vstu_and_others,
    lesson_order integer                                                    not null
        constraint lessons_lesson_order_check
            check ((lesson_order >= 1) AND (lesson_order <= 6)),
    is_busy      boolean                                                    not null,
    lesson_date  date                                                       not null
        constraint lessons_date_fk
            references public.learning_dates
);

create table public.students_ck
(
    id                  integer default nextval('students_id_seq'::regclass) not null
        constraint students_pkey
            primary key,
    full_name           varchar(255),
    university_name     varchar(255),
    faculty             varchar(255),
    oop_group_2023_2024 varchar(255)
        constraint students_ck_groups_group_name_fk
            references public.groups_vstu_and_others,
    ck_program          varchar(255),
    ck_group            varchar(255)
);

create table public.lesson_intervals_for_vstu
(
    id              integer default nextval('lesson_intervals_id_seq'::regclass) not null
        constraint lesson_intervals_for_vstu_pk
            primary key,
    group_name      varchar(100)                                                 not null
        constraint lesson_groups_group_name_fkey
            references public.groups_vstu_and_others,
    lesson_interval varchar(3)                                                   not null,
    lesson_date     date                                                         not null
        constraint lesson_groups_lesson_date_fkey
            references public.learning_dates,
    is_busy         boolean                                                      not null
);

create table public.lesson_intervals_for_ck
(
    id              integer default nextval('new_lesson_intervals_id_seq'::regclass) not null
        constraint new_lesson_intervals_pkey
            primary key,
    group_name      varchar(100)                                                     not null,
    lesson_interval varchar(3)                                                       not null,
    lesson_date     date                                                             not null
        constraint lesson_intervals_for_ck_dates_date_fk
            references public.learning_dates,
    is_busy         boolean                                                          not null
);
