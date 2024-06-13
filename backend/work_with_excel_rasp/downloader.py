import os  # Импорт модуля для работы с операционной системой
import shutil
from shutil import move
from urllib.parse import urljoin  # Импорт функции для объединения URL-адресов
import time

import requests  # Импорт модуля для выполнения HTTP-запросов
from bs4 import BeautifulSoup  # Импорт модуля для парсинга HTML
from colorama import Style, Fore
from xls2xlsx import XLS2XLSX
from concurrent.futures import ProcessPoolExecutor, as_completed


def download_schedule_files(main_url='https://www.vstu.ru/student/raspisaniya/zanyatiy/',
                            output_folder='downloaded_files'):
    t = time.time()
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
            if "аспирантура" in category_output_folder.lower() or "вечерний" in category_output_folder.lower():
                continue
            # Создаем папку, если она еще не существует
            os.makedirs(category_output_folder, exist_ok=True)

        # Выводим информацию о текущей категории
        print(f"Скачиваем категорию: {link.text}")

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
                if ("1 курс" in file_name.lower() or "1курс" in file_name.lower() or "вечерники" in file_name.lower() or
                        "вмцэ" in file_name.lower()):
                    continue
                file_response = requests.get(file_url)  # Выполнение GET-запроса для скачивания файла

                # Сохраняем файл на диск
                with open(file_name, 'wb') as file:  # Открываем файл для записи в бинарном режиме
                    file.write(file_response.content)  # Записываем содержимое файла на диск

                # Выводим информацию о скачанном файле
                print(f"Скачан файл: {file_name}")

    print(f"{Fore.GREEN}Загрузка завершена. {Style.RESET_ALL}")
    print("--- %s seconds --- downloader" % (time.time() - t))


def convert_file(file_info):
    input_file_path, new_root = file_info
    file_name, file_extension = os.path.splitext(os.path.basename(input_file_path))

    if file_extension.lower() == '.xls':
        output_file_path = os.path.join(new_root, f"{file_name}.xlsx")
        x2x = XLS2XLSX(input_file_path)
        x2x.to_xlsx(output_file_path)
        return f"Конвертирован файл: {input_file_path.split('/')[-1]} -> {output_file_path.split('/')[-1]}"
    elif file_extension.lower() == '.xlsx':
        output_file_path = os.path.join(new_root, os.path.basename(input_file_path))
        move(input_file_path, output_file_path)
        return f"Перемещен файл: {input_file_path.split('/')[-1]}"
    else:
        return None


def convert_xls_to_xlsx(input_folder="downloaded_files", output_folder="converted_files"):
    t = time.time()
    file_infos = []

    for root, dirs, files in os.walk(input_folder):
        new_root = os.path.join(output_folder, os.path.relpath(root, input_folder))
        os.makedirs(new_root, exist_ok=True)

        for file in files:
            input_file_path = os.path.join(root, file)
            file_infos.append((input_file_path, new_root))

    # Используем все доступные ядра процессора
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(convert_file, file_info): file_info for file_info in file_infos}
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(result)

    print(f"{Fore.GREEN}Конвертация завершена. {Style.RESET_ALL}")
    print("--- %s seconds --- convertor" % (time.time() - t))


def delete_files_and_download_files():
    items = os.listdir()
    folders = [item for item in items if os.path.isdir(item) and "__" not in item]
    for folder in folders:
        try:
            shutil.rmtree(folder)
        except OSError as e:
            print(f'{Fore.RED}Ошибка при удалении папки {folder} {e} {Style.RESET_ALL}')
    download_schedule_files()
    convert_xls_to_xlsx()


if __name__ == "__main__":
    delete_files_and_download_files()
