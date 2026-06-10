import json
import os
from datetime import datetime  # Добавляем импорт даты

# Пути к файлам
PATH_WIKI = os.path.join('src', 'data', 'wiki.json')
PATH_CUSTOM = os.path.join('src', 'data', 'custom.json')
PATH_FINAL = os.path.join('public', 'dictionary.json')
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

def compile_dictionary():
    # 1. Читаем кастомные слова (если файла нет, создаем пустой массив)
    if os.path.exists(PATH_CUSTOM):
        with open(PATH_CUSTOM, 'r', encoding='utf-8') as f:
            custom_data = json.load(f)
    else:
        custom_data = []

    # 2. Читаем слова из Вики
    if os.path.exists(PATH_WIKI):
        with open(PATH_WIKI, 'r', encoding='utf-8') as f:
            wiki_data = json.load(f)
    else:
        wiki_data = []

    # 3. Склеиваем их (кастомные в начало, чтобы у них был негласный приоритет)
    full_dictionary = custom_data + wiki_data

    # 4. Сохраняем в public для фронтенда
    # ensure_ascii=False сохранит казахские и русские буквы как есть, а не как \u0442
    with open(PATH_FINAL, 'w', encoding='utf-8') as f:
        json.dump(full_dictionary, f, ensure_ascii=False, separators=(',', ':'))

    print(f"🔥 Словарь успешно собран! Всего слов: {len(full_dictionary)} (Личных: {len(custom_data)}, Вики: {len(wiki_data)})")

def add_new_word():
    print("--- Добавление нового слова в словарь ---")
    word = input("Введите казахское слово (w): ").strip()
    translation = input("Введите перевод на русский (t): ").strip()

    if not word or not translation:
        print("Ошибка: поля не могут быть пустыми!")
        return

    # 1. Читаем существующий файл (или создаем пустой массив, если файла нет)
    if os.path.exists(PATH_CUSTOM):
        with open(PATH_CUSTOM, 'r', encoding='utf-8') as f:
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
    with open(PATH_CUSTOM, 'w', encoding='utf-8') as f:
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

    compile_dictionary()

if __name__ == '__main__':
    # Цикл, чтобы можно было добавлять несколько слов подряд, не перезапуская скрипт
    while True:
        add_new_word()
        cont = input("Хотите добавить еще одно слово? (д/н): ").strip().lower()
        if cont not in ['д', 'y', 'yes', 'да']:
            print("Выход из скрипта.")
            break
