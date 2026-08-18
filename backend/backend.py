from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import *
from datetime import datetime
from pdf_report import build_shift_report
import math
import os
import re
import secrets

def is_24_hr(tme):
    try:
        datetime.strptime(tme, "%H:%M")
        return True
    except ValueError:
        return False


DATABASE_URL = os.environ.get(
    "DATABASE_URL", 'postgresql+psycopg2://postgres:post@localhost:5432/postgres')

"""
    The databases the app is allowed to read and write, as name=url pairs
    separated by semicolons:

        DATABASES="live=postgresql+psycopg2://...;training=postgresql+psycopg2://..."

    The browser only ever sends a name, and a name that is not listed here is
    refused. Connection strings stay on this machine, so no password reaches a
    browser and nobody can aim the app at a database of their own.
"""
def load_databases():
    profiles = {}
    for entry in os.environ.get("DATABASES", "").split(";"):
        label, _, url = entry.partition("=")
        if label.strip() and url.strip():
            profiles[label.strip()] = url.strip()
    if not profiles:
        # Single-database mode: DATABASES was not set, so DATABASE_URL is it.
        profiles["default"] = DATABASE_URL
    return profiles


DATABASES = load_databases()
ENGINES = {name: create_engine(url) for name, url in DATABASES.items()}
# Whichever database a request gets when it sends no X-Database header at all -
# the first one configured, so naming your own databases in DATABASES does not
# leave an extra unnamed "default" entry sitting alongside them.
DEFAULT_DATABASE = next(iter(DATABASES))
engine = ENGINES[DEFAULT_DATABASE]
metadata = MetaData()


async def pick_engine(x_database: str = Header(default="")):
    name = x_database.strip() or DEFAULT_DATABASE
    if name not in ENGINES:
        raise HTTPException(status_code=400, detail=f"Unknown database '{name}'")
    return ENGINES[name]

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

system = FastAPI()

# Add the hosted frontend's address here, comma separated, when deploying:
#   ALLOWED_ORIGINS=https://ez-volunteersys.vercel.app
origins = [o.strip() for o in os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost,http://localhost:3000,http://localhost:5173").split(",") if o.strip()]

system.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"],
                      allow_headers=["*"], expose_headers=["Content-Disposition"])

# Shared key every request must present once the API is reachable from the internet.
# Left unset the API stays open, which is only safe while it is bound to localhost.
ADMIN_KEY = os.environ.get("ADMIN_KEY", "").strip()

if not ADMIN_KEY:
    print("WARNING: ADMIN_KEY is not set, so this API is unauthenticated.")
    print("         Anyone who can reach it can read and write volunteer records,")
    print("         including names, home addresses and phone numbers.")
    print("         Set ADMIN_KEY before exposing this beyond localhost.")


async def require_key(x_admin_key: str = Header(default="")):
    if not ADMIN_KEY:
        return
    # Constant time, so a wrong key cannot be narrowed down by timing the reply.
    if not secrets.compare_digest(x_admin_key, ADMIN_KEY):
        raise HTTPException(status_code=401, detail="Missing or invalid admin key")


class Volunteer(BaseModel):
    fullname: str
    phone: str
    address: str
    admin: str
    date: str


class Shift(BaseModel):
    dte: str
    name: str
    start: str
    end: str
    admin: str
    phone: str

class softCheck(BaseModel):
    name: str
    phone: str

@system.post("/addvolunteer", dependencies=[Depends(require_key)])
async def grab_volunteer_data(data: Volunteer, db=Depends(pick_engine)):
    name = data.fullname
    phonenumb = data.phone
    residence = data.address
    signer = data.admin
    datestamp = data.date
    if not re.fullmatch(r'^\d{10}$', phonenumb):
        raise HTTPException(status_code=400, detail="The phone number must be only 10 digits, no spaces")
    else:
        with db.connect() as conn:
            select_stmt = select(masterlist).where(
                and_(masterlist.c.Fullname == name, masterlist.c.PhoneNum == phonenumb))
            result = conn.execute(select_stmt).fetchone()

            if result:
                raise HTTPException(status_code=409,
                                    detail=f"A volunteer named {name} and phone number {phonenumb} was already added")
            else:
                cmd = insert(masterlist).values(Fullname=name, PhoneNum=phonenumb, Address=residence, Admin=signer)
                conn.execute(cmd)
                conn.commit()
                return {
                    "message": "Volunteer added successfully",
                    "fullname": name,
                    "phone": phonenumb,
                    "address": residence,
                    "admin": signer,
                    "date": datestamp,
                }


