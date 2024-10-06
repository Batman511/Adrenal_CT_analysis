import os
import pandas as pd
import requests
import cv2
import numpy as np

def create_folder_structure(base_path:str) -> None:
    """
    Создает иерархию папок для хранения mp4-файлов

    Структура папок:
    base_path/
        └── data/
            ├── left_adrenal/
            │   ├── class_0_0_0/
            │   ├── class_0_0_1/
            │   ├── class_0_1_0/
                ...
            │   └── class_1_1_1/
            └── right_adrenal/
                ├── class_0_0_0/
                ├── class_0_0_1/
                ├── class_0_1_0/
                ...
                └── class_1_1_1/
    """

    class_combinations = [
        'class_0_0_0', 'class_0_0_1', 'class_0_1_0', 'class_0_1_1',
        'class_1_0_0', 'class_1_0_1', 'class_1_1_0', 'class_1_1_1'
    ]
    locations = ['left_adrenal', 'right_adrenal']

    for location in locations:
        for class_combination in class_combinations:
            folder_path = os.path.join(base_path, 'data', location, class_combination)
            os.makedirs(folder_path, exist_ok=True)

    print(f"Структура папок успешно создана в: {os.path.join(base_path, 'data')}")

# С этим пока проблема. Не может загрузить файл по ссылке, с API Яндекс.Диска тоже не вышло.
def test_download_and_display_single_video(excel_file, column_names):
    """
    Функция для тестирования: загружает и отображает видеофайл с Яндекс.Диска по ссылке из excel-файла.
    """

    df = pd.read_excel(excel_file)
    row = df.iloc[1]
    base_link = row['Местоположение файлов']

    for col_name in column_names:
        file_name = f"{row[col_name]}.mp4"
        full_video_link = f"{base_link}/{file_name}"  # Полная ссылка
        print(f"Полная ссылка на видео: {full_video_link}")

        # Загрузка видео
        try:
            print(f"Загрузка файла: {file_name}")
            response = requests.get(full_video_link, stream=True)

            if response.status_code == 200:
                # Сохранение загруженного видео во временный файл
                temp_file = 'temp_video.mp4'
                with open(temp_file, 'wb') as f:
                    f.write(response.content)

                file_size = os.path.getsize(temp_file)
                print(f"Размер загруженного файла: {file_size} байт")

                if file_size == 0:
                    print(f"Ошибка: загруженный файл {file_name} пуст.")
                    continue

                # Открываем временный видеофайл и показываем первый кадр
                cap = cv2.VideoCapture(temp_file)
                if not cap.isOpened():
                    print(f"Не удалось открыть видеофайл: {temp_file}")
                    continue

                ret, frame = cap.read()
                if ret:
                    cv2.imshow(f'Первый кадр видео: {file_name}', frame)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                else:
                    print(f"Не удалось прочитать первый кадр из видео: {file_name}")

                # Освобождаем ресурсы
                cap.release()
            else:
                print(f"Ошибка при загрузке файла: {response.status_code}")
                continue
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            continue



if __name__ == "__main__":
    # create_folder_structure(r'C:\Users\Антон\Documents\материалы ВИШ\Диплом КТ\Adrenal CT architecture')

    # test_download_and_display_single_video(r"C:\Users\Антон\Documents\материалы ВИШ\Диплом КТ\База данных МСКТ надпочечников_MP4.xlsx", column_names=['Файл c нативной фазой'])




