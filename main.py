import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, Listbox
from tkinter import ttk
import json
import os
import pyperclip
import threading
from paddleocr import PaddleOCR
from PIL import Image
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

logging.getLogger("ppocr").setLevel(logging.ERROR)


def update_ui(
    left_text, data, translated_data, status_label, file_listbox, image_stats_label
):
    update_visual_indication(left_text, data, translated_data, status_label)
    if current_directory:
        show_directory_files(
            current_directory,
            file_listbox,
            data,
            translated_data,
            left_text,
            status_label,
            update_ui,
            image_stats_label,
        )


def update_progress(progress_bar, value):
    progress_bar["value"] = value
    progress_bar.update_idletasks()


def show_progress_bar(progress_bar):
    progress_bar.pack(side=tk.BOTTOM, pady=10)
    progress_bar["value"] = 0
    progress_bar.update_idletasks()


def hide_progress_bar(progress_bar):
    progress_bar.pack_forget()


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


def import_translations(
    data,
    translated_data,
    update_ui,
    left_text,
    status_label,
    file_listbox,
    image_stats_label,
):
    file_path = choose_input_file()
    if file_path:
        new_data = load_json_file(file_path)
        for key, value in new_data.items():
            if key in data:
                translated_data[key] = value
        messagebox.showinfo("Успех", "Переводы импортированы!")
        update_ui(
            left_text,
            data,
            translated_data,
            status_label,
            file_listbox,
            image_stats_label,
        )


def update_visual_indication(left_text, data, translated_data, status_label):
    left_text.config(state=tk.NORMAL)
    left_text.delete(1.0, tk.END)
    for key in data:
        if key in translated_data:
            left_text.insert(tk.END, f'"{key}"\n', "translated")
        else:
            left_text.insert(tk.END, f'"{key}"\n', "untranslated")
    left_text.config(state=tk.DISABLED)
    update_status(status_label, data, translated_data)


def update_status(status_label, data, translated_data):
    translated_count = sum(1 for key in data if key in translated_data)
    untranslated_count = len(data) - translated_count
    status_label.config(
        text=f"Переведено: {translated_count}, Не переведено: {untranslated_count}"
    )


def open_translation_window(
    key,
    value,
    translated_data,
    update_ui,
    left_text,
    data,
    status_label,
    file_listbox,
    image_stats_label,
):
    translation_window = tk.Toplevel()
    translation_window.title(f"Перевод для: {key}")

    tk.Label(translation_window, text=f"Ключ: {key}", font=("Arial", 10, "bold")).pack(
        pady=5
    )

    tk.Label(translation_window, text="Текущее значение:").pack(pady=5)
    current_value_text = scrolledtext.ScrolledText(
        translation_window, width=60, height=5, wrap=tk.WORD
    )
    current_value_text.insert(tk.END, value)
    current_value_text.config(state=tk.DISABLED)
    current_value_text.pack(pady=5)

    tk.Label(translation_window, text="Перевод:").pack(pady=5)
    translation_entry = tk.Text(translation_window, width=60, height=8)
    translation_entry.insert(tk.END, translated_data.get(key, ""))
    translation_entry.pack(pady=5)

    def copy_text(event=None):
        selected_text = translation_entry.selection_get()
        pyperclip.copy(selected_text)

    def paste_text(event=None):
        translation_entry.insert(tk.INSERT, pyperclip.paste())
        return "break"

    def select_all_text(event=None):
        translation_entry.tag_add(tk.SEL, "1.0", tk.END)
        translation_entry.mark_set(tk.INSERT, "1.0")
        translation_entry.see(tk.INSERT)
        return "break"

    def save_translation(event=None):
        translated_data[key] = translation_entry.get("1.0", tk.END).strip()
        translation_window.destroy()
        update_ui(
            left_text,
            data,
            translated_data,
            status_label,
            file_listbox,
            image_stats_label,
        )

    translation_entry.bind("<Control-v>", paste_text)
    translation_entry.bind("<Control-c>", copy_text)
    translation_entry.bind("<Control-a>", select_all_text)

    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)

    context_menu = tk.Menu(translation_window, tearoff=0)
    context_menu.add_command(label="Копировать текст", command=copy_text)
    context_menu.add_command(label="Вставить текст", command=paste_text)
    context_menu.add_command(
        label="Копировать ключ", command=lambda: pyperclip.copy(key)
    )

    # translation_entry.bind("<Button-3>", show_context_menu)

    translation_window.bind("<Button-3>", show_context_menu)

    save_button = tk.Button(
        translation_window, text="Сохранить перевод", command=save_translation
    )
    save_button.pack(pady=10)


