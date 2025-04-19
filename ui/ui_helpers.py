import os
import tkinter as tk

def update_translation_table(tree, data, translated_data):
    """Обновляет таблицу 'оригинал - перевод'."""
    tree.delete(*tree.get_children())
    for key, value in data.items():
        translation = translated_data.get(key, "")
        tree.insert("", "end", values=(value, translation))

def update_file_list(file_listbox, current_directory):
    """Обновляет список файлов в директории."""
    file_listbox.delete(0, "end")
    json_files = [f for f in os.listdir(current_directory) if f.lower().endswith(".json")]
    for file_name in json_files:
        file_listbox.insert("end", file_name)

def update_file_list(file_listbox, current_directory):
        """Обновляет список файлов в директории."""
        if current_directory:
            file_listbox.delete(0, tk.END)  # Очищаем список файлов
            json_files = [f for f in os.listdir(current_directory) if f.lower().endswith(".json")]
            for file_name in json_files:
                file_listbox.insert(tk.END, file_name)  # Добавляем файлы в список

def update_status(data, translated_data, status_label):
        """Обновляет статус перевода."""
        translated_count = sum(1 for key in data if key in translated_data)
        untranslated_count = len(data) - translated_count
        status_label.config(text=f"Переведено: {translated_count}, Не переведено: {untranslated_count}")

def update_translation_table(tree, data,translated_data):
        """Обновляет таблицу 'оригинал - перевод'."""
        tree.delete(*tree.get_children())  # Очищаем таблицу
        for key, value in data.items():
            translation = translated_data.get(key, "")  # Получаем перевод, если он есть
            tree.insert("", tk.END, values=(value, translation))  # Добавляем строку с оригиналом и переводом