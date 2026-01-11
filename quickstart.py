"""Quick start script - uses config.py if available."""

import sys

# Try to load config
try:
    from config import BOT_TOKEN, CHAT_ID
    print("✅ Загружен токен из config.py")
except ImportError:
    BOT_TOKEN = None
    CHAT_ID = None
    print("⚠️  config.py не найден")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("\nСоздайте файл config.py на основе config.example.py")
        print("или используйте команду напрямую:")
        print("  telegram-diag check YOUR_BOT_TOKEN\n")
        sys.exit(1)
    
    from telegram_diagnostics.cli import main
    
    # Add token to sys.argv if not provided
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['check', 'monitor', 'full']):
        command = sys.argv[1] if len(sys.argv) == 2 else 'check'
        sys.argv = ['telegram-diag', command, BOT_TOKEN]
        if CHAT_ID and command == 'full':
            sys.argv.extend(['--chat-id', str(CHAT_ID)])
    
    main()
