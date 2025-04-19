import tkinter as tk
import os
import re
from tkinter import filedialog, messagebox

def choose_directory():
    directory = filedialog.askdirectory()
    if directory:
        return directory
    else:
        messagebox.showerror("Ошибка", "Не выбрана директория")
        return None

def show_directory_files(directory, file_listbox, data, translated_data, left_text, status_label, update_ui, image_stats_label):
    # Очистка списка файлов
    file_listbox.delete(0, tk.END)
    
    # Список файлов JSON
    json_files = [f for f in os.listdir(directory) if f.endswith(".json")]
    for file_name in json_files:
        file_listbox.insert(tk.END, file_name)  # Добавляем файлы в file_listbox

    # Список изображений JPG и WEBP
    jpg_files = [f for f in os.listdir(directory) if f.lower().endswith(".jpg")]
    webp_files = [f for f in os.listdir(directory) if f.lower().endswith(".webp")]

    # Обновление статистики изображений
    image_stats_label.config(text=f"JPG: {len(jpg_files)}, WEBP: {len(webp_files)}")

    # Очистка данных и обновление интерфейса
    data.clear()
    translated_data.clear()
    left_text.delete(1.0, tk.END)
    update_ui()
    
def generate_translated_filename(directory):
    files = os.listdir(directory)
    pattern = re.compile(r"(\d+)_translate\.json")
    numbers = []

    for file in files:
        match = pattern.match(file)
        if match:
            numbers.append(int(match.group(1)))

    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1

    filename = f"{next_number:02d}_translate.json"
    return os.path.join(directory, filename)