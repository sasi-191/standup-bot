from datetime import date, datetime, timedelta

from models import Member, Standup

# answers that mean "I have no blockers"
NO_BLOCKER_WORDS = ["no", "none", "nil", "nothing", "na", "n/a", "no blockers", "nope", "-"]


def start_of_day(day):
    return datetime.combine(day, datetime.min.time())


def is_real_blocker(text):
    if text is None:
        return False
    return text.strip().lower() not in NO_BLOCKER_WORDS


def save_member(db, telegram_id, name):
    """Adds the person to the team the first time they message the bot."""
    member = db.query(Member).filter(Member.telegram_id == telegram_id).first()
    if member is None:
        db.add(Member(telegram_id=telegram_id, name=name))
        db.commit()


def todays_standup(db, telegram_id):
    return db.query(Standup).filter(
        Standup.telegram_id == telegram_id,
        Standup.created_at >= start_of_day(date.today()),
    ).first()


def missing_members(db):
    """Team members who have not sent today's standup yet."""
    done_today = db.query(Standup.telegram_id).filter(
        Standup.created_at >= start_of_day(date.today())
    ).all()
    done_ids = [row.telegram_id for row in done_today]

    missing = []
    for member in db.query(Member).order_by(Member.name).all():
        if member.telegram_id not in done_ids:
            missing.append(member)
    return missing


def week_summary_text(db, telegram_id):
    """One message with everything this person did since Monday."""
    monday = date.today() - timedelta(days=date.today().weekday())
    standups = db.query(Standup).filter(
        Standup.telegram_id == telegram_id,
        Standup.created_at >= start_of_day(monday),
    ).order_by(Standup.created_at).all()

    if len(standups) == 0:
        return "You did not send any standups this week."

    text = "Your week:\n"
    for standup in standups:
        day_name = standup.created_at.strftime("%A")
        text = text + "\n" + day_name + ": " + standup.today
        if is_real_blocker(standup.blockers):
            text = text + " (blocker: " + standup.blockers + ")"
    return text
