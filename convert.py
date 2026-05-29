import json
import os

# словарь скачан с https://kaikki.org/ruwiktionary/raw-wiktextract-data.jsonl.gz ~2.5gb
# Функция для создания ключа "без специфических букв"
def normalize(text):
    replacements = {
        'ә': 'а', 'і': 'и', 'ң': 'н', 'ғ': 'г', 'ү': 'у',
        'ұ': 'у', 'қ': 'к', 'ө': 'о', 'һ': 'х'
    }
    low_text = text.lower()
    for kz_char, ru_char in replacements.items():
        low_text = low_text.replace(kz_char, ru_char)
    return low_text

input_file = 'raw-wiktextract-data.jsonl'
output_file = os.path.join('public', 'dictionary.json')
result_data = []

with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)

        # Проверяем, что это казахское слово
        # if data.get('lang') == 'Kazakh':
        if data.get('lang') == 'Казахский':
            word = data.get('word')
            senses = data.get('senses', [])

            translations = []
            for sense in senses:
                # Ищем переводы (в Wiktextract они часто в glosses)
                glosses = sense.get('glosses', [])
                if glosses:
                    translations.extend(glosses)

            if word and translations:
                result_data.append({
                    "w": word,
                    "n": normalize(word), # Для поиска қүдық -> құдық
                    "t": "; ".join(translations)[:200] # Ограничим длину перевода
                })

# Сохраняем в компактный JSON
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result_data, f, ensure_ascii=False, separators=(',', ':'))

print(f"Готово! Обработано слов: {len(result_data)}")
