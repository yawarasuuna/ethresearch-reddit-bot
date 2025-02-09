# ETH Research Bot

A Reddit bot that monitors [ethresear.ch](https://ethresear.ch) for new research posts and automatically shares them to specified subreddits with proper attribution and formatting.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Features

- Automated monitoring of ethresear.ch/latest for new research posts
- Intelligent filtering of non-research content
- Automatic posting to Reddit with proper formatting
- Daily discussion thread integration
- Robust error handling and retry mechanisms
- Comprehensive logging
- Post history tracking to prevent duplicates

## Prerequisites

- Python 3.9 or higher
- Reddit API credentials (see [Setup](#setup))
- Virtual environment (recommended)
- pip package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/eth-research-bot.git
cd eth-research-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Setup

### Reddit API Credentials

1. Go to [Reddit's App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in the following:
   - Name: ETHResearchBot (or your preferred name)
   - App type: Script
   - Description: Bot that posts ETH research updates
   - About URL: Your GitHub repository URL
   - Redirect URI: http://localhost:8080

4. Create a `.env` file in the project root with your credentials:
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_bot_username
REDDIT_PASSWORD=your_bot_password # trying to figure out OAuth with reddit to avoid it
REDDIT_SUBREDDIT=your_test_subreddit
```

**Important**: Never commit your `.env` file to version control!

## Configuration

The bot's behavior can be customized through the `config.py` file:

```python
# Timing configuration
CHECK_INTERVAL = 300  # 5 minutes between checks

# Post formatting
POST_COMMENT_TEMPLATE = """
New post on http://EthResear.ch! Reddit thread [here]({reddit_url}), what do you guys think?

{title}

By: {authors}

🔗 https://ethresear.ch/t/{topic_id}
"""
```

## Usage

### Running the Bot

1. Ensure your virtual environment is activated
2. Run the bot:
```bash
python main.py
```

### Running Tests

Run the test suite:
```bash
python -m unittest discover tests
```

Run specific test file:
```bash
python -m unittest tests/test_bot.py
```

## Project Structure

```
eth-research-bot/
├── config.py          # Configuration and environment settings
├── main.py            # Main bot logic and entry point
├── reddit_poster.py   # Reddit API integration
├── scraper.py         # ETH Research scraping logic
├── requirements.txt   # Project dependencies
├── tests/             # Test suite
│   ├── __init__.py
│   └── test_bot.py
├── .env               # Environment variables (not in version control)
├── .gitignore
├── LICENSE
└── README.md
```

## Development

### Adding New Features

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Add tests for new functionality
4. Run the test suite
5. Create a pull request

### Code Style

This project follows PEP 8 guidelines with some modifications:
- Line length limit: 88 characters
- Use type hints for all function definitions
- Use docstrings for all classes and functions

## Logging

Logs are stored in `eth_research_bot.log` with the following levels:
- INFO: Normal operation events
- WARNING: Non-critical issues
- ERROR: Critical issues that need attention
- DEBUG: Detailed debugging information

## Error Handling

The bot implements robust error handling:
- Network failures: Automatic retry with exponential backoff
- Reddit API limits: Rate limiting compliance
- Scraping errors: Graceful degradation
- Configuration errors: Clear error messages

## Production Deployment

For production deployment:

1. Update `.env` with production credentials
2. Set `REDDIT_SUBREDDIT` to your target subreddit
3. Consider using a process manager (e.g., supervisor, systemd)
4. Set up monitoring and alerting
5. Configure proper logging rotation

Example systemd service file:
```ini
[Unit]
Description=ETH Research Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/path/to/eth-research-bot
Environment=PYTHONPATH=/path/to/eth-research-bot
ExecStart=/path/to/venv/bin/python main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

Common issues and solutions:

1. **Bot not posting**
   - Check Reddit API credentials
   - Verify subreddit permissions
   - Check rate limits

2. **Missing posts**
   - Verify ethresear.ch accessibility
   - Check filtering settings
   - Review log files

3. **Duplicate posts**
   - Clear post history file
   - Check topic ID extraction

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

Please ensure:
- Tests pass
- Code is properly documented
- Changes are backwards compatible
- New features include tests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- ETH Research community
- @ethresearchbot team
- Reddit API developers
- Beautiful Soup maintainers
- PRAW developers

## Versioning

We use [SemVer](http://semver.org/) for versioning. For available versions, see the [tags on this repository](https://github.com/yawarasuuna/ethresearch-socials-bot/tags).

## Authors

* **yawarasuuna** - *Initial work* - [YourGithub](https://github.com/yawarasuuna)

## Support

For support, please:
1. Check existing issues
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Log output

---

**Note**: This bot is not officially affiliated with the Ethereum Research team, ethresear.ch or @ethresearchbot on twitter.