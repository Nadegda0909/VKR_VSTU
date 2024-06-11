create table if not exists groups_vstu_and_others
(
    group_name varchar(100) not null,
    faculty    varchar(100),
    course     integer,
    program    varchar(100) not null,
    constraint groups_pkey
        primary key (group_name)
);

create table if not exists learning_dates
(
    date     date    not null,
    week_day integer not null,
    week_num integer not null,
    constraint learning_dates_pk
        primary key (date),
    constraint week_day_check
        check ((week_day >= 1) AND (week_day <= 6)),
    constraint week_num_check
        check ((week_num >= 1) AND (week_num <= 2))
);

create table if not exists lessons_for_vstu
(
    lesson_id    serial not null,
    group_name   varchar(100)                                               not null,
    lesson_order integer                                                    not null,
    is_busy      boolean                                                    not null,
    lesson_date  date                                                       not null,
    constraint lessons_pkey
        primary key (lesson_id),
    constraint lessons_group_name_fkey
        foreign key (group_name) references groups_vstu_and_others,
    constraint lessons_date_fk
        foreign key (lesson_date) references learning_dates,
    constraint lessons_lesson_order_check
        check ((lesson_order >= 1) AND (lesson_order <= 6))
);

create table if not exists students_ck
(
    id                  serial not null,
    full_name           varchar(255),
    university_name     varchar(255),
    faculty             varchar(255),
    oop_group_2023_2024 varchar(255),
    ck_program          varchar(255),
    ck_group            varchar(255),
    constraint students_pkey
        primary key (id),
    constraint students_ck_groups_group_name_fk
        foreign key (oop_group_2023_2024) references groups_vstu_and_others
);

create table if not exists lesson_intervals_for_vstu
(
    id              serial not null,
    group_name      varchar(100)                                                 not null,
    lesson_interval varchar(3)                                                   not null,
    lesson_date     date                                                         not null,
    is_busy         boolean                                                      not null,
    constraint lesson_intervals_for_vstu_pk
        primary key (id),
    constraint lesson_groups_group_name_fkey
        foreign key (group_name) references groups_vstu_and_others,
    constraint lesson_groups_lesson_date_fkey
        foreign key (lesson_date) references learning_dates
);

create table if not exists lesson_intervals_for_ck
(
    id              serial not null,
    group_name      varchar(100)                                                     not null,
    lesson_interval varchar(3)                                                       not null,
    lesson_date     date                                                             not null,
    is_busy         boolean                                                          not null,
    constraint new_lesson_intervals_pkey
        primary key (id),
    constraint lesson_intervals_for_ck_dates_date_fk
        foreign key (lesson_date) references learning_dates
);

