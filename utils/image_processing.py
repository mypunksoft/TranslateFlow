import os
from PIL import Image
import cv2
import numpy as np
from tkinter import messagebox
from utils.ocr_operations import visualize_text_bboxes

def convert_webp_to_jpg(directory, progress_bar, update_ui=None, left_text=None, data=None, translated_data=None, status_label=None, file_listbox=None, image_stats_label=None):
    """
    Конвертирует все файлы .webp в указанной директории в .jpg.
    """
    # Получаем список файлов .webp
    webp_files = [f for f in os.listdir(directory) if f.lower().endswith(".webp")]
    total_files = len(webp_files)

    if total_files == 0:
        messagebox.showinfo("Информация", "WEBP-файлы не найдены.")
        return

    # Инициализация прогресс-бара
    progress_bar["value"] = 0
    progress_bar.pack(side="bottom", pady=10)

    for i, filename in enumerate(webp_files):
        webp_path = os.path.join(directory, filename)
        jpg_path = os.path.join(directory, filename.rsplit(".", 1)[0] + ".jpg")

        try:
            # Конвертация файла
            with Image.open(webp_path) as img:
                img.convert("RGB").save(jpg_path, "JPEG", quality=95)
            os.remove(webp_path)  # Удаляем оригинальный .webp файл
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при конвертации файла {filename}: {e}")
            continue

        # Обновление прогресс-бара
        progress = (i + 1) / total_files * 100
        progress_bar["value"] = progress
        progress_bar.update_idletasks()

    # Скрытие прогресс-бара
    progress_bar.pack_forget()

    # Обновление интерфейса через метод update_ui, если он передан
    if update_ui:
        update_ui()

    messagebox.showinfo("Успех", "Конвертация завершена.")    
    
def extract_text_from_image(image_path, ocr_model):
    result = ocr_model.ocr(image_path, cls=True)
    return result

def process_image(image_path, ocr_model):
    extracted_text = extract_text_from_image(image_path, ocr_model)
    # Further processing can be done here
    return extracted_text

def save_image(image, path):
    image.save(path)

def fill_green_squares_with_white(image_path, output_path):
    # Загружаем изображение
    image = cv2.imread(image_path)

    if image is None:
        print("Ошибка: изображение не найдено!")
        return

    # Преобразуем изображение в пространство цветности HSV (это удобнее для выделения цвета)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Определяем диапазон для зеленого цвета в HSV
    lower_green = np.array([40, 50, 50])  # Нижний порог для зеленого
    upper_green = np.array([90, 255, 255])  # Верхний порог для зеленого

    # Создаем маску для зеленого цвета
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Находим контуры (границы объектов на маске)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Проходим по найденным контурам
    for idx, contour in enumerate(contours):
        # Получаем минимальный ограничивающий прямоугольник для каждого контура
        x, y, w, h = cv2.boundingRect(contour)

        # Создаем маску для области внутри найденного прямоугольникаф
        region = image[y:y+h, x:x+w]

        # Проверяем, что все пиксели внутри прямоугольника являются черными, белыми или оттенками серого
        if np.all(np.logical_or(np.logical_and(region >= 0, region <= 255), region == 0)):
            # Заливаем белым цветом
            image[y:y+h, x:x+w] = (255, 255, 255)

    # Сохраняем изображение с залитыми квадратами
    cv2.imwrite(output_path, image)
    print(f"Процесс завершен. Изображение сохранено в {output_path}")

def process_images_from_folder(input_folder):
    # Проходим по всем файлам в папке
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        # Пропускаем файл '01.jpg'
        if filename == "01.jpg":
            print("Игнорируем файл 01.jpg")
            continue

        if filename.endswith(('.jpg', '.png', '.jpeg')):  # Проверяем расширение файла
            print(f"Обрабатываем файл: {filename}")

            # Шаг 1: Применение OCR для выделения текста
            output_path_ocr = os.path.join(input_folder, f"ocr_{filename}")
            visualize_text_bboxes(file_path, output_path_ocr)

            # Шаг 2: Применение заливки зеленых квадратов
            output_path_filled = os.path.join(input_folder, f"filled_{filename}")
            fill_green_squares_with_white(output_path_ocr, output_path_filled)

            # Удаляем временный файл с результатами OCR
            if os.path.exists(output_path_ocr):
                os.remove(output_path_ocr)
                print(f"Удален временный файл {output_path_ocr}")
