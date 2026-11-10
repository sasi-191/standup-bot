from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, SessionLocal, engine
from models import Standup
from standup_logic import missing_members, start_of_day

# make the tables if they do not exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/standups")
def get_standups(name: str = None, day: date = None):
    """All standups. Optional search by name and filter by one day."""
    db = SessionLocal()
    query = db.query(Standup)
    if name:
        query = query.filter(Standup.name.ilike("%" + name + "%"))
    if day:
        next_day = day + timedelta(days=1)
        query = query.filter(Standup.created_at >= start_of_day(day),
                             Standup.created_at < start_of_day(next_day))
    rows = query.order_by(Standup.created_at.desc()).all()
    db.close()
    return rows


@app.get("/standups/today")
def get_todays_standups():
    db = SessionLocal()
    todays_standups = db.query(Standup).filter(
        Standup.created_at >= start_of_day(date.today())
    ).order_by(Standup.created_at.desc()).all()
    db.close()
    return todays_standups


@app.get("/standups/missing")
def get_missing():
    """Team members who have not sent today's standup."""
    db = SessionLocal()
    names = [member.name for member in missing_members(db)]
    db.close()
    return names
