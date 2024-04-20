# Discord Certification Bot

This Discord bot retrieves certification details for games from the WATA Games API and displays them in an embed format.

## Features

- Fetches certification details for games from the WATA Games API.
- Displays certification information in an embed with relevant details.
- Updates a counter for the number of requests made to the bot.
- Supports custom commands and interactions.

## Setup

### Prerequisites

- Python 3.6 or higher
- Discord Bot Token
- Webhook URL for error logging

### Installation

1. Clone the repository:
git clone https://github.com/lorenzjan/certification_bot.git

2. Install dependencies:
pip install -r requirements.txt

3. Update the following variables in the code with your Discord Bot Token and Webhook URL:

```python
TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
WEBHOOK_URL = 'YOUR_WEBHOOK_URL'
COUNTER_FILE = 'YOUR_PATH/request_counter.txt'
```

4. Run the bot:
python bot.py

### Usage
The bot listens for commands prefixed with !. Here are the available commands:

- !wata [certification_number]: Fetches certification details for the specified certification number.
- !request_count: Displays the total number of requests made to the bot.

### Contributing
Contributions are welcome! If you want to contribute to this project, feel free to open a pull request.
