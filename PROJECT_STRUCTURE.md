# Telegram Network Diagnostics - Project Structure

## 📁 Структура проекта

```
telegram-network-diagnostics/
├── .github/
│   └── copilot-instructions.md    # Инструкции для GitHub Copilot
├── telegram_diagnostics/          # Основной пакет
│   ├── __init__.py               # Инициализация пакета
│   ├── cli.py                    # CLI интерфейс (argparse)
│   ├── diagnostics.py            # Полная диагностика
│   ├── monitor.py                # Непрерывный мониторинг
│   └── quick_check.py            # Быстрая проверка
├── .gitignore                    # Git ignore файл
├── CHANGELOG.md                  # История изменений
├── config.example.py             # Пример конфигурации
├── LICENSE                       # MIT License
├── pyproject.toml                # Конфигурация проекта (PEP 517/518)
├── QUICKSTART.md                 # Быстрый старт
├── quickstart.py                 # Скрипт быстрого запуска
├── README.md                     # Основная документация
└── requirements.txt              # Зависимости проекта
```

## 🚀 Основные компоненты

### 1. CLI Module (`cli.py`)

- Единая точка входа для всех команд
- Использует argparse для парсинга аргументов
- Три команды: `check`, `monitor`, `full`
- Поддержка параметров: interval, history, chat-id

### 2. Quick Check (`quick_check.py`)

- Быстрая проверка соединения (5 попыток)
- Измерение задержки API
- Статистика: среднее, мин, макс
- Оценка состояния соединения

### 3. Monitor (`monitor.py`)

- Непрерывный мониторинг соединения
- Настраиваемый интервал проверки
- История проверок (настраиваемый размер)
- Статистика каждые 20 проверок
- Гистограмма распределения задержек
- Автосохранение результатов

### 4. Diagnostics (`diagnostics.py`)

- Комплексная диагностика сети
- Тесты: DNS, TCP, API latency, connection pool
- Опциональные тесты загрузки файлов
- Детальное логирование
- Сохранение результатов в файл

## 📦 Установка и использование

### Установка в режиме разработки

```bash
cd telegram-network-diagnostics
pip install -e .
```

### CLI команды

```bash
# Быстрая проверка
telegram-diag check YOUR_BOT_TOKEN

# Мониторинг
telegram-diag monitor YOUR_BOT_TOKEN --interval 5

# Полная диагностика
telegram-diag full YOUR_BOT_TOKEN --chat-id YOUR_CHAT_ID
```

### С использованием config.py

```bash
# Создать config.py из примера
cp config.example.py config.py
# Отредактировать и добавить токен

# Запуск через quickstart
python quickstart.py check
python quickstart.py monitor
python quickstart.py full
```

## 🔧 Конфигурация

### pyproject.toml

- Метаданные проекта
- Зависимости
- Entry points для CLI
- Настройки инструментов (black, mypy)

### requirements.txt

- aiohttp >= 3.9.0
- Pillow >= 10.0.0

## 📊 Возможности

### ✅ Реализовано

- [x] Быстрая проверка соединения
- [x] Непрерывный мониторинг
- [x] Полная диагностика
- [x] DNS тесты
- [x] TCP тесты
- [x] API latency тесты
- [x] Connection pool тесты
- [x] File upload тесты
- [x] CLI интерфейс
- [x] Автосохранение результатов
- [x] Статистика и гистограммы
- [x] Документация

### 🔮 Возможные улучшения

- [ ] Поддержка конфигурационных файлов (YAML/JSON)
- [ ] Экспорт результатов в разные форматы (JSON, CSV)
- [ ] Web dashboard для мониторинга
- [ ] Интеграция с системами мониторинга (Prometheus, Grafana)
- [ ] Алерты при проблемах (email, Telegram)
- [ ] Batch тестирование нескольких ботов
- [ ] Исторический анализ трендов
- [ ] Автоматические рекомендации по оптимизации

## 🧪 Тестирование

### Текущее состояние

Проект протестирован вручную:

- CLI команды работают
- Все модули импортируются корректно
- Entry points установлены

### Будущие тесты

```bash
# После добавления тестов
pytest
pytest --cov=telegram_diagnostics
```

## 📝 Документация

- **README.md** - Основная документация
- **QUICKSTART.md** - Быстрый старт
- **CHANGELOG.md** - История версий
- **Docstrings** - В каждом модуле и функции

## 🤝 Контрибьюция

1. Fork проекта
2. Создать feature branch
3. Commit изменений
4. Push в branch
5. Открыть Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

## 🎯 Цели проекта

1. **Простота использования** - CLI интерфейс, минимум зависимостей
2. **Информативность** - Детальная диагностика и логи
3. **Универсальность** - Работает с любым Telegram ботом
4. **Расширяемость** - Модульная архитектура
5. **Надежность** - Обработка ошибок, повторные попытки

## 📞 Поддержка

- Issues: GitHub Issues
- Документация: README.md, QUICKSTART.md
- Примеры: В CLI help и документации
