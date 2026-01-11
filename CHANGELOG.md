# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-11

### Added
- Initial release of telegram-network-diagnostics
- Quick connectivity check command (`check`)
- Continuous network monitoring command (`monitor`)
- Comprehensive diagnostics command (`full`)
- DNS resolution testing
- TCP connection testing
- API latency measurement
- Connection pool testing
- File upload speed testing (with Pillow)
- Automatic result saving to log files
- CLI interface with argparse
- Configuration file support (config.py)
- Quickstart script for easy usage
- Comprehensive README and documentation
- MIT License

### Features
- 🚀 Three operational modes: check, monitor, full
- 📊 Detailed statistics and histograms
- ⚡ Parallel request testing
- 🎨 Emoji indicators for status
- 💾 Automatic result persistence
- 🔧 Configurable intervals and history size
- 📝 Extensive logging and error reporting

### Dependencies
- Python 3.8+
- aiohttp >= 3.9.0
- Pillow >= 10.0.0 (optional, for file upload tests)

[0.1.0]: https://github.com/yourusername/telegram-network-diagnostics/releases/tag/v0.1.0
