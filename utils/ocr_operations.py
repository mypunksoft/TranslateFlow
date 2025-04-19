import os
import json
import cv2
import re
from paddleocr import PaddleOCR
from tkinter import messagebox

def extract_text_to_json(image_path, json_path, confidence_threshold=0.6, x_tolerance=15): #last: 0.93
    """
    Извлекает текст из изображения с использованием PaddleOCR и сохраняет его в JSON-файл.
    """
    ocr = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=True)
    result = ocr.ocr(image_path, cls=True)

    if not result or not result[0]:
        messagebox.showerror(
            "Ошибка",
            f"Нет распознанного текста в файле: {os.path.basename(image_path)}",
        )
        return

    words = []

    for line in result[0]:
        coord = line[0]
        text = line[1][0]
        confidence = line[1][1]

        if confidence < confidence_threshold:
            continue

        x1, y1 = int(coord[0][0]), int(coord[0][1])
        x2, y2 = int(coord[2][0]), int(coord[2][1])
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

        words.append((text, center_x, center_y, confidence))

    if not words:
        messagebox.showinfo(
            "Ошибка",
            f"Все слова в {os.path.basename(image_path)} имели низкую уверенность и были отфильтрованы.",
        )
        return

    words.sort(key=lambda w: w[1])

    grouped_sentences = []

    for text, center_x, center_y, confidence in words:
        added = False
        for group in grouped_sentences:
            ref_x = group[0][1]
            if abs(ref_x - center_x) <= x_tolerance:
                group.append((text, center_x, center_y))
                added = True
                break

        if not added:
            grouped_sentences.append([(text, center_x, center_y)])

    for group in grouped_sentences:
        group.sort(key=lambda w: w[2])

    grouped_sentences.sort(key=lambda group: group[0][2])

    sentences_json = {
        f"Text{i+1}": " ".join(word[0] for word in group)
        for i, group in enumerate(grouped_sentences)
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sentences_json, f, ensure_ascii=False, indent=4)

def visualize_text_bboxes(image_path, output_path='output.jpg', scale_factor=0.5):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')  
    img = cv2.imread(image_path)
    result = ocr.ocr(image_path, cls=True)

    if not result or not isinstance(result, list) or not result[0]:
        print(f"⚠️ OCR не дал результата для {image_path}")
        return

    for line in result[0]:
        text = line[1][0]  # Распознанный текст

        # Пропускаем знаки препинания
        if re.fullmatch(r'[\W_]+', text):
            continue  

        coord = line[0]  # Координаты текста
        x1, y1 = int(coord[0][0]), int(coord[0][1])
        x2, y2 = int(coord[2][0]), int(coord[2][1])

        # Рисуем только рамку
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)

    # Сохраняем изображение без текста
    cv2.imwrite(output_path, img)
    print(f'Изображение сохранено как {output_path}')
