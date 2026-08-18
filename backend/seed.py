from sqlalchemy import *
from datetime import datetime, time

"""
    Loading a sample volunteer and their shifts for testing

    Names and admins are stored lowercase because the frontend lowercases every
    field before it posts, and the lookups match on the stored value exactly.
    The PDF and the app title-case them again for display.
"""
engine = create_engine('postgresql+psycopg2://postgres:post@localhost:5432/postgres')
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
ADMIN = "maria chen"

# date, start, end, signing admin. The May shift runs past midnight on purpose,
# so the overnight handling gets exercised by the sample data too.
SHIFTS = [
    ("2026-01-10", "09:00", "13:00", "maria chen"),
    ("2026-01-24", "09:00", "12:30", "maria chen"),
    ("2026-02-07", "13:00", "17:30", "maria chen"),
    ("2026-02-21", "08:30", "12:00", "sam ortiz"),
    ("2026-03-07", "09:00", "15:00", "maria chen"),
    ("2026-03-21", "10:00", "14:15", "sam ortiz"),
    ("2026-04-04", "08:00", "12:00", "maria chen"),
    ("2026-04-18", "12:00", "18:00", "priya nair"),
    ("2026-05-02", "09:30", "13:00", "maria chen"),
    ("2026-05-16", "22:00", "02:00", "sam ortiz"),
    ("2026-06-06", "07:45", "11:45", "priya nair"),
    ("2026-06-20", "14:00", "19:30", "maria chen"),
]


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


try:
    new_id = seed()
    print("seeded '%s' (volunteer ID %d) with %d shifts" % (NAME, new_id, len(SHIFTS)))
    print("look them up in the app as: Abhiram Vadali / %s" % PHONE)
except Exception as problem:
    print("Could not seed the sample data:", problem)
