"""Comprehensive network diagnostics for Telegram Bot API."""

import asyncio
import aiohttp
import socket
import time
from datetime import datetime
from io import BytesIO
from typing import List, Tuple, Optional

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class TelegramNetworkDiagnostics:
    """Comprehensive network diagnostics for Telegram Bot API."""
    
    TELEGRAM_API_HOST = 'api.telegram.org'
    
    def __init__(self, bot_token: str, test_chat_id: Optional[int] = None):
        """
        Initialize diagnostics.
        
        Args:
            bot_token: Telegram Bot API token
            test_chat_id: Optional chat ID for file upload tests
        """
        self.bot_token = bot_token
        self.test_chat_id = test_chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.results: List[Tuple[str, str, str]] = []
        
    def log(self, message: str, status: str = "INFO") -> None:
        """Log message with timestamp."""
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
    
    async def test_dns_resolution(self) -> bool:
        """Test DNS resolution for Telegram API."""
        self.log(f"Проверка DNS разрешения для {self.TELEGRAM_API_HOST}", "TEST")
        
        try:
            start = time.time()
            
            loop = asyncio.get_event_loop()
            addrinfo = await loop.run_in_executor(
                None,
                socket.getaddrinfo,
                self.TELEGRAM_API_HOST,
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
    
    async def test_tcp_connection(self) -> bool:
        """Test TCP connection to Telegram API."""
        self.log(f"Проверка TCP соединения с {self.TELEGRAM_API_HOST}:443", "TEST")
        
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            result = sock.connect_ex((self.TELEGRAM_API_HOST, 443))
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
    
    async def test_api_latency(self) -> bool:
        """Test API latency using getMe method."""
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
                f"Средняя задержка: {avg_latency:.2f}ms "
                f"(мин: {min_latency:.2f}ms, макс: {max_latency:.2f}ms)",
                "OK"
            )
            
            if avg_latency > 1000:
                self.log("⚠️  Высокая задержка API (>1000ms)", "WARNING")
            
            return True
        else:
            self.log("Не удалось измерить задержку API", "ERROR")
            return False
    
    async def test_connection_pool(self) -> bool:
        """Test connection pool with parallel requests."""
        self.log("Тест пула соединений (10 параллельных запросов)", "TEST")
        
        async def make_request(session: aiohttp.ClientSession, idx: int) -> float:
            try:
                start = time.time()
                async with session.get(
                    f"{self.api_url}/getMe",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    await resp.json()
                    return (time.time() - start) * 1000
            except Exception as e:
                self.log(f"  Запрос {idx}: Ошибка - {e}", "ERROR")
                return -1
        
        try:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=10)
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [make_request(session, i) for i in range(10)]
                results = await asyncio.gather(*tasks)
                
                successful = [r for r in results if r > 0]
                if successful:
                    avg = sum(successful) / len(successful)
                    self.log(
                        f"Успешно {len(successful)}/10 запросов, "
                        f"средняя задержка: {avg:.2f}ms",
                        "OK"
                    )
                    return True
                else:
                    self.log("Все запросы завершились с ошибкой", "ERROR")
                    return False
        except Exception as e:
            self.log(f"Ошибка теста пула соединений: {e}", "ERROR")
            return False
    
    async def test_file_upload(self) -> bool:
        """Test file upload speed (requires test_chat_id and PIL)."""
        if not self.test_chat_id:
            self.log("Пропуск теста загрузки (не указан test_chat_id)", "WARNING")
            return None
        
        if not HAS_PIL:
            self.log("Пропуск теста загрузки (не установлена библиотека Pillow)", "WARNING")
            return None
        
        self.log("Тест скорости загрузки файла (1MB)", "TEST")
        
        try:
            # Create test image
            img = Image.new('RGB', (1000, 1000), color='red')
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            
            # Pad to 1MB
            target_size = 1 * 1024 * 1024
            while buffer.tell() < target_size:
                buffer.write(b'\x00')
            
            buffer.seek(0)
            buffer.name = "test_1mb.jpg"
            
            start = time.time()
            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                form_data.add_field('chat_id', str(self.test_chat_id))
                form_data.add_field('photo', buffer, filename=buffer.name)
                
                async with session.post(
                    f"{self.api_url}/sendPhoto",
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    result = await resp.json()
                    if result.get('ok'):
                        elapsed = time.time() - start
                        speed = (target_size / 1024 / 1024) / elapsed * 8
                        self.log(
                            f"Загрузка 1MB за {elapsed:.2f}s ({speed:.2f} Mbps)",
                            "OK"
                        )
                        return True
                    else:
                        self.log(f"Ошибка загрузки: {result.get('description')}", "ERROR")
                        return False
        except asyncio.TimeoutError:
            self.log("Таймаут при загрузке файла (>120s)", "ERROR")
            return False
        except Exception as e:
            self.log(f"Ошибка теста загрузки: {e}", "ERROR")
            return False
    
    async def run_all_tests(self) -> None:
        """Run all diagnostic tests."""
        self.log("=" * 60, "INFO")
        self.log("ДИАГНОСТИКА TELEGRAM BOT API СЕТИ", "INFO")
        self.log("=" * 60, "INFO")
        
        tests = [
            ("DNS разрешение", self.test_dns_resolution()),
            ("TCP соединение", self.test_tcp_connection()),
            ("Задержка API", self.test_api_latency()),
            ("Пул соединений", self.test_connection_pool()),
        ]
        
        if self.test_chat_id:
            tests.append(("Загрузка файла", self.test_file_upload()))
        
        for _, test_coro in tests:
            self.log(f"\n{'=' * 60}", "INFO")
            await test_coro
        
        self.log("\n" + "=" * 60, "INFO")
        self.log("ДИАГНОСТИКА ЗАВЕРШЕНА", "INFO")
        self.log("=" * 60, "INFO")
        
        self.save_results()
    
    def save_results(self) -> None:
        """Save diagnostic results to file."""
        filename = f"telegram_network_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("TELEGRAM BOT API NETWORK DIAGNOSTICS\n")
            f.write(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for timestamp, status, message in self.results:
                f.write(f"[{timestamp}] {status}: {message}\n")
        
        self.log(f"\n📄 Результаты сохранены в {filename}", "OK")


async def run_diagnostics(bot_token: str, test_chat_id: Optional[int] = None) -> None:
    """Run diagnostics CLI."""
    print("\n🔍 Диагностика сетевых проблем Telegram Bot API\n")
    
    if test_chat_id:
        print(f"✅ Используется test_chat_id: {test_chat_id}")
    else:
        print("ℹ️  Для полного тестирования укажите chat_id")
        print("   (где chat_id - ваш Telegram ID для тестовой отправки файлов)\n")
    
    diagnostics = TelegramNetworkDiagnostics(bot_token, test_chat_id)
    await diagnostics.run_all_tests()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m telegram_diagnostics.diagnostics <BOT_TOKEN> [chat_id]")
        sys.exit(1)
    
    token = sys.argv[1]
    chat_id = None
    
    if len(sys.argv) > 2:
        try:
            chat_id = int(sys.argv[2])
        except ValueError:
            print("⚠️  Неверный формат chat_id, пропускаются тесты загрузки")
    
    try:
        asyncio.run(run_diagnostics(token, chat_id))
    except KeyboardInterrupt:
        print("\n\n⚠️  Диагностика прервана пользователем")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
