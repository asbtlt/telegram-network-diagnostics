# Быстрый старт

## Установка

```bash
# Клонировать репозиторий
cd telegram-network-diagnostics

# Установить зависимости
pip install -e .
```

## Настройка (опционально)

Для упрощения работы создайте файл `config.py`:

```bash
cp config.example.py config.py
# Отредактируйте config.py и добавьте свой токен
```

## Использование

### Вариант 1: С config.py (рекомендуется)

```bash
# Быстрая проверка
telegram-diag check

# Мониторинг
telegram-diag monitor

# Мониторинг с интервалом 10 секунд
telegram-diag monitor --interval 10

# Полная диагностика (chat_id из config.py)
telegram-diag full
```

### Вариант 2: Без config.py

```bash
# Быстрая проверка (5 запросов)
telegram-diag check YOUR_BOT_TOKEN

# Мониторинг (непрерывный, Ctrl+C для остановки)
telegram-diag monitor YOUR_BOT_TOKEN

# Мониторинг с интервалом 10 секунд
telegram-diag monitor YOUR_BOT_TOKEN --interval 10

# Полная диагностика
telegram-diag full YOUR_BOT_TOKEN

# Полная диагностика с тестами загрузки файлов
telegram-diag full YOUR_BOT_TOKEN --chat-id YOUR_CHAT_ID
```

### Вариант 3: Через quickstart.py

```bash
# Быстрая проверка
python quickstart.py

# Или укажите команду
python quickstart.py check
python quickstart.py monitor
python quickstart.py full
```

### Вариант 4: Через Python модуль

```bash
python -m telegram_diagnostics.cli check YOUR_BOT_TOKEN
python -m telegram_diagnostics.cli monitor YOUR_BOT_TOKEN
python -m telegram_diagnostics.cli full YOUR_BOT_TOKEN
```

## Важно: config.py автоматически загружается

Если в текущей директории есть `config.py`, токен и chat_id будут загружены автоматически:

```python
# config.py
BOT_TOKEN = "123456:ABC-DEF..."
CHAT_ID = 123456789  # опционально
```

Тогда можно использовать команды без аргументов:

```bash
telegram-diag check      # токен из config.py
telegram-diag monitor    # токен из config.py
telegram-diag full       # токен и chat_id из config.py
```

## Как получить chat_id

1. Перейдите к боту [@userinfobot](https://t.me/userinfobot)
2. Отправьте любое сообщение
3. Бот пришлет ваш chat ID
4. Используйте этот ID для тестов с загрузкой файлов

## Примеры вывода

### Quick Check

```
🔍 Быстрая проверка Telegram API...

✅ Попытка 1/5: 234.12ms
✅ Попытка 2/5: 245.67ms
✅ Состояние: ОТЛИЧНОЕ
```

### Monitor

```
🔍 Запуск непрерывного мониторинга Telegram API
[21:05:01] 🟢 Проверка #   1: 234.12ms
[21:05:06] 🟢 Проверка #   2: 245.67ms
...
```

### Full Diagnostics

```
[21:05:30.123] 🔍 Проверка DNS разрешения
[21:05:30.234] ✅ DNS разрешение успешно за 45.23ms
[21:05:30.345] 🔍 Проверка TCP соединения
[21:05:30.456] ✅ TCP соединение успешно за 112.45ms
...
```

## Сохранение результатов

Все результаты автоматически сохраняются:
- Monitor: `telegram_monitor_YYYYMMDD_HHMMSS.log`
- Full: `telegram_network_diagnostics_YYYYMMDD_HHMMSS.log`

## Troubleshooting

### Токен не найден

Если видите ошибку `Не указан токен бота`:

```bash
# Вариант 1: Создайте config.py
cp config.example.py config.py
# Отредактируйте и добавьте токен

# Вариант 2: Укажите токен в команде
telegram-diag full YOUR_BOT_TOKEN
```

### ImportError: No module named 'telegram_diagnostics'

```bash
pip install -e .
```

### CommandNotFound: telegram-diag

Убедитесь что виртуальное окружение активировано или используйте полный путь:
```bash
.venv/Scripts/telegram-diag.exe  # Windows
.venv/bin/telegram-diag  # Linux/Mac
```

### Проблемы с Pillow

Тесты загрузки файлов требуют Pillow:
```bash
pip install Pillow
```
