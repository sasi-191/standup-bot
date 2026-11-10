import os
from datetime import time
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from database import Base, SessionLocal, engine
from models import Member, Standup
from standup_logic import is_real_blocker, missing_members, save_member, todays_standup, week_summary_text

load_dotenv()

INDIA = ZoneInfo("Asia/Kolkata")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

questions = [
    "What did you do yesterday?",
    "What will you do today?",
    "Any blockers?",
]

user_steps = {}
user_answers = {}


async def ask_first_question(update, user_id):
    user_steps[user_id] = 1
    user_answers[user_id] = []
    await update.message.reply_text(questions[0])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    save_member(db, update.effective_user.id, update.effective_user.first_name)
    db.close()
    await update.message.reply_text(
        "Hi! I collect the daily standup.\n"
        "Send any message to start, /edit to change today's answers, /cancel to stop."
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_steps[user_id] = 0
    user_answers[user_id] = []
    await update.message.reply_text("Cancelled. Send any message to start again.")


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deletes today's standup and asks the questions again."""
    user_id = update.effective_user.id
    db = SessionLocal()
    old = todays_standup(db, user_id)
    if old is not None:
        db.delete(old)
        db.commit()
    db.close()
    await update.message.reply_text("Ok, let's redo today's standup.")
    await ask_first_question(update, user_id)


async def tell_manager_about_blocker(context, name, blocker):
    if MANAGER_CHAT_ID:
        await context.bot.send_message(chat_id=MANAGER_CHAT_ID,
                                       text="Blocker from " + name + ": " + blocker)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    message_text = update.message.text

    db = SessionLocal()
    save_member(db, user_id, user_name)
    db.close()

    step = user_steps.get(user_id, 0)

    if step == 0:
        await ask_first_question(update, user_id)
        return

    user_answers[user_id].append(message_text)

    if step < len(questions):
        await update.message.reply_text(questions[step])
        user_steps[user_id] = step + 1
        return

    # all 3 answers are in: save them
    answers = user_answers[user_id]
    db = SessionLocal()
    new_standup = Standup(
        telegram_id=user_id,
        name=user_name,
        yesterday=answers[0],
        today=answers[1],
        blockers=answers[2],
    )
    db.add(new_standup)
    db.commit()
    db.close()

    await update.message.reply_text("Thanks, standup saved!")
    if is_real_blocker(answers[2]):
        await tell_manager_about_blocker(context, user_name, answers[2])

    user_steps[user_id] = 0
    user_answers[user_id] = []


async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Every morning: remind the people who have not sent today's standup."""
    db = SessionLocal()
    people = missing_members(db)
    db.close()
    for member in people:
        await context.bot.send_message(chat_id=member.telegram_id,
                                       text="Good morning! Please send today's standup.")


async def send_weekly_summaries(context: ContextTypes.DEFAULT_TYPE):
    """Every Friday evening: each person gets a summary of their week."""
    db = SessionLocal()
    for member in db.query(Member).all():
        text = week_summary_text(db, member.telegram_id)
        await context.bot.send_message(chat_id=member.telegram_id, text=text)
    db.close()


def main():
    Base.metadata.create_all(bind=engine)
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("edit", edit))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # days: 0 = Sunday ... 6 = Saturday
    application.job_queue.run_daily(send_reminders, time=time(10, 0, tzinfo=INDIA), days=(1, 2, 3, 4, 5))
    application.job_queue.run_daily(send_weekly_summaries, time=time(18, 0, tzinfo=INDIA), days=(5,))

    print("bot running")
    application.run_polling()


if __name__ == "__main__":
    main()
