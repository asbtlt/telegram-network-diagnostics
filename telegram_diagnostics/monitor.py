"""Continuous network monitoring for Telegram Bot API."""

import asyncio
import aiohttp
import time
from datetime import datetime
from collections import deque
from typing import Tuple, Optional, List


class TelegramNetworkMonitor:
    """Continuous network monitoring for Telegram Bot API."""
    
    def __init__(self, bot_token: str, interval: int = 5, history_size: int = 60):
        """
        Initialize monitor.
        
        Args:
            bot_token: Telegram Bot API token
            interval: Seconds between checks
            history_size: Number of checks to keep in history
        """
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        self.interval = interval
        self.history: deque = deque(maxlen=history_size)
        self.errors: List[Tuple[str, str]] = []
        self.running = True
        
    async def check_once(self) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Perform single connectivity check.
        
        Returns:
            Tuple of (success, latency_ms, error_message)
        """
        try:
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    await resp.json()
                    elapsed = (time.time() - start) * 1000
                    return (True, elapsed, None)
        except asyncio.TimeoutError:
            return (False, None, "Timeout")
        except Exception as e:
            return (False, None, str(e))
    
    def get_status_symbol(self, latency: Optional[float]) -> str:
        """Get status emoji based on latency."""
        if latency is None:
            return "❌"
        elif latency < 300:
            return "🟢"
        elif latency < 500:
            return "🟡"
        elif latency < 1000:
            return "🟠"
        else:
            return "🔴"
    
    def print_stats(self) -> None:
        """Print statistics for recent checks."""
        if not self.history:
            return
        
        successful = [h for h in self.history if h[0]]
        failed = [h for h in self.history if not h[0]]
        
        print("\n" + "=" * 70)
        print(f"📊 Статистика за последние {len(self.history)} проверок:")
        print("=" * 70)
        
        if successful:
            latencies = [h[1] for h in successful]
            avg = sum(latencies) / len(latencies)
            min_lat = min(latencies)
            max_lat = max(latencies)
            
            print(f"✅ Успешных: {len(successful)}/{len(self.history)} "
                  f"({len(successful)/len(self.history)*100:.1f}%)")
            print(f"📈 Задержка: {avg:.2f}ms (мин: {min_lat:.2f}ms, макс: {max_lat:.2f}ms)")
            
            # Histogram of latencies
            ranges = [
                (0, 300, "🟢 < 300ms", 0),
                (300, 500, "🟡 300-500ms", 0),
                (500, 1000, "🟠 500-1000ms", 0),
                (1000, float('inf'), "🔴 > 1000ms", 0)
            ]
            
            for lat in latencies:
                for i, (min_r, max_r, _, _) in enumerate(ranges):
                    if min_r <= lat < max_r:
                        ranges[i] = (min_r, max_r, ranges[i][2], ranges[i][3] + 1)
            
            print("\n📊 Распределение задержек:")
            for _, _, label, count in ranges:
                if count > 0:
                    bar = "█" * (count * 50 // len(successful))
                    print(f"   {label:15} {count:3d} {bar}")
        
        if failed:
            print(f"\n❌ Ошибок: {len(failed)}/{len(self.history)} "
                  f"({len(failed)/len(self.history)*100:.1f}%)")
            
            # Error types
            error_types = {}
            for _, _, error in failed:
                error_types[error] = error_types.get(error, 0) + 1
            
            print("\n🔍 Типы ошибок:")
            for error_type, count in error_types.items():
                print(f"   {error_type}: {count}")
        
        print("=" * 70)
    
    async def monitor(self) -> None:
        """Main monitoring loop."""
        print("🔍 Запуск непрерывного мониторинга Telegram API")
        print(f"   Интервал проверки: {self.interval}s")
        print(f"   История: последние {self.history.maxlen} проверок")
        print("\n   Нажмите Ctrl+C для остановки и вывода статистики")
        print("   Нажмите Ctrl+C дважды для немедленного выхода\n")
        print("=" * 70)
        
        check_count = 0
        
        try:
            while self.running:
                check_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                success, latency, error = await self.check_once()
                self.history.append((success, latency, error))
                
                status = self.get_status_symbol(latency)
                
                if success:
                    print(f"[{timestamp}] {status} Проверка #{check_count:4d}: {latency:7.2f}ms")
                else:
                    print(f"[{timestamp}] {status} Проверка #{check_count:4d}: ОШИБКА - {error}")
                    self.errors.append((timestamp, error))
                
                # Show warnings
                if success and latency > 1000:
                    print(f"           ⚠️  ВЫСОКАЯ ЗАДЕРЖКА!")
                
                # Show stats every 20 checks
                if check_count % 20 == 0:
                    self.print_stats()
                
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Остановка мониторинга...")
            self.running = False
            
            # Print final stats
            self.print_stats()
            
            # Save results
            self.save_results()
    
    def save_results(self) -> None:
        """Save monitoring results to file."""
        filename = f"telegram_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("TELEGRAM API NETWORK MONITOR RESULTS\n")
            f.write(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Интервал: {self.interval}s\n")
            f.write(f"Всего проверок: {len(self.history)}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("История проверок:\n")
            f.write("-" * 80 + "\n")
            for i, (success, latency, error) in enumerate(self.history, 1):
                if success:
                    f.write(f"{i:4d}. ✅ {latency:.2f}ms\n")
                else:
                    f.write(f"{i:4d}. ❌ {error}\n")
            
            if self.errors:
                f.write("\n" + "=" * 80 + "\n")
                f.write("Список ошибок:\n")
                f.write("-" * 80 + "\n")
                for timestamp, error in self.errors:
                    f.write(f"[{timestamp}] {error}\n")
        
        print(f"\n📄 Результаты сохранены в {filename}")


async def run_monitor(bot_token: str, interval: int = 5, history_size: int = 60) -> None:
    """Run monitoring CLI."""
    monitor = TelegramNetworkMonitor(bot_token, interval, history_size)
    await monitor.monitor()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m telegram_diagnostics.monitor <BOT_TOKEN> [interval]")
        sys.exit(1)
    
    token = sys.argv[1]
    interval_arg = 5
    
    if len(sys.argv) > 2:
        try:
            interval_arg = int(sys.argv[2])
        except ValueError:
            print("⚠️  Неверный интервал, используется 5s")
    
    try:
        asyncio.run(run_monitor(token, interval_arg))
    except KeyboardInterrupt:
        print("\n\n⚠️  Мониторинг прерван")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