def load_file(
    data,
    translated_data,
    left_text,
    status_label,
    file_listbox,
    image_stats_label,
    update_ui,
):
    file_path = choose_input_file()
    if file_path:
        new_data = load_json_file(file_path)
        data.clear()
        data.update(new_data)
        translated_data.clear()
        update_ui(
            left_text,
            data,
            translated_data,
            status_label,
            file_listbox,
            image_stats_label,
        )


def show_directory_files(
    directory,
    file_listbox,
    data,
    translated_data,
    left_text,
    status_label,
    update_ui,
    image_stats_label,
):
    file_listbox.delete(0, tk.END)
    jpg_files = [f for f in os.listdir(directory) if f.lower().endswith(".jpg")]
    webp_files = [f for f in os.listdir(directory) if f.lower().endswith(".webp")]

    image_stats_label.config(text=f"JPG: {len(jpg_files)}, WEBP: {len(webp_files)}")

    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            file_listbox.insert(tk.END, file_name)

    def on_file_select(event):
        selected_file = file_listbox.get(file_listbox.curselection())
        file_path = os.path.join(directory, selected_file)
        new_data = load_json_file(file_path)
        data.clear()
        data.update(new_data)
        translated_data.clear()
        update_ui(
            left_text,
            data,
            translated_data,
            status_label,
            file_listbox,
            image_stats_label,
        )

    file_listbox.bind("<<ListboxSelect>>", on_file_select)


def process_folder(folder_path):
    jpg_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")]

    if not jpg_files:
        messagebox.showerror("Ошибка", "В папке нет изображений .jpg")

        return

    for jpg_file in jpg_files:
        image_path = os.path.join(folder_path, jpg_file)
        json_path = os.path.join(folder_path, os.path.splitext(jpg_file)[0] + ".json")

        extract_text_to_json(image_path, json_path)


def extract_text_to_json(
    image_path, json_path, confidence_threshold=0.93, x_tolerance=15
):
    ocr = PaddleOCR(use_angle_cls=True, lang="en")
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


def convert_webp_to_jpg(
    progress_bar,
    left_text,
    data,
    translated_data,
    status_label,
    file_listbox,
    image_stats_label,
    update_ui,
):
    global current_directory

    if not current_directory:
        logger.error("Директория не выбрана.")
        messagebox.showerror(
            "Ошибка", "Сначала выберите папку через меню 'Открыть директорию'."
        )
        return

    webp_files = [
        f for f in os.listdir(current_directory) if f.lower().endswith(".webp")
    ]
    total_files = len(webp_files)

    if total_files == 0:
        logger.info("WEBP-файлы не найдены.")
        messagebox.showinfo("Информация", "WEBP-файлы не найдены.")
        return

    show_progress_bar(progress_bar)
    logger.info(f"Начало конвертации {total_files} WEBP-файлов.")

    def convert_files():
        for i, filename in enumerate(webp_files):
            webp_path = os.path.join(current_directory, filename)
            jpg_path = os.path.join(
                current_directory, filename.rsplit(".", 1)[0] + ".jpg"
            )

            try:
                with Image.open(webp_path) as img:
                    img.convert("RGB").save(jpg_path, "JPEG", quality=95)
                os.remove(webp_path)
                logger.info(f"Файл {filename} успешно конвертирован.")
            except Exception as e:
                logger.error(f"Ошибка при конвертации файла {filename}: {e}")

            progress = (i + 1) / total_files * 100
            update_progress(progress_bar, progress)

        hide_progress_bar(progress_bar)
        logger.info("Конвертация завершена.")
        messagebox.showinfo("Успех", "Конвертация завершена.")
        update_ui(
            left_text,
            data,
            translated_data,
            status_label,
            file_listbox,
            image_stats_label,
        )

    threading.Thread(target=convert_files).start()


