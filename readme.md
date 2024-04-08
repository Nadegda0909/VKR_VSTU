# Диплом

## Обработка расписания ВолгГТУ и создание расписание цифровой кафедры

### Основные папки

* [web](web)

  Здесь будет backend и frontend для веба
    
  Самый важный тут файл - [app.py](web%2Fapp.py), в нем происходит запуск всего приложения

  Чтобы запустить веб-приложение, используйте команду:
  ```commandline
  uvicorn web.app:app
  ```
* [work_with_files](work_with_files)

  Здесь происходит работа с excel файлами, а именно:
  1. Скачивание xls и xlsx файлов
  2. Преобразование xls в xlsx файлы
  3. Обработка xlsx файлов, то есть занесение данных в БД

#### Коротко о всех остальных файлах
* [requirements.txt](requirements.txt)

  Тут хранятся все нужные для проекта зависимости

  Можно быстро их установить командой:
  ```commandline
  pip install -r requirements.txt
  ```

##### Полезная информация
Так как мы тут используем БД, считаю важным рассказать о ней.

Используем мы PostgreSQL c вот такой структурой данных:
#### dates
|    date    | week_day | week_num |
|:----------:|:--------:|:--------:|
| 2024-05-28 |    2     |    2     |
| 2024-03-06 |    3     |    2     | 

#### groups
| group_name | faculty | course |
|:----------:|:-------:|:------:|
|  ивт-160   |  ФЭВТ   |   1    |
|  прин-168  |  ФЭВТ   |   1    |

#### lessons

| lesson_id | group_name | lesson_order | is_busy | lesson_date |
|-----------|:----------:|:------------:|:-------:|:-----------:|
| 1         |  ивт-160   |      1       |  false  | 2024-02-12  |
| 10        |  ивт-160   |      2       |  true   | 2024-02-12  |


```mermaid
classDiagram
direction BT
class dates {
   integer week_day
   integer week_num
   date date
}
class groups {
   varchar(100) faculty
   integer course
   varchar(100) group_name
}
class lessons {
   varchar(100) group_name
   integer lesson_order
   boolean is_busy
   date lesson_date
   integer lesson_id
}
lessons  -->  dates : lesson_date
lessons  -->  groups : group_name
```


