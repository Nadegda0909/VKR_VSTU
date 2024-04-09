import os  # Импорт модуля для работы с операционной системой
import requests  # Импорт модуля для выполнения HTTP-запросов
from bs4 import BeautifulSoup  # Импорт модуля для парсинга HTML
from urllib.parse import urljoin  # Импорт функции для объединения URL-адресов
from shutil import move
from xls2xlsx import XLS2XLSX


def download_schedule_files(main_url='https://www.vstu.ru/student/raspisaniya/zanyatiy/',
                            output_folder='downloaded_files'):
    """
    Функция для скачивания файлов расписания с указанной страницы.

    Аргументы:
    \n
    main_url (str): URL главной страницы с расписанием. По умолчанию - 'https://vstu.ru/student/raspisaniya/zanyatiy/'.
    \n
    output_folder (str): Папка для сохранения скачанных файлов. По умолчанию - 'downloaded_files'.
    """
    # Получаем HTML-код страницы
    response = requests.get(main_url)  # Выполнение GET-запроса к главной странице
    soup = BeautifulSoup(response.text, 'html.parser')  # Создание объекта BeautifulSoup для парсинга HTML

    # Создаем главную папку для сохранения файлов, если она еще не существует
    os.makedirs(output_folder, exist_ok=True)

    # Ищем все ссылки на факультеты, бакалавриат, магистратуру и аспирантуру
    all_links = soup.select('.units-row.content h4 + ul a, .units-row.content h3 + ul a')

    # Обходим все найденные ссылки
    for link in all_links:
        # Формируем полный URL для текущей категории
        category_url = urljoin(main_url, link['href'])

        if 'h3' in link.find_parents():
            # Если ссылка находится внутри h3, создаем папку в основной папке
            category_output_folder = os.path.join(output_folder, link.text)
            # Создаем папку, если она еще не существует
            os.makedirs(category_output_folder, exist_ok=True)
        else:
            # Если ссылка находится внутри h4, создаем папку в соответствующей папке категории
            category_output_folder = os.path.join(output_folder, link.find_previous('h3').text, link.text)
            if "Аспирантура" in category_output_folder or "Вечерний" in category_output_folder:
                continue
            # Создаем папку, если она еще не существует
            os.makedirs(category_output_folder, exist_ok=True)

        # Выводим информацию о текущей категории
        print(f"Обрабатываем категорию: {link.text}")

        # Получаем HTML-код страницы текущей категории
        category_response = requests.get(category_url)  # Выполнение GET-запроса к странице категории
        category_soup = BeautifulSoup(category_response.text,
                                      'html.parser')  # Создание объекта BeautifulSoup для парсинга HTML

        # Ищем все ссылки на файлы .xls и .xlsx
        for file_link in category_soup.find_all('a', href=True):
            file_url = urljoin(category_url, file_link['href'])  # Формируем полный URL для скачивания файла

            if file_url.endswith('.xls') or file_url.endswith('.xlsx'):
                # Скачиваем файл
                file_name = os.path.join(category_output_folder,
                                         os.path.basename(file_url))  # Формируем путь для сохранения файла
                if "1 курс" in file_name:
                    continue
                file_response = requests.get(file_url)  # Выполнение GET-запроса для скачивания файла

                # Сохраняем файл на диск
                with open(file_name, 'wb') as file:  # Открываем файл для записи в бинарном режиме
                    file.write(file_response.content)  # Записываем содержимое файла на диск

                # Выводим информацию о скачанном файле
                # print(f"Скачан файл: {file_name}")

    print("Загрузка завершена.")


def convert_xls_to_xlsx(input_folder="downloaded_files", output_folder="converted_files"):
    """
    Конвертирует все файлы формата XLS в XLSX и перемещает все файлы формата XLSX в указанной папке.

    Аргументы:
    input_folder (str): Путь к папке с исходными файлами.
    output_folder (str): Путь к папке для сохранения конвертированных файлов.
    """
    # Проходимся по всем файлам и поддиректориям в папке input_folder
    for root, dirs, files in os.walk(input_folder):
        # Формируем путь к поддиректории в новой папке
        new_root = os.path.join(output_folder, os.path.relpath(root, input_folder))

        # Создаем поддиректорию в новой папке, если она еще не существует
        os.makedirs(new_root, exist_ok=True)

        # Перебираем все файлы в текущей директории
        for file in files:
            # Получаем полный путь к исходному файлу
            input_file_path = os.path.join(root, file)

            # Определяем имя файла без расширения исходного формата
            file_name, file_extension = os.path.splitext(file)

            if file_extension.lower() == '.xls':
                # Если файл XLS, то конвертируем его в формат XLSX
                output_file_path = os.path.join(new_root, f"{file_name}.xlsx")
                x2x = XLS2XLSX(input_file_path)
                x2x.to_xlsx(output_file_path)
                # Выводим информацию о конвертированном файле
                # print(f"Конвертирован файл: {input_file_path} -> {output_file_path}")
            elif file_extension.lower() == '.xlsx':
                # Если файл XLSX, просто перемещаем его в новую папку
                output_file_path = os.path.join(new_root, file)
                move(input_file_path, output_file_path)
                # Выводим информацию о перемещенном файле
                # print(f"Перемещен файл: {input_file_path} -> {output_file_path}")
    print("Конвертация завершена")
