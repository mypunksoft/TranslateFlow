import tkinter as tk
from tkinter import scrolledtext, Listbox, messagebox, ttk
import os
from utils.file_operations import load_json_file, save_translated_data, import_translations, sort_keys
from ui.ui_helpers import update_file_list, update_status, update_translation_table
from app.directory_operations import choose_directory
from ui.logs_window import show_logs_window
from ui.translation_window import open_translation_window
from utils.json_operations import create_json_files
from utils.image_processing import convert_webp_to_jpg, process_images_from_folder

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("TranslateFlow")
        self.master.geometry("653x516")

        self.translated_data = {}
        self.data = {}
        self.current_directory = None
        self.translation_file_found = True
        self.progress_window = None

        self.create_widgets()
        self.create_menu()
        self.bind_events()

    def create_progress_window(self):
        """Создает отдельное окно для прогресс-бара."""
        if self.progress_window is None or not self.progress_window.winfo_exists():
            self.progress_window = tk.Toplevel(self.master)
            self.progress_window.title("Прогресс")
            self.progress_window.geometry("400x100")
            self.progress_window.resizable(False, False)

            # Устанавливаем окно всегда поверх других
            self.progress_window.attributes("-topmost", True)

            self.progress_bar = ttk.Progressbar(self.progress_window, orient="horizontal", length=300, mode="determinate")
            self.progress_bar.pack(pady=20)

    def update_progress(self, value):
        """Обновляет значение прогресс-бара."""
        if self.progress_bar:
            self.progress_bar["value"] = value
            self.progress_bar.update_idletasks()

    def close_progress_window(self):
        """Закрывает окно прогресс-бара."""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.destroy()
            self.progress_window = None


    def create_widgets(self):
        """Создает элементы интерфейса."""
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.text_frame = tk.Frame(self.notebook)
        self.notebook.add(self.text_frame, text="Текущий текст")

        self.mapping_frame = tk.Frame(self.notebook)
        self.notebook.add(self.mapping_frame, text="оригинал - перевод")

        self.selected_file_label = tk.Label(self.text_frame, text="Файл не выбран", anchor="w")
        self.selected_file_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.sidebar_frame = tk.Frame(self.text_frame)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.stats_frame = tk.Frame(self.sidebar_frame)
        self.stats_frame.pack(side=tk.TOP, fill=tk.X)

        self.image_stats_label = tk.Label(self.stats_frame, text="JPG: 0, WEBP: 0")
        self.image_stats_label.pack(side=tk.TOP, pady=2)

        self.status_label = tk.Label(self.stats_frame, text="Переведено: 0, Не переведено: 0")
        self.status_label.pack(side=tk.TOP, pady=2)

        self.file_listbox = Listbox(self.sidebar_frame, width=30, height=20)
        self.file_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.left_text = scrolledtext.ScrolledText(self.text_frame, width=50, height=20, wrap=tk.WORD)
        self.left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_text.tag_configure("translated", foreground="green")
        self.left_text.tag_configure("untranslated", foreground="red")

        self.tree = ttk.Treeview(self.mapping_frame, columns=("original", "translation"), show="headings", height=20)
        self.tree.heading("original", text="Оригинал")
        self.tree.heading("translation", text="Перевод")
        self.tree.column("original", width=200)
        self.tree.column("translation", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_menu(self):
        """Создает меню."""
        menubar = tk.Menu(self.master)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть файл", command=self.load_file)
        file_menu.add_command(label="Открыть директорию", command=self.open_directory)
        file_menu.add_command(label="Сохранить (Ctrl+S)", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.master.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        actions_menu = tk.Menu(menubar, tearoff=0)
        actions_menu.add_command(label="Импортировать переводы", command=self.import_translations)
        actions_menu.add_command(label="Сортировать ключи", command=self.sort_keys)
        menubar.add_cascade(label="Действия", menu=actions_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Создать JSON файл страницы", command=self.create_json_files)
        tools_menu.add_command(label="WEBP to JPG", command=self.convert_webp_to_jpg)
        tools_menu.add_command(label="Обработать изображения", command=self.process_images)  # Новый пункт меню
        menubar.add_cascade(label="Инструменты", menu=tools_menu)

        self.master.config(menu=menubar)

    def bind_events(self):
        """Привязывает события."""
        self.left_text.bind("<Button-1>", self.on_left_text_click)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        self.master.bind("<Control-s>", lambda event: self.save_file())  # Сохранение
        self.master.bind("<Control-i>", lambda event: self.import_translations())  # Импорт переводов
        self.master.bind("<Control-j>", lambda event: self.create_json_files())  # Создание JSON-файлов
        self.master.bind("<Control-w>", lambda event: self.master.quit())  # Выход
        self.master.bind("<Control-f>", lambda event: self.sort_keys())  # Сортировка ключей
        self.master.bind("<Control-o>", lambda event: self.load_file())  # Открытие файла
        self.master.bind("<Control-d>", lambda event: choose_directory())


    def load_file(self):
        """Открывает файл и обновляет интерфейс."""
        file_path = tk.filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        try:
            self.data = load_json_file(file_path)
            self.translated_data.clear()
            self.update_ui()
            self.hide_directory_elements()
            self.image_stats_label.pack_forget()
            self.selected_file_label.config(text=f"Выбранный файл: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def open_directory(self):
        """Открывает директорию и обновляет интерфейс."""
        self.current_directory = choose_directory()
        if self.current_directory:
            self.show_directory_elements()
            self.image_stats_label.pack(side=tk.TOP, pady=2)
            update_file_list(self.file_listbox, self.current_directory)
            self.update_ui()

    def save_file(self):
        """Сохраняет переведенные данные."""
        save_translated_data(self.data, self.translated_data, self.current_directory, self.selected_file_label)

    def import_translations(self):
        """Импортирует переводы."""
        file_path = tk.filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            import_translations(file_path, self.data, self.translated_data)
            messagebox.showinfo("Успех", "Переводы импортированы!")
            self.update_ui()

    def sort_keys(self):
        """Сортирует ключи."""
        self.data = sort_keys(self.data, self.translated_data)
        self.update_ui()

    def create_json_files(self):
        """Вызывает функцию создания JSON-файлов."""
        create_json_files(
            self.current_directory,
            self.create_progress_window,
            self.update_progress,
            self.close_progress_window,
            self.update_ui
        )
    
    def hide_directory_elements(self):
        """Скрывает элементы интерфейса, связанные с директориями."""
        self.file_listbox.pack_forget()
        self.selected_file_label.config(text="Файл не выбран")
        
    def convert_webp_to_jpg(self):
        if not self.current_directory:
            messagebox.showerror("Ошибка", "Сначала выберите папку через меню 'Открыть директорию'.")
            return

        self.create_progress_window()
        convert_webp_to_jpg(
            self.current_directory,
            self.progress_bar,
            self.update_ui,
            self.left_text,
            self.data,
            self.translated_data,
            self.status_label,
            self.file_listbox,
            self.image_stats_label
        )
        self.close_progress_window()
    
    def process_images(self):
        """Обрабатывает изображения в текущей директории."""
        if not self.current_directory:
            messagebox.showerror("Ошибка", "Сначала выберите директорию.")
            return

        try:
            process_images_from_folder(self.current_directory)
            messagebox.showinfo("Успех", "Обработка изображений завершена.")
            self.update_ui()  # Обновляем интерфейс после обработки
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке изображений: {e}")
    
    def show_directory_elements(self):
        """Показывает элементы интерфейса, связанные с директориями."""
        self.file_listbox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.selected_file_label.config(text="Файл не выбран")

    def update_ui(self):
        """Обновляет интерфейс, кроме списка файлов."""
        self.left_text.config(state=tk.NORMAL)
        self.left_text.delete(1.0, tk.END)
        for key in self.data:
            tag = "translated" if key in self.translated_data else "untranslated"
            self.left_text.insert(tk.END, f'"{key}"\n', tag)
        self.left_text.config(state=tk.DISABLED)

        update_status(self.data, self.translated_data, self.status_label)

        if self.current_directory:
            jpg_files = [
                f for f in os.listdir(self.current_directory)
                if f.lower().endswith(".jpg") and "filled_" not in f.lower()
                ]
            webp_files = [f for f in os.listdir(self.current_directory) if f.lower().endswith(".webp")]
            self.image_stats_label.config(text=f"JPG: {len(jpg_files)}, WEBP: {len(webp_files)}")
    
    def on_tab_changed(self, event):
        """Обработчик события переключения вкладок."""
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Соотношение оригинал - перевод":
            update_translation_table(self.tree, self.data, self.translated_data)
            if not self.translation_file_found:
                messagebox.showwarning("Предупреждение", "Файл перевода не найден.")

    def on_left_text_click(self, event):
        """Обрабатывает клик по тексту."""
        index = self.left_text.index(tk.CURRENT)
        line_number = int(index.split(".")[0])
        if 1 <= line_number <= len(self.data):
            key = list(self.data.keys())[line_number - 1]
            value = self.data[key]
            open_translation_window(
                key,
                value,
                self.translated_data,
                self.update_ui,
                self.left_text,
                self.data,
                self.status_label,
                self.file_listbox,
                self.image_stats_label,
                self.current_directory
            )

    def on_file_select(self, event):
        try:
            current_scroll_position = self.file_listbox.yview()
            selected_index = self.file_listbox.curselection()
            if not selected_index:
                return 
            selected_file = self.file_listbox.get(selected_index)
            file_path = os.path.join(self.current_directory, selected_file)
            if file_path.endswith(".json"):
                original_data = load_json_file(file_path)
                self.data.clear()
                self.data.update(original_data)
                original_name, ext = os.path.splitext(selected_file)
                translated_file = f"{original_name}_translate{ext}"
                translated_path = os.path.join(self.current_directory, translated_file)

                if os.path.exists(translated_path):
                    translated_data = load_json_file(translated_path)
                    self.translated_data.clear()
                    self.translated_data.update(translated_data)
                    self.translation_file_found = True 
                else:
                    self.translated_data.clear()
                    self.translation_file_found = False 

                update_file_list(self.file_listbox, self.current_directory)

                update_translation_table(self.tree, self.data, self.translated_data)

                self.selected_file_label.config(text=f"Выбранный файл: {selected_file}")

                self.file_listbox.selection_clear(0, tk.END)
                self.file_listbox.selection_set(selected_index)
                self.file_listbox.see(selected_index)  
                self.file_listbox.yview_moveto(current_scroll_position[0])

                self.update_ui()  
        except tk.TclError as e:
            print(f"Ошибка выбора файла: {e}")
