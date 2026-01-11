#!/usr/bin/env python3
"""
Диагностика сетевых проблем при отправке медиафайлов в Telegram Bot API
"""

import asyncio
import aiohttp
import time
import os
import sys
from io import BytesIO
from datetime import datetime
import socket

# Добавляем путь к модулям проекта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import BOT_TOKENS
    bot_token = BOT_TOKENS[0] if isinstance(BOT_TOKENS, list) else BOT_TOKENS
except ImportError:
    print("⚠️  Не удалось загрузить токен из config.py")
    bot_token = input("Введите токен бота: ").strip()


class TelegramNetworkDiagnostics:
    """Диагностика сетевых проблем Telegram Bot API"""
    
    TELEGRAM_API_HOSTS = [
        'api.telegram.org',
        'core.telegram.org',
        '149.154.167.220'  # Один из IP-адресов Telegram
    ]
    
    def __init__(self, bot_token: str, test_chat_id: int = None):
        self.bot_token = bot_token
        self.test_chat_id = test_chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.results = []
        
    def log(self, message: str, status: str = "INFO"):
        """Логирование с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        symbols = {
            "INFO": "ℹ️",
            "OK": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "TEST": "🔍"
        }
        symbol = symbols.get(status, "•")
        print(f"[{timestamp}] {symbol} {message}")
        self.results.append((timestamp, status, message))
    
    async def test_dns_resolution(self):
        """Проверка разрешения DNS"""
        self.log("Проверка DNS разрешения для api.telegram.org", "TEST")
        
        try:
            start = time.time()
            
            # Используем стандартный socket.getaddrinfo
            loop = asyncio.get_event_loop()
            addrinfo = await loop.run_in_executor(
                None,
                socket.getaddrinfo,
                'api.telegram.org',
                443,
                socket.AF_INET
            )
            
            elapsed = (time.time() - start) * 1000
            
            ips = list(set([addr[4][0] for addr in addrinfo]))
            self.log(f"DNS разрешение успешно за {elapsed:.2f}ms: {', '.join(ips)}", "OK")
            return True
        except Exception as e:
            self.log(f"Ошибка DNS разрешения: {e}", "ERROR")
            return False
    
    async def test_tcp_connection(self):
        """Проверка TCP соединения с Telegram API"""
        self.log("Проверка TCP соединения с api.telegram.org:443", "TEST")
        
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            result = sock.connect_ex(('api.telegram.org', 443))
            elapsed = (time.time() - start) * 1000
            sock.close()
            
            if result == 0:
                self.log(f"TCP соединение успешно за {elapsed:.2f}ms", "OK")
                return True
            else:
                self.log(f"TCP соединение не удалось (код: {result})", "ERROR")
                return False
        except Exception as e:
            self.log(f"Ошибка TCP соединения: {e}", "ERROR")
            return False
    
    async def test_api_latency(self):
        """Проверка задержки API через getMe"""
        self.log("Измерение задержки API (getMe)", "TEST")
        
        latencies = []
        for i in range(5):
            try:
                start = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.api_url}/getMe",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        await resp.json()
                        elapsed = (time.time() - start) * 1000
                        latencies.append(elapsed)
                        self.log(f"  Попытка {i+1}/5: {elapsed:.2f}ms", "INFO")
                
                await asyncio.sleep(0.5)
            except Exception as e:
                self.log(f"  Попытка {i+1}/5: Ошибка - {e}", "ERROR")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            self.log(
                f"Средняя задержка: {avg_latency:.2f}ms (мин: {min_latency:.2f}ms, макс: {max_latency:.2f}ms)",
                "OK"
            )
            
            if avg_latency > 1000:
                self.log("⚠️  Высокая задержка API (>1000ms)", "WARNING")
            
            return True
        else:
            self.log("Не удалось измерить задержку API", "ERROR")
            return False
    
    async def test_file_upload_speed(self):
        """Тест скорости загрузки файлов разных размеров"""
        if not self.test_chat_id:
            self.log("Пропуск теста загрузки (не указан test_chat_id)", "WARNING")
            return None
        
        self.log("Тест скорости загрузки файлов", "TEST")
        
        # Тестовые размеры: 100KB, 1MB, 5MB, 10MB
        test_sizes = [
            (100 * 1024, "100KB"),
            (1 * 1024 * 1024, "1MB"),
            (5 * 1024 * 1024, "5MB"),
            (10 * 1024 * 1024, "10MB")
        ]
        
        results = []
        
        for size, label in test_sizes:
            try:
                # Создаем тестовое изображение (простой красный квадрат)
                from PIL import Image
                img = Image.new('RGB', (1000, 1000), color='red')
                buffer = BytesIO()
                
                # Заполняем до нужного размера
                img.save(buffer, format='JPEG', quality=95)
                
                # Дополняем данными до нужного размера
                while buffer.tell() < size:
                    buffer.write(b'\x00' * min(1024, size - buffer.tell()))
                
                buffer.seek(0)
                buffer.name = f"test_{label}.jpg"
                
                self.log(f"  Отправка файла {label}...", "INFO")
                
                start = time.time()
                async with aiohttp.ClientSession() as session:
                    form = aiohttp.FormData()
                    form.add_field('chat_id', str(self.test_chat_id))
                    form.add_field('document', buffer, filename=f"test_{label}.jpg")
                    
                    async with session.post(
                        f"{self.api_url}/sendDocument",
                        data=form,
                        timeout=aiohttp.ClientTimeout(total=120)
                    ) as resp:
                        result = await resp.json()
                        elapsed = time.time() - start
                        
                        if result.get('ok'):
                            speed_mbps = (size / 1024 / 1024) / elapsed * 8
                            self.log(
                                f"  {label}: {elapsed:.2f}s ({speed_mbps:.2f} Mbps)",
                                "OK"
                            )
                            results.append((label, elapsed, speed_mbps))
                        else:
                            self.log(
                                f"  {label}: Ошибка - {result.get('description')}",
                                "ERROR"
                            )
                
                await asyncio.sleep(1)
                
            except asyncio.TimeoutError:
                self.log(f"  {label}: Таймаут (>120s)", "ERROR")
            except Exception as e:
                self.log(f"  {label}: Ошибка - {e}", "ERROR")
        
        if results:
            avg_speed = sum(r[2] for r in results) / len(results)
            self.log(f"Средняя скорость загрузки: {avg_speed:.2f} Mbps", "OK")
            
            if avg_speed < 1.0:
                self.log("⚠️  Низкая скорость загрузки (<1 Mbps)", "WARNING")
            
            return True
        else:
            self.log("Не удалось завершить тесты загрузки", "ERROR")
            return False
    
    async def test_timeout_patterns(self):
        """Проверка паттернов таймаутов"""
        if not self.test_chat_id:
            self.log("Пропуск теста таймаутов (не указан test_chat_id)", "WARNING")
            return None
        
        self.log("Тест паттернов таймаутов", "TEST")
        
        # Тестируем с разными таймаутами
        timeout_values = [10, 30, 60, 120]
        
        for timeout_val in timeout_values:
            try:
                # Создаем небольшой тестовый файл
                from PIL import Image
                img = Image.new('RGB', (500, 500), color='blue')
                buffer = BytesIO()
                img.save(buffer, format='JPEG')
                buffer.seek(0)
                buffer.name = f"test_timeout_{timeout_val}s.jpg"
                
                self.log(f"  Тест с таймаутом {timeout_val}s...", "INFO")
                
                start = time.time()
                try:
                    async with aiohttp.ClientSession() as session:
                        form = aiohttp.FormData()
                        form.add_field('chat_id', str(self.test_chat_id))
                        form.add_field('photo', buffer)
                        
                        async with session.post(
                            f"{self.api_url}/sendPhoto",
                            data=form,
                            timeout=aiohttp.ClientTimeout(total=timeout_val)
                        ) as resp:
                            result = await resp.json()
                            elapsed = time.time() - start
                            
                            if result.get('ok'):
                                self.log(
                                    f"  {timeout_val}s: Успешно за {elapsed:.2f}s",
                                    "OK"
                                )
                            else:
                                self.log(
                                    f"  {timeout_val}s: Ошибка API - {result.get('description')}",
                                    "ERROR"
                                )
                except asyncio.TimeoutError:
                    elapsed = time.time() - start
                    self.log(
                        f"  {timeout_val}s: Таймаут после {elapsed:.2f}s",
                        "ERROR"
                    )
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.log(f"  {timeout_val}s: Исключение - {e}", "ERROR")
    
    async def test_connection_pool(self):
        """Тест пула соединений - множественные запросы"""
        self.log("Тест пула соединений (10 параллельных запросов)", "TEST")
        
        async def make_request(session, idx):
            try:
                start = time.time()
                async with session.get(
                    f"{self.api_url}/getMe",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    await resp.json()
                    elapsed = (time.time() - start) * 1000
                    return (idx, elapsed, True)
            except Exception as e:
                return (idx, 0, False)
        
        try:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=10)
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [make_request(session, i) for i in range(10)]
                results = await asyncio.gather(*tasks)
                
                successful = [r for r in results if r[2]]
                failed = [r for r in results if not r[2]]
                
                if successful:
                    avg_time = sum(r[1] for r in successful) / len(successful)
                    self.log(
                        f"Успешно: {len(successful)}/10 запросов, средняя задержка: {avg_time:.2f}ms",
                        "OK"
                    )
                
                if failed:
                    self.log(
                        f"Не удалось: {len(failed)}/10 запросов",
                        "ERROR"
                    )
                
                return len(successful) == 10
        except Exception as e:
            self.log(f"Ошибка теста пула соединений: {e}", "ERROR")
            return False
    
    async def test_bulk_upload_with_short_timeout(self):
        """Тест массовой отправки с коротким таймаутом (имитация проблемы)"""
        if not self.test_chat_id:
            self.log("Пропуск теста массовой отправки (не указан test_chat_id)", "WARNING")
            return None
        
        self.log("Тест массовой отправки: 10 файлов по 200KB с таймаутом 5s", "TEST")
        
        try:
            from PIL import Image
            
            # Создаем тестовое изображение 200KB
            img = Image.new('RGB', (800, 800), color='purple')
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            
            # Дополняем до 200KB
            target_size = 200 * 1024
            while buffer.tell() < target_size:
                buffer.write(b'\x00' * min(1024, target_size - buffer.tell()))
            
            base_image_data = buffer.getvalue()
            self.log(f"  Создан шаблон изображения: {len(base_image_data)/1024:.2f}KB", "INFO")
            
            successful = 0
            failed = 0
            timeout_errors = 0
            other_errors = 0
            timings = []
            
            start_total = time.time()
            
            for i in range(1, 11):
                try:
                    # Создаем новый BytesIO для каждой отправки
                    file_stream = BytesIO(base_image_data)
                    file_stream.name = f"bulk_test_{i}.jpg"
                    
                    self.log(f"  Отправка файла {i}/10...", "INFO")
                    
                    start = time.time()
                    async with aiohttp.ClientSession() as session:
                        form = aiohttp.FormData()
                        form.add_field('chat_id', str(self.test_chat_id))
                        form.add_field('document', file_stream)
                        
                        async with session.post(
                            f"{self.api_url}/sendDocument",
                            data=form,
                            timeout=aiohttp.ClientTimeout(total=5)  # Короткий таймаут!
                        ) as resp:
                            result = await resp.json()
                            elapsed = time.time() - start
                            
                            if result.get('ok'):
                                successful += 1
                                timings.append(elapsed)
                                self.log(
                                    f"    ✅ Файл {i}: Успешно за {elapsed:.2f}s",
                                    "OK"
                                )
                            else:
                                failed += 1
                                other_errors += 1
                                self.log(
                                    f"    ❌ Файл {i}: API ошибка - {result.get('description')}",
                                    "ERROR"
                                )
                
                except asyncio.TimeoutError:
                    failed += 1
                    timeout_errors += 1
                    elapsed = time.time() - start
                    self.log(
                        f"    ⏱️ Файл {i}: Таймаут после {elapsed:.2f}s (лимит: 5s)",
                        "ERROR"
                    )
                except Exception as e:
                    failed += 1
                    other_errors += 1
                    self.log(
                        f"    ❌ Файл {i}: Ошибка - {e}",
                        "ERROR"
                    )
                
                # Небольшая задержка между отправками
                await asyncio.sleep(0.3)
            
            total_elapsed = time.time() - start_total
            
            # Итоговая статистика
            self.log("\n" + "=" * 60, "INFO")
            self.log("📊 РЕЗУЛЬТАТЫ МАССОВОЙ ОТПРАВКИ:", "INFO")
            self.log("=" * 60, "INFO")
            self.log(f"✅ Успешно отправлено: {successful}/10 ({successful*10}%)", "OK" if successful > 7 else "WARNING")
            self.log(f"❌ Не удалось отправить: {failed}/10 ({failed*10}%)", "ERROR" if failed > 0 else "OK")
            
            if timeout_errors > 0:
                self.log(f"⏱️  Таймауты: {timeout_errors}", "ERROR")
            if other_errors > 0:
                self.log(f"❌ Другие ошибки: {other_errors}", "ERROR")
            
            if timings:
                avg_time = sum(timings) / len(timings)
                min_time = min(timings)
                max_time = max(timings)
                self.log(
                    f"⏱️  Время отправки успешных: мин={min_time:.2f}s, макс={max_time:.2f}s, средн={avg_time:.2f}s",
                    "INFO"
                )
            
            self.log(f"⏱️  Общее время теста: {total_elapsed:.2f}s", "INFO")
            self.log("=" * 60, "INFO")
            
            # Выводы и рекомендации
            if successful >= 9:
                self.log("✅ ОТЛИЧНО: Почти все файлы отправлены успешно", "OK")
                self.log("   Таймаут 5s достаточен для файлов 200KB", "INFO")
            elif successful >= 7:
                self.log("⚠️  УДОВЛЕТВОРИТЕЛЬНО: Большинство файлов отправлено", "WARNING")
                self.log("   Рекомендация: Увеличить таймаут до 10s для стабильности", "WARNING")
            elif successful >= 5:
                self.log("⚠️  ПЛОХО: Половина файлов не отправлена", "WARNING")
                self.log("   Рекомендация: Увеличить таймаут до 15-20s", "WARNING")
            else:
                self.log("❌ КРИТИЧНО: Большинство файлов не отправлено", "ERROR")
                self.log("   Рекомендация: Увеличить таймаут до 30s или проверить соединение", "ERROR")
            
            if timeout_errors > 0:
                self.log(f"\n💡 Для файлов 200KB наблюдается {timeout_errors} таймаутов при лимите 5s", "WARNING")
                self.log(f"   В result_sender.py для файлов ~10MB используется таймаут 120s", "INFO")
                self.log(f"   Это соотношение: 10MB/120s = ~0.083MB/s", "INFO")
                if timings:
                    actual_speed = (0.2 / avg_time)  # 0.2MB / время в секундах
                    self.log(f"   Фактическая скорость: ~{actual_speed:.3f}MB/s", "INFO")
                    if actual_speed < 0.083:
                        self.log(f"   ⚠️  Скорость ниже расчетной - возможны таймауты для больших файлов!", "WARNING")
            
            return successful >= 7
            
        except Exception as e:
            self.log(f"Критическая ошибка теста массовой отправки: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_real_worker_scenario(self):
        """Имитация реального сценария worker'а"""
        if not self.test_chat_id:
            self.log("Пропуск теста worker сценария (не указан test_chat_id)", "WARNING")
            return None
        
        self.log("Имитация реального worker сценария", "TEST")
        
        try:
            from PIL import Image
            
            # Создаем 3 изображения как в реальном worker
            images = []
            for i in range(3):
                img = Image.new('RGB', (1024, 1024), color=['red', 'green', 'blue'][i])
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)
                data = buffer.read()
                images.append(data)
            
            self.log(f"  Создано {len(images)} тестовых изображений", "INFO")
            
            # Сценарий 1: Отправка документа + фото (как в result_sender.py)
            self.log("  Сценарий 1: Документ + Фото", "INFO")
            
            start_total = time.time()
            
            for idx, img_data in enumerate(images, 1):
                try:
                    # Отправка документа
                    doc_start = time.time()
                    doc_stream = BytesIO(img_data)
                    doc_stream.name = f"test_doc_{idx}.jpg"
                    
                    async with aiohttp.ClientSession() as session:
                        form = aiohttp.FormData()
                        form.add_field('chat_id', str(self.test_chat_id))
                        form.add_field('document', doc_stream)
                        
                        async with session.post(
                            f"{self.api_url}/sendDocument",
                            data=form,
                            timeout=aiohttp.ClientTimeout(total=120)
                        ) as resp:
                            result = await resp.json()
                            doc_elapsed = time.time() - doc_start
                            
                            if result.get('ok'):
                                self.log(
                                    f"    Изображение {idx} документ: {doc_elapsed:.2f}s",
                                    "OK"
                                )
                            else:
                                self.log(
                                    f"    Изображение {idx} документ: Ошибка - {result.get('description')}",
                                    "ERROR"
                                )
                    
                    # Отправка фото
                    photo_start = time.time()
                    photo_stream = BytesIO(img_data)
                    photo_stream.name = f"test_photo_{idx}.jpg"
                    
                    async with aiohttp.ClientSession() as session:
                        form = aiohttp.FormData()
                        form.add_field('chat_id', str(self.test_chat_id))
                        form.add_field('photo', photo_stream)
                        
                        async with session.post(
                            f"{self.api_url}/sendPhoto",
                            data=form,
                            timeout=aiohttp.ClientTimeout(total=60)
                        ) as resp:
                            result = await resp.json()
                            photo_elapsed = time.time() - photo_start
                            
                            if result.get('ok'):
                                self.log(
                                    f"    Изображение {idx} фото: {photo_elapsed:.2f}s",
                                    "OK"
                                )
                            else:
                                self.log(
                                    f"    Изображение {idx} фото: Ошибка - {result.get('description')}",
                                    "ERROR"
                                )
                    
                except asyncio.TimeoutError:
                    self.log(f"    Изображение {idx}: Таймаут", "ERROR")
                except Exception as e:
                    self.log(f"    Изображение {idx}: Ошибка - {e}", "ERROR")
                
                await asyncio.sleep(0.5)
            
            total_elapsed = time.time() - start_total
            self.log(
                f"Общее время сценария: {total_elapsed:.2f}s",
                "OK" if total_elapsed < 60 else "WARNING"
            )
            
            return True
            
        except Exception as e:
            self.log(f"Ошибка worker сценария: {e}", "ERROR")
            return False
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        self.log("=" * 60, "INFO")
        self.log("ДИАГНОСТИКА TELEGRAM BOT API СЕТИ", "INFO")
        self.log("=" * 60, "INFO")
        
        tests = [
            ("DNS разрешение", self.test_dns_resolution()),
            ("TCP соединение", self.test_tcp_connection()),
            ("Задержка API", self.test_api_latency()),
            ("Пул соединений", self.test_connection_pool()),
        ]
        
        # Тесты требующие test_chat_id
        if self.test_chat_id:
            tests.extend([
                ("Массовая отправка (5s таймаут)", self.test_bulk_upload_with_short_timeout()),
                ("Скорость загрузки", self.test_file_upload_speed()),
                ("Паттерны таймаутов", self.test_timeout_patterns()),
                ("Worker сценарий", self.test_real_worker_scenario()),
            ])
        
        for test_name, test_coro in tests:
            self.log(f"\n{'=' * 60}", "INFO")
            await test_coro
        
        self.log("\n" + "=" * 60, "INFO")
        self.log("ДИАГНОСТИКА ЗАВЕРШЕНА", "INFO")
        self.log("=" * 60, "INFO")
        
        # Сохраняем результаты
        self.save_results()
    
    def save_results(self):
        """Сохранение результатов в файл"""
        filename = f"telegram_network_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("TELEGRAM BOT API NETWORK DIAGNOSTICS\n")
            f.write(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for timestamp, status, message in self.results:
                f.write(f"[{timestamp}] [{status}] {message}\n")
        
        self.log(f"\n📄 Результаты сохранены в {filename}", "OK")


async def main():
    """Главная функция"""
    print("\n🔍 Диагностика сетевых проблем Telegram Bot API\n")
    
    # Получаем test_chat_id для тестов загрузки
    test_chat_id = None
    if len(sys.argv) > 1:
        try:
            test_chat_id = int(sys.argv[1])
            print(f"✅ Используется test_chat_id: {test_chat_id}")
        except ValueError:
            print("⚠️  Неверный формат chat_id, пропускаются тесты загрузки")
    else:
        print("ℹ️  Для полного тестирования запустите: python diagnose_telegram_network.py YOUR_CHAT_ID")
        print("   (где YOUR_CHAT_ID - ваш Telegram ID для тестовой отправки файлов)\n")
    
    diagnostics = TelegramNetworkDiagnostics(bot_token, test_chat_id)
    await diagnostics.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Диагностика прервана пользователем")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
