"""CLI interface for telegram-network-diagnostics."""

import argparse
import asyncio
import sys
from pathlib import Path

from .quick_check import run_quick_check
from .monitor import run_monitor
from .diagnostics import run_diagnostics


def load_config():
    """Load bot token and chat_id from config.py if available."""
    try:
        # Try to import from current directory
        config_path = Path.cwd() / "config.py"
        if config_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", config_path)
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            
            bot_token = getattr(config, 'BOT_TOKEN', None)
            chat_id = getattr(config, 'CHAT_ID', None)
            
            if bot_token:
                return bot_token, chat_id
    except Exception:
        pass
    
    return None, None


def main() -> None:
    """Main CLI entry point."""
    # Try to load config
    config_token, config_chat_id = load_config()
    
    parser = argparse.ArgumentParser(
        prog='telegram-diag',
        description='CLI tools for diagnosing and monitoring Telegram Bot API network connections',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick connectivity check
  telegram-diag check YOUR_BOT_TOKEN
  
  # Or use config.py
  telegram-diag check
  
  # Start continuous monitoring (5s interval)
  telegram-diag monitor YOUR_BOT_TOKEN
  
  # Monitor with custom interval (10s)
  telegram-diag monitor YOUR_BOT_TOKEN --interval 10
  
  # Full diagnostics (without file uploads)
  telegram-diag full YOUR_BOT_TOKEN
  
  # Full diagnostics with file upload tests
  telegram-diag full YOUR_BOT_TOKEN --chat-id YOUR_CHAT_ID
  
  # Or use config.py for all commands
  telegram-diag full
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Quick connectivity check (5 attempts)'
    )
    check_parser.add_argument(
        'token',
        nargs='?',
        default=config_token,
        help='Telegram Bot API token (optional if config.py exists)'
    )
    
    # Monitor command
    monitor_parser = subparsers.add_parser(
        'monitor',
        help='Continuous network monitoring'
    )
    monitor_parser.add_argument(
        'token',
        nargs='?',
        default=config_token,
        help='Telegram Bot API token (optional if config.py exists)'
    )
    monitor_parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Seconds between checks (default: 5)'
    )
    monitor_parser.add_argument(
        '--history',
        type=int,
        default=60,
        help='Number of checks to keep in history (default: 60)'
    )
    
    # Full diagnostics command
    full_parser = subparsers.add_parser(
        'full',
        help='Comprehensive network diagnostics'
    )
    full_parser.add_argument(
        'token',
        nargs='?',
        default=config_token,
        help='Telegram Bot API token (optional if config.py exists)'
    )
    full_parser.add_argument(
        '--chat-id',
        type=int,
        default=config_chat_id,
        help='Chat ID for file upload tests (optional, can be set in config.py)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Check if token is provided
    if not args.token:
        print("❌ Ошибка: Не указан токен бота")
        print("\nВарианты:")
        print("  1. Создайте config.py с BOT_TOKEN")
        print("  2. Укажите токен в команде: telegram-diag", args.command, "YOUR_BOT_TOKEN")
        sys.exit(1)
    
    # Show config info if loaded
    if config_token:
        print("✅ Токен загружен из config.py")
        if config_chat_id and args.command == 'full':
            print(f"✅ Chat ID загружен из config.py: {config_chat_id}")
    
    # Execute command
    try:
        if args.command == 'check':
            asyncio.run(run_quick_check(args.token))
        elif args.command == 'monitor':
            asyncio.run(run_monitor(args.token, args.interval, args.history))
        elif args.command == 'full':
            asyncio.run(run_diagnostics(args.token, args.chat_id))
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
