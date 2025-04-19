from tkinter import filedialog, messagebox
import json
import os
import re

def load_json_file(file_path):
    """Загружает данные из JSON файла."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_translated_data(data, translated_data, current_directory, selected_file_label):
    """Сохраняет переведенные данные в файл."""
    if not current_directory:
        messagebox.showerror("Ошибка", "Директория не выбрана.")
        return

    selected_file = selected_file_label.cget("text").replace("Выбранный файл: ", "").strip()
    if not selected_file or selected_file == "Файл не выбран":
        messagebox.showerror("Ошибка", "Файл не выбран.")
        return

    original_name, ext = os.path.splitext(selected_file)
    new_file_name = f"{original_name}_translate{ext}"
    save_path = os.path.join(current_directory, new_file_name)

    try:
        with open(save_path, "w", encoding="utf-8") as file:
            json.dump(translated_data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Успех", f"Переведённый файл сохранён как {new_file_name}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

def choose_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        return file_path
    else:
        messagebox.showerror("Ошибка", "Не выбран файл")
        return None

def choose_directory():
    directory = filedialog.askdirectory()
    if directory:
        return directory
    else:
        messagebox.showerror("Ошибка", "Не выбрана директория")
        return None

def generate_translated_filename(directory):
    """
    Генерирует уникальное имя файла в формате XX_translate.json в указанной директории.
    """
    # Получаем список файлов в директории
    files = os.listdir(directory)
    
    # Ищем файлы с шаблоном "XX_translate.json"
    pattern = re.compile(r"(\d+)_translate\.json")
    numbers = []
    
    for file in files:
        match = pattern.match(file)
        if match:
            numbers.append(int(match.group(1)))
    
    # Находим следующее число
    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1
    
    # Форматируем число с ведущим нулем (например, 01, 02, ...)
    filename = f"{next_number:02d}_translate.json"
    return os.path.join(directory, filename)

def import_translations(file_path, data, translated_data):
    """Импортирует переводы из другого JSON файла."""
    new_data = load_json_file(file_path)
    for key, value in new_data.items():
        if key in data:
            translated_data[key] = value

def sort_keys(data, translated_data):
    """Сортирует ключи в данных."""
    sorted_keys = sorted(data.keys(), key=lambda k: (k in translated_data, k))
    return {key: data[key] for key in sorted_keys}