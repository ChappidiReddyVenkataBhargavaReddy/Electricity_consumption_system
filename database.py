import sqlite3, os
from flask import g
from config import DATABASE_PATH

def get_db():
    if "db" not in g:
        g.db=sqlite3.connect(DATABASE_PATH); g.db.row_factory=sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH),exist_ok=True)
    db=sqlite3.connect(DATABASE_PATH); db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS consumers(consumer_id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,consumer_type TEXT NOT NULL,region TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS meters(meter_id INTEGER PRIMARY KEY AUTOINCREMENT,consumer_id INTEGER NOT NULL,meter_code TEXT NOT NULL UNIQUE,FOREIGN KEY(consumer_id) REFERENCES consumers(consumer_id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS meter_readings(reading_id INTEGER PRIMARY KEY AUTOINCREMENT,meter_id INTEGER NOT NULL,reading_date TEXT NOT NULL,cumulative_kwh REAL NOT NULL CHECK(cumulative_kwh>=0),validation_note TEXT DEFAULT '',UNIQUE(meter_id,reading_date),FOREIGN KEY(meter_id) REFERENCES meters(meter_id) ON DELETE CASCADE);
    """); db.commit(); db.close()

def seed_demo_data():
    db=sqlite3.connect(DATABASE_PATH); db.execute("PRAGMA foreign_keys=ON")
    if db.execute("SELECT COUNT(*) FROM consumers").fetchone()[0]==0:
        db.executemany("INSERT INTO consumers(name,consumer_type,region) VALUES(?,?,?)",[("Asha Kumar","Residential","Tirupati"),("Sri Lakshmi Stores","Commercial","Punganur"),("MBU Lab Block","Institutional","Tirupati")])
        db.executemany("INSERT INTO meters(consumer_id,meter_code) VALUES(?,?)",[(1,"TM-1001"),(2,"TM-1002"),(3,"TM-1003")])
        sample=[(1,"2026-01-01",1000),(1,"2026-02-01",1240),(1,"2026-03-01",1505),(1,"2026-04-01",1770),(1,"2026-05-01",2100),(1,"2026-06-01",2400),(2,"2026-01-01",5000),(2,"2026-02-01",5390),(2,"2026-03-01",5800),(2,"2026-04-01",6230),(2,"2026-05-01",6680),(2,"2026-06-01",7150),(3,"2026-01-01",200),(3,"2026-02-01",430),(3,"2026-03-01",680),(3,"2026-04-01",920),(3,"2026-05-01",1180),(3,"2026-06-01",1460)]
        db.executemany("INSERT INTO meter_readings(meter_id,reading_date,cumulative_kwh) VALUES(?,?,?)",sample)
    db.commit(); db.close()
