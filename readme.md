# Диплом

## Обработка расписания ВолгГТУ и создание расписание цифровой кафедры

### Основные папки

* [app](app)

  Здесь находится само приложение

* [client](app%2Fclient)
  Здесь будет backend и frontend для веба
    
  Самый важный тут файл - [app.py](web%2Fapp.py), в нем происходит запуск всего приложения

  Чтобы запустить веб-приложение, используйте команду:
  ```commandline
  uvicorn app.client.app:app
  ```
* [work_with_files](app%2Fserver%2Fwork_with_files)

  Здесь происходит работа с excel файлами, а именно:
  1. Скачивание xls и xlsx файлов
  2. Преобразование xls в xlsx файлы
  3. Обработка xlsx файлов, то есть занесение данных в БД
  
* [docker](docker)
  
  Тут работа с докером. Разворачиваем базу данных.

#### Коротко о всех остальных файлах
* [requirements.txt](frontend/requirements.txt)

  Тут хранятся все нужные для проекта зависимости

  Можно быстро их установить командой:
  ```commandline
  pip install -r requirements.txt
  ```

##### Полезная информация
Так как мы тут используем БД, считаю важным рассказать о ней.

Используем мы PostgreSQL c вот такой структурой данных:

#### ER-диаграмма
```mermaid
erDiagram
    groups ||--o{ lessons : "group_name"
    dates ||--o{ lessons : "lesson_date"
```
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
