# Разработка программы для интеграции и обработки расписаний ВолгГТУ

## Описание

### Система анализирует расписание ВолгГТУ и составляет расписание для Цифровой Кафедры и состоит из следующих основных компонентов:

1. [Модуль загрузки расписания](backend/work_with_excel_rasp/downloader.py):

   Пользователь может загрузить в систему расписание с сайта ВолгГТУ или со своего компьютера
2. [Модуль обработки расписания](backend/work_with_excel_rasp/parser.py):
   
   Система анализирует расписание ВолгГТУ и находит для каждой группы незанятые пары, в которые она может заниматься
3. [Модуль создания групп ЦК](backend/work_with_excel_groups):
   - Пользователь может загрузить список студентов, которые записались на Цифровую Кафедру
   - На основании списка студентов и незанятых пар, система составляет группы Цифровой кафедры
   - На основании групп Цифровой Кафедры составляется расписание Цифровой Кафедры
4. [Модуль создания Excel табличек для ЦК](backend/work_with_ck_excel_rasp)
   - Система создает Excel табличку для групп Цифровой Кафедры
   - Система создает Excel табличку для расписания Цифровой Кафедры

## Требования

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker-Compose](https://docs.docker.com/compose/install/)
- [Git](https://www.geeksforgeeks.org/how-to-install-git-on-windows-macos-and-linux/)
- [Python 3.12](https://www.python.org/downloads/)

## Архитектура проекта

- **[backend](backend)**: Серверная часть проекта, включая обработку данных и взаимодействие с базой данных.
- **[frontend](frontend)**: Веб-интерфейс для взаимодействия с пользователем.

## Установка

#### Для установки/запуска:
1. Убедитесь, что у вас установлен [Docker](https://www.docker.com/products/docker-desktop/)
и [Docker-Compose](https://docs.docker.com/compose/install/)
2. Убедитесь, что у вас установлен [Git](https://www.geeksforgeeks.org/how-to-install-git-on-windows-macos-and-linux/):
3. Клонируете репозиторий и переходите в папку с проектом
   ```shell
   git clone https://github.com/Nadegda0909/VKR_VSTU.git
   ```
   ```shell
   cd VKR_VSTU
   ```
4. Запускаете docker-compose
   ```shell
   docker-compose up -d
   ```
5. Теперь открываете в браузере [ссылку](http://localhost:8082)
   
   Данные для входа
   - логин: диплом
   - пароль: 123

# Работа с серверной частью
## Установка
1. Убедитесь, что у вас установлен [Python](https://www.python.org/downloads/) версии 3.12
2. Клонируете репозиторий и переходите в папку с проектом
   ```shell
   git clone https://github.com/Nadegda0909/VKR_VSTU.git
   ```
   ```shell
   cd VKR_VSTU
   ```
3. Создайте и активируйте виртуальное окружение
   ```shell
   # Linux:
   python3 -m venv venv
   source ./venv/bin/activate
   ```
   ```shell
   # Windows PowerShell:
   python -m venv venv
   ```
   ```shell
   # Windows PowerShell:
   .\venv\Scripts\Activate
   ```
   - Если вдруг выдало ошибку, то пропишите в терминале (в диалоге введите `Y`)
   
   ```shell
      # Windows PowerShell:
      Set-ExecutionPolicy RemoteSigned
      ```
4. Установите зависимости
   ```shell
   # Linux:
   (cd backend
   pip install -r requirements.txt)
   ```
   ```shell
   # Windows PowerShell:
   cd backend
   ```
   ```shell
   # Windows PowerShell:
   pip install -r requirements.txt
   ```
   ```shell
   # Windows PowerShell:
   cd ..
   ```
5. Установите переменную окружения PYTHONPATH
   ```shell
   # Linux:
   export PYTHONPATH=$(pwd):$PYTHONPATH
   ```
   ```shell
   # Windows PowerShell:
     $env:PYTHONPATH = (Get-Location).Path
   ```
## Тестирование
1. Поднимаем базу данных (на порту `5433`)
   ```shell
   docker-compose up -d postgres
   ```
2. Перейдите в [папку](backend/work_with_excel_rasp)
   ```shell
   cd backend/work_with_excel_rasp
   ```
3. Запустите [файл](backend/work_with_excel_rasp/parser.py) для скачивания расписания с сайта ВолгГТУ и анализа свободных пар
   ```shell
   python parser.py
   ```
   При успешном выполнении:
   - Создаются папки `downloaded_files`, `converted_files`, в которых хранятся расписание
   - В БД таблицы `groups_vstu_and_others`, `learning_dates`, `lesson_intervals_for_vstu`, `lessons_for_vstu` заполняются данными
4. Перейдите в [папку](backend/work_with_excel_groups)
   ```shell
   cd ../work_with_excel_groups
   ```
5. Запустите модуль для обработки файла со списком студентов
   (файл со списком студентов с расширением .csv предварительно нужно поместить в папке `work_with_excel_groups` (в репозитории этот файл уже есть))
   ```shell
   python group_parser.py
   ```
   При успешном выполнении:

   В БД таблицы `groups_vstu_and_others`, `students_ck` заполнятся данными
6. Запустите модуль создания групп и расписания для ЦК
   ```shell
   python group_maker.py
   ```
   ```shell
   python group_maker_for_others.py
   ```
7. (Опционально) Запустите модуль для создания только расписания, если существуют группы ЦК
   ```shell
   python create_schedule.py 
   ```
   При успешном выполнении:
   
   В БД таблица `lesson_intervals_for_ck` заполняется данными
8. Перейдите в [папку](backend/work_with_ck_excel_rasp)
   ```shell
   cd ../work_with_ck_excel_rasp
   ```
9. Запустите модуль для создания Excel файла с группами ЦК
   ```shell
   python groups_ck_creator.py
   ```
   При успешном выполнении:

   Создается файл `group_ck.xlsx` в папке `backend/work_with_ck_excel_rasp`