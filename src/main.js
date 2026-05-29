let searchTimeout; // Переменная для таймера
let dictionary = [];
const input = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');
const toast = document.getElementById('toast');

function normalize(text) {
  const map = { 'ә': 'а', 'і': 'и', 'ң': 'н', 'ғ': 'г', 'ү': 'у', 'ұ': 'у', 'қ': 'к', 'ө': 'о', 'һ': 'х' };
  return text.toLowerCase().split('').map(c => map[c] || c).join('');
}

async function loadDict() {
  try {
    const response = await fetch('dictionary.json');
    dictionary = await response.json();
    input.disabled = false;
    input.placeholder = "Введите слово...";
    input.focus();
  } catch (e) {
    resultsDiv.innerHTML = "<p style='color: red;'>Ошибка загрузки базы</p>";
  }
}

// function getWeight(word, norm, trans, q, qN) {
//   const w = word.toLowerCase();
//   const t = trans.toLowerCase();
//   if (w === q) return 1;
//   if (norm === qN && w.length === q.length) return 2;
//   const tParts = t.split(/[;|,]\s*/);
//   if (tParts.some(p => p.trim() === q)) return 5;
//   if (w.startsWith(q)) return 10;
//   if (norm.startsWith(qN)) return 15;
//   if (t.startsWith(q)) return 20;
//   if (w.includes(q) || t.includes(q)) return 100 + t.length;
//   return 999;
// }

function getWeight(word, norm, trans, q, qN) {
  const w = word.toLowerCase();
  const t = trans.toLowerCase();

  if (w === q) return 1;
  if (norm === qN && w.length === q.length) return 2;

  // Разбиваем перевод на части по точкам с запятой или запятым
  const tParts = t.split(/[;|,]\s*/);

  // Флаг: нашли ли мы точное совпадение слова после очистки от мусора
  let hasExactWordAfterClean = false;
  // Флаг: нашли ли мы фразу, где "мышь" идет как отдельное слово (например, "летучая мышь")
  let hasPhraseWithWord = false;

  tParts.forEach(p => {
    const trimmed = p.strip ? p.strip() : p.trim();

    // Очищаем от "зоол. ", "хим. " и скобок
    const cleanPart = trimmed
      .replace(/^[а-яё]+\.\s+/, '')
      .replace(/\s*\(.*?\)\s*/g, '')
      .trim();

    if (cleanPart === q) {
      hasExactWordAfterClean = true;
    }

    // Проверяем, есть ли слово внутри этой части как ОТДЕЛЬНОЕ слово.
    // Чтобы не зависеть от багов кириллической \b, проверяем пробелы вручную
    // Слово "мышь" считается отдельным, если вокруг него пробелы или это края строки
    const wordsInPart = cleanPart.split(/\s+/);
    if (wordsInPart.includes(q)) {
      hasPhraseWithWord = true;
    }
  });

  // 1. САМЫЙ ТОП: Прямые переводы ("мышь", "зоол. мышь (mus)", "мышь (компьютерная)")
  if (hasExactWordAfterClean) return 5;

  if (w.startsWith(q)) return 10;
  if (norm.startsWith(qN)) return 15;
  if (t.startsWith(q)) return 20;

  // 2. СРЕДНИЙ ПРИОРИТЕТ: Составные понятия, где "мышь" — отдельное слово ("летучая мышь", "домовая мышь")
  // Даем фиксированный небольшой вес (например, 30), чтобы длина строки вообще не влияла!
  if (hasPhraseWithWord) return 30;

  // 3. НИЗШИЙ ПРИОРИТЕТ: Частичные совпадения в корне ("мышьяк", "мышьяковистый")
  // Они гарантированно получат вес 100+ и улетят в самый подвал, под летучих мышей
  if (w.includes(q) || t.includes(q)) return 100 + t.length;

  return 999;
}

function search() {
  // Очищаем предыдущий таймер, если пользователь нажал клавишу снова
  clearTimeout(searchTimeout);

  // Устанавливаем новый таймер
  searchTimeout = setTimeout(() => {
    let query = input.value.replace(/\s\s+/g, ' ').toLowerCase();
    let trimmedQuery = query.trim();

    if (trimmedQuery.length < 1) {
      resultsDiv.innerHTML = "";
      return;
    }

    const qNorm = normalize(trimmedQuery);

    // Сам процесс фильтрации
    const filtered = dictionary.filter(item => {
      return item.w.toLowerCase().includes(trimmedQuery) ||
        item.n.includes(qNorm) ||
        item.t.toLowerCase().includes(trimmedQuery);
    });

    // Сортировка по весам
    filtered.sort((a, b) => {
      const wA = getWeight(a.w, a.n, a.t, trimmedQuery, qNorm);
      const wB = getWeight(b.w, b.n, b.t, trimmedQuery, qNorm);
      return wA - wB;
    });

    render(filtered.slice(0, 40));
  }, 150); // Задержка 150 мс — золотая середина между скоростью и экономией ресурсов
}

function render(data) {
  resultsDiv.innerHTML = data.map(item => `
        <div class="result-item" data-word="${item.w}">
            <span class="copy-hint">клик — копировать</span>
            <div class="word-title">${item.w}</div>
            <div class="translation">${item.t}</div>
        </div>
    `).join('');
}

function copyToClipboard(text) {
  // 1. Пробуем современный метод
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => {
      showToast();
    }).catch(err => {
      fallbackCopy(text);
    });
  } else {
    // 2. Если http или старый браузер — используем запасной вариант
    fallbackCopy(text);
  }
}

function fallbackCopy(text) {
  const textArea = document.createElement("textarea");
  textArea.value = text;

  // Прячем поле, чтобы экран не дергался
  textArea.style.position = "fixed";
  textArea.style.left = "-999999px";
  textArea.style.top = "-999999px";
  document.body.appendChild(textArea);

  textArea.focus();
  textArea.select();

  try {
    document.execCommand('copy');
    showToast();
  } catch (err) {
    console.error('Не удалось скопировать', err);
  }

  document.body.removeChild(textArea);
}

function showToast() {
  toast.style.display = 'block';
  setTimeout(() => { toast.style.display = 'none'; }, 1500);
}


function addChar(char) {
  input.value += char;
  input.focus();
  search();
}

// Слушатель для Esc (очистка и фокус)
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    input.value = '';
    input.focus();
    search();
  }
});

document.querySelectorAll('.btn-kz').forEach(button => {
  button.addEventListener('click', () => {
    const char = button.getAttribute('data-char');
    addChar(char);
  });
});

resultsDiv.addEventListener('click', (event) => {
  const item = event.target.closest('.result-item');

  if (item) {
    const wordToCopy = item.getAttribute('data-word');
    copyToClipboard(wordToCopy);
  }
});

input.addEventListener('input', search);
loadDict();
