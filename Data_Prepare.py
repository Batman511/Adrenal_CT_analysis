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


def check_images_in_excel(image_dir, excel_file, column_d='Файл c нативной фазой', column_t='Присутствует в папке "Все картинки"'):
    """
    Функция проверяет, присутствуют ли имена картинок из папки в Excel-файле и обновляет Excel:
    - Если имя картинки найдено в столбце D, ставит 1 в столбце T.
    - Картинки, не найденные в Excel, записывает в отдельный список.

    Возвращает:
        missing_images (list): Список картинок, которые не найдены в Excel-файле.
    """

    # Проверка существования пути к папке с изображениями
    if not os.path.isdir(image_dir):
        print(f"Ошибка: Путь к папке с изображениями '{image_dir}' не существует.")
        return []

    # Проверка существования Excel-файла
    if not os.path.isfile(excel_file):
        print(f"Ошибка: Excel-файл '{excel_file}' не найден.")
        return []

    # Попытка загрузить Excel-файл
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Ошибка при открытии Excel-файла: {e}")
        return []

    # Проверка наличия столбцов
    if column_d not in df.columns or column_t not in df.columns:
        print(f"Ошибка: В Excel-файле нет столбцов '{column_d}' или '{column_t}'.")
        return []

    # Преобразуем имена картинок из столбца D в список для удобства поиска
    excel_images = df[column_d].astype(str).tolist()

    # Список картинок, которые не найдены в Excel
    missing_images = []

    # Проходим по всем картинкам в папке
    for image_name in os.listdir(image_dir):
        # Убираем расширение файла (например, .jpg или .png) для сравнения
        image_base_name = os.path.splitext(image_name)[0]

        if image_base_name in excel_images:
            # Если имя картинки найдено, ставим 1 в столбец T
            df.loc[df[column_d] == image_base_name, column_t] = 1
        else:
            # Если не найдено, добавляем в список
            missing_images.append(image_name)

    # Попытка сохранить Excel-файл
    try:
        df.to_excel(excel_file, index=False)
    except Exception as e:
        print(f"Ошибка при сохранении Excel-файла: {e}")
        return []

    return missing_images

def delete_videos(video_dir, video_list):
    """
    Удаляет видеофайлы из указанной папки по названиям, которые переданы в списке.
    """
    for video_name in video_list:
        video_path = os.path.join(video_dir, video_name)
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
                print(f"Удалено: {video_path}")
            except OSError as e:
                print(f"Ошибка при удалении {video_path}: {e}")
        else:
            print(f"Файл не найден: {video_path}")


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

