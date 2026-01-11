"""Quick network connectivity check for Telegram Bot API."""

import asyncio
import aiohttp
import time
from typing import List, Tuple


async def quick_check(bot_token: str, attempts: int = 5) -> Tuple[List[float], List[str]]:
    """
    Perform quick Telegram API connectivity check.
    
    Args:
        bot_token: Telegram Bot API token
        attempts: Number of attempts to perform
        
    Returns:
        Tuple of (successful latencies, errors)
    """
    api_url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    print("🔍 Быстрая проверка Telegram API...\n")
    
    results: List[float] = []
    errors: List[str] = []
    
    for i in range(attempts):
        try:
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    api_url, 
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    await resp.json()
                    elapsed = (time.time() - start) * 1000
                    results.append(elapsed)
                    status = "✅" if elapsed < 500 else "⚠️" if elapsed < 1000 else "❌"
                    print(f"{status} Попытка {i+1}/{attempts}: {elapsed:.2f}ms")
        except asyncio.TimeoutError:
            print(f"❌ Попытка {i+1}/{attempts}: Таймаут (>10s)")
            errors.append("timeout")
        except Exception as e:
            print(f"❌ Попытка {i+1}/{attempts}: Ошибка - {e}")
            errors.append(str(e))
        
        if i < attempts - 1:
            await asyncio.sleep(0.5)
    
    print("\n" + "=" * 50)
    
    if results:
        avg = sum(results) / len(results)
        min_lat = min(results)
        max_lat = max(results)
        
        print(f"📊 Статистика:")
        print(f"   Успешных запросов: {len(results)}/{attempts}")
        print(f"   Средняя задержка: {avg:.2f}ms")
        print(f"   Мин/Макс: {min_lat:.2f}ms / {max_lat:.2f}ms")
        
        if avg < 300:
            print(f"\n✅ Состояние: ОТЛИЧНОЕ")
        elif avg < 500:
            print(f"\n✅ Состояние: ХОРОШЕЕ")
        elif avg < 1000:
            print(f"\n⚠️  Состояние: УДОВЛЕТВОРИТЕЛЬНОЕ (повышенная задержка)")
        else:
            print(f"\n❌ Состояние: ПЛОХОЕ (высокая задержка)")
            print(f"   Рекомендация: Увеличьте таймауты в ваших скриптах")
    
    if errors:
        print(f"\n❌ Ошибок: {len(errors)}/{attempts}")
        print(f"   Рекомендация: Проверьте соединение или запустите полную диагностику")
    
    print("=" * 50 + "\n")
    
    return results, errors


async def run_quick_check(bot_token: str) -> None:
    """Run quick check CLI."""
    try:
        await quick_check(bot_token)
    except KeyboardInterrupt:
        print("\n\n⚠️  Проверка прервана")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m telegram_diagnostics.quick_check <BOT_TOKEN>")
        sys.exit(1)
    
    token = sys.argv[1]
    asyncio.run(run_quick_check(token))
