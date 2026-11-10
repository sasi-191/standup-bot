# Standup Bot

A Telegram bot that collects daily standups from a team and shows them on a React dashboard.

## Features

- Bot asks 3 questions: yesterday, today and blockers
- /edit to redo today's standup, /cancel to stop
- Reminder at 10 AM (Mon-Fri) for people who have not sent their standup
- Manager gets a message when someone has a blocker
- Weekly summary every Friday at 6 PM
- Dashboard with today / all standups, search by name, filter by date and who is missing today

## Tech

Python, FastAPI, SQLAlchemy, PostgreSQL, python-telegram-bot, React

## Run

1. Make a bot with @BotFather and copy the token
2. Backend:

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add your bot token and database url in .env, then:

```
python models.py
uvicorn main:app --reload
```

3. Bot (new terminal): `python bot.py`
4. Dashboard (new terminal):

```
cd frontend
npm install
npm run dev
```