def display_video(video_path, frame_skip=5, wait_key=200):
    """
    Функция для воспроизведения каждого {frame_skip} кадра видео с задержкой  {wait_key} мс.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Не удалось открыть видеофайл: {video_path}")
        return

    frame_count = 0  # Счётчик кадров
    window_name = 'Display_video'


    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break  # Конец видео

        if frame_count % frame_skip == 0:
            cv2.imshow(window_name, frame) # Отображение кадра в одном и том же окне

            # Задержка между кадрами и Остановка при нажатии клавиши 'q'
            if cv2.waitKey(wait_key) & 0xFF == ord('q'):
                break

        frame_count += 1

    # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()

# плохо работает
def display_video_with_max_contour(video_path, frame_skip=5, wait_key=400):
    """
    Функция находит максимальный контур на каждом {frame_skip} кадре,
    проводит вертикальную линию через центр контура и выводит кадры в одном окне, чтобы убедиться, что центр найден
    """

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Не удалось открыть видеофайл: {video_path}")
        return

    window_name = 'Display_video'
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Применяем размытие
            blurred = cv2.GaussianBlur(gray, (9, 9), 5)

            # Используем Canny для выделения границ
            edges = cv2.Canny(blurred, 50, 100)

            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)

                # Получаем момент для нахождения центра
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])

                    # Рисуем контур и линию на кадре
                    cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
                    cv2.line(frame, (center_x, 0), (center_x, frame.shape[0]), (255, 0, 0), 2)

            cv2.imshow(window_name, frame)

            if cv2.waitKey(wait_key) & 0xFF == ord('q'):  # 'q' для выхода
                break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

# проверяем что надпочечники на своих местах
def display_video_with_center(video_path, frame_skip=5, wait_key=200):
    """
    Функция проводит вертикальную линию через центр каждого {frame_skip} кадра для РУЧНОГО контроля того, что пациент не сместился. Выводит название файла.
    """

    file_name = os.path.splitext(os.path.basename(video_path))[0]


    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Не удалось открыть видеофайл: {video_path}")
        return

    window_name = 'Display_video'
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
            height, width, _ = frame.shape

            center_x = width // 2
            cv2.line(frame, (center_x, 0), (center_x, height), (255, 0, 0), 2)

            # Выводим название файла на видео
            cv2.putText(frame, file_name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow(window_name, frame)

            if cv2.waitKey(wait_key) & 0xFF == ord('q'): # выход
                break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
def manual_directory_check(image_dir):

    for file_name in os.listdir(image_dir):
        video_path = os.path.join(image_dir, file_name)

        if os.path.isfile(video_path) and file_name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            display_video_with_center(video_path)


# вроде норм функция для загрузки и обработки видео с уменьшением количества и размера кадров. Надо написать тестовую функцию для ее проверки
def load_videos(data_dir, target_size=(224, 224), frame_skip=5, add_third_dimension=False):
    """
      Функция загружает видео из указанной директории, обрабатывает их (уменьшает количество кадров, уменьшает размер) и
      сохраняет в виде массивов.

      Возвращает:
          videos : Массив обработанных видео.
          labels : Массив меток классов. [0 0 1]
          label_names : Список имен меток. 'left_001'
      """

    videos = []
    labels = []
    formatted_label_names = []
    label_names = os.listdir(data_dir)

    for label_name in label_names:
        label_dir = os.path.join(data_dir, label_name)
        if 'left_adrenal' in label_name:
            prefix = 'left'
        elif 'right_adrenal' in label_name:
            prefix = 'right'
        else:
            continue


        class_names = os.listdir(label_dir)
        for class_name in class_names:
            class_path = os.path.join(label_dir, class_name)
            for video_name in os.listdir(class_path):
                video_path = os.path.join(class_path, video_name)
                cap = cv2.VideoCapture(video_path)
                frames = []
                frame_count = 0
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_count % frame_skip == 0:
                        # Обрезаем изображение в зависимости от надпочечника
                        if prefix == 'left':
                            frame = frame[:, :frame.shape[1] // 2]
                        else:
                            frame = frame[:, frame.shape[1] // 2:]


                        frame = cv2.cvtColor(cv2.resize(frame, target_size), cv2.COLOR_BGR2GRAY)
                        if add_third_dimension:
                            frame = np.expand_dims(frame, axis=-1)  # Добавление канала для совместимости формы для некоторых моделей

                        frames.append(frame)
                    frame_count += 1
                cap.release()

                # Генерируем метку в виде массива из трех чисел
                class_parts = class_name.split('_')[1:]
                label = [np.uint8(int(class_parts[i])) for i in range(3)]

                # Генерируем имя метки в виде left_001 или right_001
                formatted_label_name = f"{prefix}_{''.join(class_parts)}"

                videos.append(np.array(frames, dtype=np.uint8))
                labels.append(label)
                formatted_label_names.append(formatted_label_name)

    return np.array(videos, dtype=np.uint8), np.array(labels, dtype=np.int64), formatted_label_names




if __name__ == "__main__":
    # create_folder_structure(r'C:\Users\Антон\Documents\материалы ВИШ\Диплом КТ\Adrenal CT architecture')
    # test_download_and_display_single_video(r"C:\Users\Антон\Documents\материалы ВИШ\Диплом КТ\База данных МСКТ надпочечников_MP4.xlsx", column_names=['Файл c нативной фазой'])

    video_path = r"C:\Users\Антон\Documents\материалы ВИШ\Диплом КТ\data\class02\ID5_NATIVE_SE1.mp4"
    # display_video(video_path,frame_skip=5, wait_key=200)
    # display_video_with_max_contour(video_path, frame_skip=5, wait_key=500) # не работает пока
    # display_video_with_center(video_path, frame_skip=5)

    data_dir = r'C:\Users\Антон\Documents\материалы ВИШ\Диплом КТ\Adrenal CT architecture\data'
    # videos, labels, label_names = load_videos(data_dir, target_size=(224, 224), frame_skip=5, add_third_dimension=True)
    # print(labels, label_names)


    image_dir = r'C:\Users\Антон\Documents\материалы ВИШ\Диплом КТ\Все картинки'  # Путь к папке с картинками
    excel_file = r"C:\Users\Антон\Documents\материалы ВИШ\Диплом КТ\База данных МСКТ надпочечников_MP4.xlsx"  # Путь к Excel-файлу

    # missing_images = check_images_in_excel(image_dir, excel_file)
    # # Печать картинок, которых нет в Excel
    # print("Картинки, не найденные в Excel:", missing_images)




    image_dir = r'C:\Users\Антон\Documents\материалы ВИШ\Диплом КТ\Все картинки'
    manual_directory_check(image_dir)