def create_json_files(
    progress_bar,
    left_text,
    data,
    translated_data,
    status_label,
    file_listbox,
    image_stats_label,
    update_ui,
):
    global current_directory

    if not current_directory:
        logger.error("Директория не выбрана.")
        messagebox.showerror(
            "Ошибка", "Сначала выберите папку через меню 'Открыть директорию'."
        )
        return

    jpg_files = [f for f in os.listdir(current_directory) if f.lower().endswith(".jpg")]
    total_files = len(jpg_files)

    if total_files == 0:
        logger.info("JPG-файлы не найдены.")
        messagebox.showinfo("Информация", "JPG-файлы не найдены.")
        return

    show_progress_bar(progress_bar)
    logger.info(f"Начало создания JSON-файлов для {total_files} JPG-файлов.")

    def create_jsons():
        for i, filename in enumerate(jpg_files):
            jpg_path = os.path.join(current_directory, filename)
            json_path = os.path.join(
                current_directory, filename.rsplit(".", 1)[0] + ".json"
            )

            try:
                extract_text_to_json(jpg_path, json_path)
                logger.info(f"JSON-файл создан для {filename}.")
            except Exception as e:
                logger.error(f"Ошибка при создании JSON для файла {filename}: {e}")

            progress = (i + 1) / total_files * 100
            update_progress(progress_bar, progress)

        hide_progress_bar(progress_bar)
        logger.info("Создание JSON-файлов завершено.")
        messagebox.showinfo("Успех", "JSON-файлы успешно созданы.")
        update_ui(
            left_text,
            data,
            translated_data,
            status_label,
            file_listbox,
            image_stats_label,
        )

    threading.Thread(target=create_jsons).start()


def show_logs_window():
    log_window = tk.Toplevel()
    log_window.title("Логи")

    log_text = scrolledtext.ScrolledText(log_window, width=80, height=20, wrap=tk.WORD)
    log_text.pack(padx=10, pady=10)

    try:
        with open("app.log", "r", encoding="utf-8") as log_file:
            log_text.insert(tk.END, log_file.read())
    except Exception as e:
        log_text.insert(tk.END, f"Ошибка при чтении логов: {e}")

    log_text.config(state=tk.DISABLED)


