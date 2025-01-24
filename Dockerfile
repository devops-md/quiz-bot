FROM python:alpine

WORKDIR /app/
RUN python -m pip install python-telegram-bot apscheduler

ADD quiz_bot.py .

CMD [ "python", "/app/quiz_bot.py" ]