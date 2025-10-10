from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import *
from datetime import datetime
import re
import numpy as np

def is_24_hr(tme):
    try:
        datetime.strptime(tme, "%H:%M")
        return True
    except ValueError:
        return False


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

system = FastAPI()

origins = ["http://localhost", "http://localhost:3000", "http://localhost:5173"]
system.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"],
                      allow_headers=["*"])


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

@system.post("/addvolunteer")
async def grab_volunteer_data(data: Volunteer):
    name = data.fullname
    phonenumb = data.phone
    residence = data.address
    signer = data.admin
    datestamp = data.date
    if not re.fullmatch(r'^\d{10}$', phonenumb):
        raise HTTPException(status_code=400, detail="The phone number must be only 10 digits, no spaces")
    else:
        with engine.connect() as conn:
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


@system.post("/addhours")
async def grab_sft_data(data: Shift):
    if not is_24_hr(data.start) or not is_24_hr(data.end):
        raise HTTPException(status_code=400, detail="Time must be in 24 hour format (HH:MM).")

    date = data.dte
    name = data.name
    start = datetime.strptime(data.start, "%H:%M")
    end = datetime.strptime(data.end, "%H:%M")
    adm = data.admin
    phone = data.phone

    with engine.connect() as fetch:
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

@system.post("/viewhours")
async def view_hrs(data: softCheck):
    name = data.name
    phone = data.phone

    if len(phone) != 10: raise HTTPException(status_code=400, detail="Phone number must be 10 digits long")
    else: 
        with engine.connect() as fetch:
            try:
                fetch_ID = select(masterlist.c.ID).where(and_(masterlist.c.Fullname == name, masterlist.c.PhoneNum == phone))
                volunteerID = (fetch.execute(fetch_ID).fetchone())[0]
                volunteerID = int(volunteerID)
            except:
                raise HTTPException(status_code=404, detail="That volunteer was not found, check their name and number")
            total_hours = func.sum(func.extract('epoch', shiftlist.c.End - shiftlist.c.Start) / 3600).label("TotalHours")
            funnel = select(total_hours).where(shiftlist.c.volunteerID == volunteerID)
            
            volhrs = (fetch.execute(funnel).fetchone())[0]
            try: 
                raise HTTPException(status_code=200, detail=f"{name.upper()} has {np.ceil(volhrs)} hours")  
            except TypeError:
                raise HTTPException(status_code=200, detail=f"{name.upper()} has 0 volunteer hours")         
            fetch.commit()
            fetch.close() 
        