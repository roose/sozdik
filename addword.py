import json
import os
from datetime import datetime  # Добавляем импорт даты

# Путь к твоему JSON-файлу в проекте Vite
FILE_PATH = os.path.join('public', 'dictionary.json')
CHANGELOG_PATH = 'CHANGELOG.md'  # Путь к чейнджлогу

def normalize(text):
    replacements = {
        'ә': 'а', 'і': 'и', 'ң': 'н', 'ғ': 'г', 'ү': 'у',
        'ұ': 'у', 'қ': 'к', 'ө': 'о', 'һ': 'х'
    }
    low_text = text.lower()
    for kz_char, ru_char in replacements.items():
        low_text = low_text.replace(kz_char, ru_char)
    return low_text

def add_new_word():
    print("--- Добавление нового слова в словарь ---")
    word = input("Введите казахское слово (w): ").strip()
    translation = input("Введите перевод на русский (t): ").strip()

    if not word or not translation:
        print("Ошибка: поля не могут быть пустыми!")
        return

    # 1. Читаем существующий файл (или создаем пустой массив, если файла нет)
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            try:
                result_data = json.load(f)
            except json.JSONDecodeError:
                result_data = []
    else:
        result_data = []

    # 2. Формируем новый объект
    new_entry = {
        "w": word,
        "n": normalize(word),
        "t": translation
    }

    # 3. Добавляем в массив
    result_data.append(new_entry)

    # 4. Сохраняем обратно в файл
    # Если хочешь, чтобы файл оставался супер-компактным (в одну строку), оставь separators=(',', ':')
    # Если хочешь, чтобы его было удобно читать глазами в VS Code, замени на indent=2
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, separators=(',', ':'))

    # === НАЧАЛО БЛОКА С ЧЕЙНДЖЛОГОМ ===
    # Получаем текущую дату в удобном формате, например: 29.05.2026
    current_date = datetime.now().strftime("%d.%m.%Y")

    # Текст новой строчки в формате Markdown-списка
    changelog_entry = f"* **[{current_date}]** `{word}` — {translation}\n"

    # Проверяем, существует ли файл. Если нет — создадим с красивым заголовком
    if not os.path.exists(CHANGELOG_PATH):
        with open(CHANGELOG_PATH, 'w', encoding='utf-8') as f:
            f.write("# История добавления слов\n\n")

    # Открываем файл в режиме 'a' (append) для дозаписи в конец
    with open(CHANGELOG_PATH, 'a', encoding='utf-8') as f:
        f.write(changelog_entry)
    # === КОНЕЦ БЛОКА С ЧЕЙНДЖЛОГОМ ===

    print(f"\nУспешно добавлено! Всего слов в базе: {len(result_data)}\n")

if __name__ == '__main__':
    # Цикл, чтобы можно было добавлять несколько слов подряд, не перезапуская скрипт
    while True:
        add_new_word()
        cont = input("Хотите добавить еще одно слово? (д/н): ").strip().lower()
        if cont not in ['д', 'y', 'yes', 'да']:
            print("Выход из скрипта.")
            break
