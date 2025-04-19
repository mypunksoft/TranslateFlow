import tkinter as tk
from app.main_window import MainWindow
from config.logger import setup_logger

def main():
    setup_logger()
    root = tk.Tk()
    root.title("TranslateFlow")
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()