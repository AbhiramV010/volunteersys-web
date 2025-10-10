from sqlalchemy import *

"""
    Creating the tables in postgres
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

try: 
    metadata.create_all(engine, checkfirst=True)
    print('tables created successfully')
except: print('Something unexpected occurred, try again later')