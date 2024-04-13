CREATE TABLE public.groups (
    group_name VARCHAR(100) NOT NULL PRIMARY KEY,
    faculty VARCHAR(100) NOT NULL,
    course INTEGER NOT NULL,
    program VARCHAR(100) NOT NULL
);

CREATE TABLE public.dates (
    date DATE NOT NULL CONSTRAINT dates_pk PRIMARY KEY,
    week_day INTEGER NOT NULL CONSTRAINT week_day_check CHECK ((week_day >= 1) AND (week_day <= 6)),
    week_num INTEGER NOT NULL CONSTRAINT week_num_check CHECK ((week_num >= 1) AND (week_num <= 2))
);

CREATE TABLE public.lessons (
    lesson_id SERIAL PRIMARY KEY,
    group_name VARCHAR(100) NOT NULL REFERENCES public.groups,
    lesson_order INTEGER NOT NULL CONSTRAINT lessons_lesson_order_check CHECK ((lesson_order >= 1) AND (lesson_order <= 6)),
    is_busy BOOLEAN NOT NULL,
    lesson_date DATE NOT NULL CONSTRAINT lessons_date_fk REFERENCES public.dates
);