@system.post("/addhours", dependencies=[Depends(require_key)])
async def grab_sft_data(data: Shift, db=Depends(pick_engine)):
    if not is_24_hr(data.start) or not is_24_hr(data.end):
        raise HTTPException(status_code=400, detail="Time must be in 24 hour format (HH:MM).")

    date = data.dte
    name = data.name
    start = datetime.strptime(data.start, "%H:%M")
    end = datetime.strptime(data.end, "%H:%M")
    adm = data.admin
    phone = data.phone

    with db.connect() as fetch:
        try:
            fetch_ID = select(masterlist.c.ID).where(and_(masterlist.c.Fullname == name, masterlist.c.PhoneNum == phone))
            volunteerID = (fetch.execute(fetch_ID).fetchone())[0]
            volunteerID = int(volunteerID)
        except:
            if len(phone) != 10: raise HTTPException(status_code=404, detail="Phone number must be 10 digits long") 
            else: raise HTTPException(status_code=404, detail="That volunteer was not found, check their name and number")
        cmd = insert(shiftlist).values(Date=date, Fullname=name, Start=start.time(), End=end.time(), Phone=phone,Admin=adm, volunteerID=volunteerID)
        fetch.execute(cmd)
        fetch.commit()
        fetch.close()


    return {
        "message": "Shift logged successfully",
        "fullname": name,
        "start": start,
        "end": end,
        "phone": phone,
        "admin": adm,
        "date": date,
        "volunteer_id": volunteerID
    }

@system.post("/viewhours", dependencies=[Depends(require_key)])
async def view_hrs(data: softCheck, db=Depends(pick_engine)):
    name = data.name
    phone = data.phone

    if len(phone) != 10: raise HTTPException(status_code=400, detail="Phone number must be 10 digits long")
    else: 
        with db.connect() as fetch:
            try:
                fetch_ID = select(masterlist.c.ID).where(and_(masterlist.c.Fullname == name, masterlist.c.PhoneNum == phone))
                volunteerID = (fetch.execute(fetch_ID).fetchone())[0]
                volunteerID = int(volunteerID)
            except:
                raise HTTPException(status_code=404, detail="That volunteer was not found, check their name and number")
            # An end time before the start time means the shift ran past midnight, so it owes a full day.
            elapsed = func.extract('epoch', shiftlist.c.End - shiftlist.c.Start) + case(
                (shiftlist.c.End < shiftlist.c.Start, 86400), else_=0)
            total_hours = (func.sum(elapsed) / 3600).label("TotalHours")
            funnel = select(total_hours).where(shiftlist.c.volunteerID == volunteerID)
            
            volhrs = (fetch.execute(funnel).fetchone())[0]
            try: 
                raise HTTPException(status_code=200, detail=f"{name.upper()} has {math.ceil(volhrs)} hours")  
            except TypeError:
                raise HTTPException(status_code=200, detail=f"{name.upper()} has 0 volunteer hours")         
            fetch.commit()
            fetch.close() 
        


@system.post("/compile", dependencies=[Depends(require_key)])
async def compile_shifts(data: softCheck, db=Depends(pick_engine)):
    name = data.name
    phone = data.phone

    if len(phone) != 10:
        raise HTTPException(status_code=400, detail="Phone number must be 10 digits long")

    with db.connect() as fetch:
        find_volunteer = select(masterlist).where(
            and_(masterlist.c.Fullname == name, masterlist.c.PhoneNum == phone))
        volunteer = fetch.execute(find_volunteer).fetchone()

        if volunteer is None:
            raise HTTPException(status_code=404,
                                detail="That volunteer was not found, check their name and number")

        find_shifts = select(shiftlist).where(
            shiftlist.c.volunteerID == int(volunteer.ID)).order_by(shiftlist.c.Date, shiftlist.c.Start)
        shifts = fetch.execute(find_shifts).fetchall()

    document = build_shift_report(volunteer, shifts)
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or "volunteer"

    return Response(
        content=document,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="shifts-%s.pdf"' % slug},
    )


@system.get("/databases", dependencies=[Depends(require_key)])
async def list_databases():
    return {"databases": sorted(ENGINES.keys())}
