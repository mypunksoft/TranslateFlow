# TranslateFlow

**TranslateFlow** — программа, разработанная для помощи переводчикам манги и разработчикам игр на Unity. Она предоставляет удобный интерфейс для визуализации, редактирования и перевода текстовых данных, извлеченных из изображений или JSON-файлов. Программа также поддерживает обработку изображений, что делает её полезным инструментом для работы с текстами, встроенными в графические материалы.

## 🚀 Основные функции

- **Визуализация и редактирование JSON-файлов**: Загружайте и редактируйте содержимое JSON-файлов в удобном интерфейсе.
- **Ручной перевод**: Переводите текст вручную с помощью встроенного редактора.
- **Импорт переводов**: Импортируйте уже переведенные данные из других JSON-файлов.
- **Обработка изображений**: Извлекайте текст из изображений (JPG, WEBP) с помощью **PaddleOCR** и сохраняйте его в JSON.
- **Конвертация изображений**: Конвертируйте изображения из формата WEBP в JPG для удобства обработки.
- **Логирование**: Все действия программы логируются в файл `app.log` для отслеживания изменений и устранения ошибок.
- **Установщик**: Удобный установщик для автоматической настройки программы и всех зависимостей.

---

## 📦 Установка и запуск

### 1️⃣ Вариант 1: Использование установщика

1. Скачайте установщик.
2. Запустите установщик и следуйте инструкциям на экране.
3. После завершения установки программа будет готова к использованию.

### 2️⃣ Вариант 2: Ручная установка

1. Убедитесь, что у вас установлен **Python 3.7 или выше**.
2. Установите необходимые зависимости:

   ```bash
   pip install pillow pyperclip
   ```

3. **Установка PaddlePaddle и PaddleOCR**:
   - Для установки библиотек `paddlepaddle` и `paddleocr` может потребоваться запуск от имени администратора.
   - Установите зависимости:

     ```bash
     sudo pip install paddlepaddle paddleocr
     ```

     **Для Windows**:
     - Запустите командную строку от имени администратора и выполните:

       ```bash
       pip install paddlepaddle paddleocr
       ```

4. Запустите программу:

   ```bash
   python main.py
   ```

---

## 🛠️ Использование

1. **Загрузка JSON-файла**:
   - Используйте меню `Файл` -> `Открыть файл`, чтобы загрузить JSON-файл.
   - Программа отобразит его содержимое для редактирования.

2. **Открытие директории**:
   - Используйте меню `Файл` -> `Открыть директорию` для выбора папки с изображениями и JSON-файлами.

3. **Ручной перевод**:
   - Кликните на текстовый элемент в левой панели, чтобы открыть окно перевода.
   - Введите перевод и сохраните изменения.

4. **Импорт переводов**:
   - Используйте кнопку `Импортировать` для загрузки уже переведенных данных из другого JSON-файла.

5. **Создание JSON-файлов из изображений**:
   - Нажмите `Создать JSON файл страницы`, чтобы извлечь текст из изображений и сохранить его в JSON.

6. **Конвертация WEBP в JPG**:
   - Нажмите кнопку `WEBP to JPG`, чтобы конвертировать изображения из формата WEBP в JPG.

7. **Просмотр логов**:
   - Используйте кнопку `Показать логи` для просмотра логов программы.

---

## 📜 Логирование

Все действия программы логируются в файл `app.log`. Логи включают информацию о загруженных файлах, выполненных переводах, ошибках и других событиях.

---

## 📋 Зависимости

- `tkinter`: Для создания графического интерфейса.
- `PaddleOCR`: Для извлечения текста из изображений.
- `Pillow`: Для работы с изображениями.
- `pyperclip`: Для работы с буфером обмена.
- `json`: Для работы с JSON-файлами.
- `os`: Для работы с файловой системой.
- `threading`: Для выполнения задач в фоновом режиме.
- `logging`: Для логирования событий.
