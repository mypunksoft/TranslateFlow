from tkinter import Toplevel, scrolledtext, messagebox

def show_logs_window():
    log_window = Toplevel()
    log_window.title("Логи")

    log_text = scrolledtext.ScrolledText(log_window, width=80, height=20, wrap='word')
    log_text.pack(padx=10, pady=10)

    try:
        with open("app.log", "r", encoding="utf-8") as log_file:
            log_text.insert('end', log_file.read())
    except Exception as e:
        log_text.insert('end', f"Ошибка при чтении логов: {e}")

    log_text.config(state='disabled')