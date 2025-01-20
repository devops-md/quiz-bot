# Simple telegram bot to publish quizes in community telegram channel

## Requirements

ENV Variables

- `BOT_TOKEN` - Telegram bot token
- `CHANNEL_ID` - Telegram chanell where to publish messages. Bot must be administrator of channel
- `THREAD_ID` - Thread in which to put messages
- `MCQ_URL` - URL of json with questions
- `PUBLISH_TIME` - time to publish quizes in format `HH:mm`
- `TZ` - timezone in which to operate (eq."Europe/Chisinau")

## Questions

Questions must be published in an available resource in format

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

At publish time bot will select an randomized question and whill shuffle response options

## Run

```bash
pyhon quiz_bot.py
```

## Build docker image

```bash
docker build --progress plain  --platform linux/amd64 -t aprescornic/telegram_quizz:1.0.0 .
```

## RUN in docker

```bash
docker run -it --rm -e CHANNEL_ID="-100Your Chanel ID" -e BOT_TOKEN="Your Bot Token" -e THREAD_ID="2" -e TZ="Europe/Chisinau" -e MCQ_URL="https://raw.githubusercontent.com/devops-md/quiz-bot/refs/heads/main/questions.json" aprescornic/telegram_quizz:1.0.0
```
