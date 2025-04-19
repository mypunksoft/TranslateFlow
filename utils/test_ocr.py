import os
import json
import random
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from paddleocr import PaddleOCR
from tkinter import messagebox


def extract_text_to_json(image_path, json_path, confidence_threshold=0.6, x_tolerance=15):
    """
    Извлекает текст из изображения с использованием PaddleOCR и сохраняет его в JSON-файл.
    Возвращает список слов для визуализации кластеров.
    """
    ocr = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=True)
    result = ocr.ocr(image_path, cls=True)

    if not result or not result[0]:
        messagebox.showerror("Ошибка", f"Нет распознанного текста в файле: {os.path.basename(image_path)}")
        return None

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
        messagebox.showinfo("Ошибка", f"Все слова в {os.path.basename(image_path)} имели низкую уверенность.")
        return None

    # Группировка по X
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

    return words


def visualize_word_clusters(image_path, words, eps=20):
    """
    Визуализирует кластеры слов на изображении с помощью DBSCAN.
    """
    coords = np.array([[y, x] for _, x, y, _ in words])
    clustering = DBSCAN(eps=eps, min_samples=1).fit(coords)

    labels = clustering.labels_
    num_clusters = len(set(labels))
    colors = {
        label: (random.random(), random.random(), random.random())
        for label in set(labels)
    }

    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(12, 10))
    plt.imshow(img_rgb)
    ax = plt.gca()

    for label, (text, x, y, _) in zip(labels, words):
        color = colors[label]
        ax.text(
            x, y, text,
            fontsize=10,
            color=color,
            bbox=dict(facecolor='white', edgecolor=color, boxstyle='round,pad=0.3')
        )
        ax.plot(x, y, 'o', color=color, markersize=5)

    plt.title(f"DBSCAN clustering (eps={eps}, clusters={num_clusters})")
    plt.axis('off')
    plt.tight_layout()
    plt.show()


# Пример использования:
if __name__ == "__main__":
    image_path = "B://gth//Honey Blonde ~Himawari~//18.jpg"     # <-- путь к изображению
    json_path = "output.json"      # <-- путь для сохранения JSON

    words = extract_text_to_json(image_path, json_path)

    if words:
        visualize_word_clusters(image_path, words)
