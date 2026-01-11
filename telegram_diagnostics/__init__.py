"""Telegram Network Diagnostics - CLI tools for monitoring Telegram Bot API."""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from .diagnostics import TelegramNetworkDiagnostics
from .monitor import TelegramNetworkMonitor
from .quick_check import quick_check

__all__ = [
    "TelegramNetworkDiagnostics",
    "TelegramNetworkMonitor",
    "quick_check",
]
