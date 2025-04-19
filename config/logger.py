import logging
import os

def setup_logger():
    log_file = "app.log"  # Укажите имя файла логов

    # Проверяем, существует ли файл логов, и создаем его, если он отсутствует
    if not os.path.exists(log_file):
        with open(log_file, "w") as file:
            file.write("")  # Создаем пустой файл

    # Настраиваем логгер
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Логгер успешно настроен.")
    logger = logging.getLogger(__name__)
    logging.getLogger("ppocr").setLevel(logging.ERROR)
    return logger

logger = setup_logger()