import os
import json
from tkinter import messagebox
from utils.ocr_operations import extract_text_to_json

def load_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {e}")
        return {}

def save_translated_data(data, output_file_path):
    try:
        with open(output_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo(
            "Успех", f"Переведённый файл сохранён как {output_file_path}"
        )
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

def create_json_files(current_directory, create_progress_window, update_progress, close_progress_window, update_ui):
    """Создает JSON файлы для всех JPG в указанной директории."""
    if not current_directory:
        messagebox.showerror("Ошибка", "Директория не выбрана.")
        return

    jpg_files = [f for f in os.listdir(current_directory) if f.lower().endswith(".jpg")]
    if not jpg_files:
        messagebox.showinfo("Информация", "JPG-файлы не найдены.")
        return

    total_files = len(jpg_files)
    create_progress_window()  # Создаем окно прогресса

    try:
        for i, filename in enumerate(jpg_files):
            jpg_path = os.path.join(current_directory, filename)
            json_path = os.path.join(current_directory, filename.rsplit(".", 1)[0] + ".json")
            try:
                extract_text_to_json(jpg_path, json_path)  # Обработка файла
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обработке файла {filename}: {e}")
                continue

            # Обновление прогресса
            progress = (i + 1) / total_files * 100
            update_progress(progress)

        messagebox.showinfo("Успех", "JSON-файлы успешно созданы.")
        update_ui()  # Обновляем интерфейс после завершения
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при создании JSON-файлов: {e}")
    finally:
        close_progress_window()  # Закрываем окно прогресса