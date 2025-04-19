from tkinter import Toplevel, Label, Text, Button, Menu, scrolledtext
from ui.ui_helpers import update_file_list
import pyperclip
import tkinter as tk

def open_translation_window(key, value, translated_data, update_ui, left_text, data, status_label, file_listbox, image_stats_label, current_directory):
    translation_window = Toplevel()
    translation_window.title(f"Перевод для: {key}")

    Label(translation_window, text=f"Ключ: {key}", font=("Arial", 10, "bold")).pack(pady=5)

    Label(translation_window, text="Текущее значение:").pack(pady=5)
    current_value_text = scrolledtext.ScrolledText(translation_window, width=60, height=5, wrap='word')
    current_value_text.insert('end', value)
    current_value_text.config(state='disabled')
    current_value_text.pack(pady=5)

    Label(translation_window, text="Перевод:").pack(pady=5)
    translation_entry = Text(translation_window, width=60, height=8)
    translation_entry.insert('end', translated_data.get(key, ""))
    translation_entry.pack(pady=5)

    def save_translation(event=None):
        translated_data[key] = translation_entry.get("1.0", tk.END).strip()
        translation_window.destroy()
        update_ui()
        update_file_list(file_listbox, current_directory)

    def open_edit_key_window():
        """Открывает окно для редактирования значения ключа."""
        edit_window = Toplevel(translation_window)
        edit_window.title(f"Редактировать значение ключа: {key}")
        edit_window.geometry("400x200")

        Label(edit_window, text="Новое значение ключа:").pack(pady=5)
        key_value_entry = Text(edit_window, width=50, height=5)
        key_value_entry.insert('end', value)
        key_value_entry.pack(pady=5)

        def save_key_value():
            new_value = key_value_entry.get("1.0", tk.END).strip()
            if new_value:
                data[key] = new_value
                update_ui()

                current_value_text.config(state='normal')
                current_value_text.delete('1.0', tk.END)
                current_value_text.insert('end', new_value)
                current_value_text.config(state='disabled')

                edit_window.destroy()
            else:
                tk.messagebox.showerror("Ошибка", "Значение ключа не может быть пустым.")

        save_button = Button(edit_window, text="Сохранить", command=save_key_value)
        save_button.pack(pady=10)

    '''edit_key_button = Button(translation_window, text="Редактировать значение ключа", command=open_edit_key_window)
    edit_key_button.pack(pady=5)'''

    save_button = Button(translation_window, text="Сохранить перевод", command=save_translation)
    save_button.pack(pady=10)