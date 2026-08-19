from sqlalchemy import *
import os
from datetime import datetime, time

"""
    Loading a sample volunteer and their shifts for testing

    Names and admins are stored lowercase because the frontend lowercases every
    field before it posts, and the lookups match on the stored value exactly.
    The PDF and the app title-case them again for display.
"""
engine = create_engine(os.environ.get(
    'DATABASE_URL', 'postgresql+psycopg2://postgres:post@localhost:5432/postgres'))
metadata = MetaData()
masterlist = Table(
    'volunteers',
    metadata,
    Column("Fullname", String(255)),
    Column("PhoneNum", String(10)),
    Column("Address", String(255)),
    Column("Admin", String(255)),
    Column("ID", Integer, primary_key=True),
    Column("Date", TIMESTAMP, server_default=text("CURRENT_DATE")))
shiftlist = Table(
    'shifts',
    metadata,
    Column("Date", TIMESTAMP, server_default=text("CURRENT_DATE")),
    Column("Fullname", String(255)),
    Column("Start", TIME),
    Column("End", TIME),
    Column("Phone", String(10)),
    Column("Admin", String(255)),
    Column("ShiftID", Integer, primary_key=True, autoincrement=True),
    Column("volunteerID", Integer, ForeignKey("volunteers.ID")))

NAME = "abhiram vadali"
PHONE = "4155550147"
ADDRESS = "88 Marigold Way, Santa Clara, CA 95051"
ADMIN = "anjali mehta"

# date, start, end, signing admin. Ten shifts totalling exactly 54.00 hours.
# The May shift runs past midnight on purpose, so the overnight handling gets
# exercised by the sample data too.
SHIFTS = [
    ("2026-01-10", "09:00", "14:00", "anjali mehta"),   # 5.0
    ("2026-01-24", "08:00", "14:00", "anjali mehta"),   # 6.0
    ("2026-02-07", "13:00", "17:30", "arjun verma"),    # 4.5
    ("2026-02-21", "08:30", "14:00", "anjali mehta"),   # 5.5
    ("2026-03-07", "09:00", "15:00", "priya nair"),   # 6.0
    ("2026-03-21", "10:00", "14:00", "arjun verma"),    # 4.0
    ("2026-04-04", "08:00", "13:00", "anjali mehta"),   # 5.0
    ("2026-04-18", "11:00", "18:00", "priya nair"),   # 7.0
    ("2026-05-02", "09:30", "15:00", "anjali mehta"),   # 5.5
    ("2026-05-16", "21:00", "02:30", "arjun verma"),    # 5.5, runs past midnight
]

EXPECTED_HOURS = 54.0


def as_time(clock):
    return datetime.strptime(clock, "%H:%M").time()


def seed():
    metadata.create_all(engine, checkfirst=True)

    with engine.connect() as conn:
        # Clear any previous run so seeding twice does not double the hours.
        existing = conn.execute(select(masterlist.c.ID).where(
            and_(masterlist.c.Fullname == NAME, masterlist.c.PhoneNum == PHONE))).fetchall()
        for row in existing:
            conn.execute(shiftlist.delete().where(shiftlist.c.volunteerID == int(row[0])))
            conn.execute(masterlist.delete().where(masterlist.c.ID == int(row[0])))

        added = conn.execute(insert(masterlist).values(
            Fullname=NAME, PhoneNum=PHONE, Address=ADDRESS, Admin=ADMIN))
        volunteer_id = int(added.inserted_primary_key[0])

        conn.execute(insert(shiftlist), [
            dict(Date=datetime.strptime(day, "%Y-%m-%d"), Fullname=NAME,
                 Start=as_time(start), End=as_time(end), Phone=PHONE,
                 Admin=admin, volunteerID=volunteer_id)
            for day, start, end, admin in SHIFTS
        ])
        conn.commit()

    return volunteer_id


def total_hours():
    """Hours the sample data adds up to, counting a past-midnight end as the next day."""
    total = 0.0
    for _, start, end, _ in SHIFTS:
        span = (as_time_delta(end) - as_time_delta(start))
        if span < 0:
            span += 24
        total += span
    return total


def as_time_delta(clock):
    stamp = datetime.strptime(clock, "%H:%M")
    return stamp.hour + stamp.minute / 60


try:
    hours = total_hours()
    new_id = seed()
    print("seeded '%s' (volunteer ID %d) with %d shifts totalling %.2f hours"
          % (NAME, new_id, len(SHIFTS), hours))
    if abs(hours - EXPECTED_HOURS) > 0.001:
        print("warning: expected %.2f hours, the shift times now add up to %.2f" % (EXPECTED_HOURS, hours))
    print("look them up in the app as: Abhiram Vadali / %s" % PHONE)
except Exception as problem:
    print("Could not seed the sample data:", problem)