def main():
    global current_directory

    window = tk.Tk()
    window.title("JSON Visualizer and Manual Translator")

    progress_bar = ttk.Progressbar(
        window, orient="horizontal", length=300, mode="determinate"
    )
    progress_bar.pack(side=tk.BOTTOM, pady=10)
    progress_bar.pack_forget()

    menubar = tk.Menu(window)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(
        label="Открыть файл",
        command=lambda: load_file(
            data,
            translated_data,
            left_text,
            status_label,
            file_listbox,
            image_stats_label,
            update_ui,
        ),
    )
    file_menu.add_command(
        label="Открыть директорию",
        command=lambda: open_directory(
            data,
            translated_data,
            left_text,
            status_label,
            update_ui,
            file_listbox,
            image_stats_label,
        ),
    )
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=window.quit)
    menubar.add_cascade(label="Файл", menu=file_menu)
    window.config(menu=menubar)

    left_frame = tk.Frame(window)
    right_frame = tk.Frame(window)
    button_frame = tk.Frame(window)
    status_frame = tk.Frame(window)

    left_frame.pack(side=tk.LEFT, padx=10, pady=10)
    right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
    button_frame.pack(side=tk.BOTTOM, pady=10)
    status_frame.pack(side=tk.BOTTOM, pady=10)

    left_text = scrolledtext.ScrolledText(left_frame, width=50, height=20, wrap=tk.WORD)
    left_text.pack()

    image_stats_label = tk.Label(right_frame, text="JPG: 0, WEBP: 0")
    image_stats_label.pack()

    file_listbox = Listbox(right_frame, width=30, height=20)
    file_listbox.pack()

    translated_data = {}
    data = {}
    current_directory = None

    left_text.tag_config("translated", foreground="green")
    left_text.tag_config("untranslated", foreground="red")

    status_label = tk.Label(left_frame, text="Переведено: 0, Не переведено: 0")
    status_label.pack(side=tk.BOTTOM)

    def update_uil():
        update_visual_indication(left_text, data, translated_data, status_label)

    def sort_keys(
        data,
        translated_data,
        left_text,
        status_label,
        file_listbox,
        image_stats_label,
        update_ui,
    ):
        sorted_keys = sorted(data.keys(), key=lambda k: (k in translated_data, k))
        sorted_data = {key: data[key] for key in sorted_keys}
        data.clear()
        data.update(sorted_data)
        update_ui(
            left_text,
            data,
            translated_data,
            status_label,
            file_listbox,
            image_stats_label,
        )

    def on_left_text_click(event):
        index = left_text.index(tk.CURRENT)
        line_number = int(index.split(".")[0])
        key = list(data.keys())[line_number - 1]
        value = data[key]

        open_translation_window(
            key,
            value,
            translated_data,
            update_ui,
            left_text,
            data,
            status_label,
            file_listbox,
            image_stats_label,
        )

    left_text.bind("<Button-1>", on_left_text_click)

    def save_file():
        output_file_path = "translated_output.json"
        save_translated_data(translated_data, output_file_path)

    def import_file():
        import_translations(data, translated_data, update_ui)

    save_button = tk.Button(button_frame, text="Сохранить", command=save_file)
    save_button.pack(side=tk.TOP, pady=5)

    import_button = tk.Button(
        button_frame,
        text="Импортировать",
        command=lambda: import_translations(
            data,
            translated_data,
            update_ui,
            left_text,
            status_label,
            file_listbox,
            image_stats_label,
        ),
    )
    import_button.pack(side=tk.TOP, pady=5)

    sort_button = tk.Button(
        button_frame,
        text="Сортировать",
        command=lambda: sort_keys(
            data,
            translated_data,
            left_text,
            status_label,
            file_listbox,
            image_stats_label,
            update_ui,
        ),
    )
    sort_button.pack(side=tk.TOP, pady=5)

    create_json_button = tk.Button(
        button_frame,
        text="Создать JSON файл страницы",
        command=lambda: create_json_files(
            progress_bar,
            left_text,
            data,
            translated_data,
            status_label,
            file_listbox,
            image_stats_label,
            update_ui,
        ),
    )
    create_json_button.pack(side=tk.TOP, pady=5)

    webp_to_jpg_button = tk.Button(
        button_frame,
        text="WEBP to JPG",
        command=lambda: convert_webp_to_jpg(
            progress_bar,
            left_text,
            data,
            translated_data,
            status_label,
            file_listbox,
            image_stats_label,
            update_ui,
        ),
    )
    webp_to_jpg_button.pack(side=tk.TOP, pady=5)

    show_logs_button = tk.Button(
        button_frame, text="Показать логи", command=show_logs_window
    )
    show_logs_button.pack(side=tk.TOP, pady=5)

    window.bind("<Control-s>", lambda event: save_file())
    window.bind("<Control-i>", lambda event: import_file())
    window.bind(
        "<Control-f>",
        lambda event: sort_keys(
            data,
            translated_data,
            left_text,
            status_label,
            file_listbox,
            image_stats_label,
            update_ui,
        ),
    )

    window.mainloop()


def open_directory(
    data,
    translated_data,
    left_text,
    status_label,
    update_ui,
    file_listbox,
    image_stats_label,
):
    global current_directory
    current_directory = choose_directory()
    if current_directory:
        show_directory_files(
            current_directory,
            file_listbox,
            data,
            translated_data,
            left_text,
            status_label,
            update_ui,
            image_stats_label,
        )


if __name__ == "__main__":
    main()
