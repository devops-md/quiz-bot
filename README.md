# Telegram Quiz Bot

A modular Telegram bot that automatically publishes quiz polls to your Telegram channel. Supports multiple quiz data sources including JSON files and QuizAPI.io.

## Features

- 🎯 **Multiple Quiz Sources**: Support for JSON files and QuizAPI.io
- 🔄 **Auto-scheduling**: Configurable daily quiz publishing
- 🎲 **Random Selection**: Randomly picks questions and shuffles options
- 🐳 **Docker Ready**: Easy deployment with Docker and Docker Compose
- 🔒 **Security**: Enforces Telegram API limitations and validates quiz data
- 🏗️ **Modular Architecture**: Clean separation of concerns with provider pattern

## Architecture

```
src/
├── main.py              # Application entry point and scheduler
├── bot.py               # Telegram bot functionality
├── quiz.py              # Core quiz processing logic
├── provider_webjson.py  # JSON file quiz provider
└── provider_quizapi.py  # QuizAPI.io quiz provider
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `CHANNEL_ID` | Telegram channel ID (bot must be admin) | `-1001234567890` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `THREAD_ID` | - | Thread ID for topic-based channels |
| `QUIZ_SOURCE` | `json` | Quiz data source: `json` or `quizapi` |
| `PUBLISH_TIME` | `8:55` | Daily publish time in `HH:MM` format |
| `DEBUG_MODE` | `false` | Enable debug mode (sends quiz every minute) |
| `TZ` | `Europe/Chisinau` | Timezone for scheduling |

### JSON Provider Variables (when `QUIZ_SOURCE=json`)

| Variable | Default | Description |
|----------|---------|-------------|
| `MCQ_URL` | GitHub raw URL | URL to JSON file with quiz questions |

### QuizAPI Provider Variables (when `QUIZ_SOURCE=quizapi`)

| Variable | Default | Description |
|----------|---------|-------------|
| `QUIZAPI_KEY` | - | **Required** - Your QuizAPI.io API key |
| `QUIZAPI_ENDPOINT` | `https://quizapi.io/api/v1/questions` | QuizAPI endpoint URL |
| `DIFFICULTY` | `hard` | Quiz difficulty: `easy`, `medium`, or `hard` |

## Quiz Data Format

### JSON Format

Questions must be in an array with the following structure:

```json
[
    {
        "question": "Which Kubernetes object is used to ensure a specified number of pod replicas are running?",
        "options": [
            "Deployment",
            "StatefulSet",
            "DaemonSet",
            "ReplicaSet"
        ],
        "correct_option_id": 3,
        "explanation": "A ReplicaSet ensures that a specified number of pod replicas are running at all times."
    }
]
```

### QuizAPI.io

The bot automatically fetches questions from QuizAPI.io with:
- Random category selection from: Linux, bash, Docker, SQL, Code, DevOps, Postgres, Apache Kafka
- Configurable difficulty level
- Automatic filtering of multiple-choice questions (only single-answer quizzes)

## Telegram API Limitations

The bot enforces Telegram Quiz Poll limitations:
- **Question**: 1-300 characters (auto-truncated if longer)
- **Options**: 2-10 options, each 1-100 characters (auto-truncated if longer)
- **Explanation**: 0-200 characters (auto-truncated if longer)

## Installation & Usage

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/devops-md/quiz-bot.git
cd quiz-bot
```

2. Create a `.env` file:
```env
BOT_TOKEN=your_bot_token
CHANNEL_ID=-1001234567890
QUIZ_SOURCE=json
# or use QuizAPI
# QUIZ_SOURCE=quizapi
# QUIZAPI_KEY=your_api_key
```

3. Run with Docker Compose:
```bash
docker-compose up -d
```

### Using Docker

```bash
docker run -d \
  -e BOT_TOKEN="your_bot_token" \
  -e CHANNEL_ID="-1001234567890" \
  -e THREAD_ID="2" \
  -e QUIZ_SOURCE="json" \
  -e PUBLISH_TIME="8:55" \
  -e TZ="Europe/Chisinau" \
  aprescornic/telegram_quizz:latest
```

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export BOT_TOKEN="your_bot_token"
export CHANNEL_ID="-1001234567890"
```

3. Run the bot:
```bash
python -m src.main
```

## Building Docker Image

```bash
docker build -t aprescornic/telegram_quizz:latest .
```

Multi-platform build:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t aprescornic/telegram_quizz:latest .
```

## Categories (QuizAPI)

When using QuizAPI source, the bot randomly selects from these categories:
- Linux
- bash
- Docker
- SQL
- Code
- DevOps
- Postgres
- Apache Kafka

## CI/CD

The project includes GitHub Actions workflow for automatic Docker image building and publishing:
- Triggers on push to `main` branch
- Auto-increments version tags
- Publishes to Docker Hub
- Creates GitHub releases

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

DevOps Moldova Community
