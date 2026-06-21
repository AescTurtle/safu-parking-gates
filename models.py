#!/usr/bin/env python3
"""Model layer (MVC): domain entities and SQLite persistence.

Entities: Gate, Vehicle, User, Tariff, ParkingSession.
"""

import sqlite3
import shutil
import os
from datetime import datetime, date

DB_NAME = "parking.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables on first run."""
    conn = get_connection()
    conn.cursor().executescript(
        """
        CREATE TABLE IF NOT EXISTS User (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone     TEXT NOT NULL,
            access_type TEXT NOT NULL,
            subscription_end TEXT
        );
        CREATE TABLE IF NOT EXISTS Vehicle (
            vehicle_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            plate       TEXT NOT NULL UNIQUE,
            make        TEXT NOT NULL,
            user_id     INTEGER,
            FOREIGN KEY (user_id) REFERENCES User(user_id)
        );
        CREATE TABLE IF NOT EXISTS Gate (
            gate_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            location    TEXT NOT NULL,
            status      TEXT NOT NULL,
            gate_type   TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Tariff (
            tariff_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            hourly_rate     REAL NOT NULL,
            subscription_fee REAL NOT NULL,
            date_from       TEXT NOT NULL,
            date_to         TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ParkingSession (
            session_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id  INTEGER NOT NULL,
            tariff_id   INTEGER,
            gate_id     INTEGER,
            entry_time  TEXT NOT NULL,
            exit_time   TEXT,
            cost        REAL,
            paid        INTEGER DEFAULT 0,
            photo_path  TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
            FOREIGN KEY (tariff_id)  REFERENCES Tariff(tariff_id),
            FOREIGN KEY (gate_id)    REFERENCES Gate(gate_id)
        );
        """
    )
    conn.commit()
    conn.close()


class User:
    def __init__(self, full_name, phone, access_type, subscription_end=None, id_=None):
        self.id = id_
        self.full_name = full_name
        self.phone = phone
        self.access_type = access_type
        self.subscription_end = subscription_end

    def save(self):
        conn = get_connection()
        conn.execute(
            "INSERT INTO User (full_name, phone, access_type, subscription_end) "
            "VALUES (?, ?, ?, ?)",
            (self.full_name, self.phone, self.access_type, self.subscription_end),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM User").fetchall()
        conn.close()
        return rows


class Vehicle:
    def __init__(self, plate, make, user_id=None, id_=None):
        self.id = id_
        self.plate = plate
        self.make = make
        self.user_id = user_id

    def save(self):
        conn = get_connection()
        conn.execute(
            "INSERT INTO Vehicle (plate, make, user_id) VALUES (?, ?, ?)",
            (self.plate, self.make, self.user_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM Vehicle").fetchall()
        conn.close()
        return rows


class Tariff:
    def __init__(self, name, hourly_rate, subscription_fee, date_from, date_to, id_=None):
        self.id = id_
        self.name = name
        self.hourly_rate = hourly_rate
        self.subscription_fee = subscription_fee
        self.date_from = date_from
        self.date_to = date_to

    def save(self):
        conn = get_connection()
        conn.execute(
            "INSERT INTO Tariff (name, hourly_rate, subscription_fee, date_from, date_to) "
            "VALUES (?, ?, ?, ?, ?)",
            (self.name, self.hourly_rate, self.subscription_fee, self.date_from, self.date_to),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM Tariff").fetchall()
        conn.close()
        return rows


class Gate:
    def __init__(self, location, gate_type, status="closed", id_=None):
        self.id = id_
        self.location = location
        self.gate_type = gate_type
        self.status = status

    def save(self):
        conn = get_connection()
        conn.execute(
            "INSERT INTO Gate (location, status, gate_type) VALUES (?, ?, ?)",
            (self.location, self.status, self.gate_type),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM Gate").fetchall()
        conn.close()
        return rows


class ParkingSession:
    def __init__(self, vehicle_id, gate_id=None, tariff_id=None, photo_path=None, id_=None):
        self.id = id_
        self.vehicle_id = vehicle_id
        self.gate_id = gate_id
        self.tariff_id = tariff_id
        self.photo_path = photo_path

    def record_entry(self, source_photo: str = None):
        """Insert entry record; optionally copy ANPR snapshot to photos/<date>/<session_id>.jpg."""
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO ParkingSession (vehicle_id, gate_id, tariff_id, entry_time, photo_path) "
            "VALUES (?, ?, ?, ?, ?)",
            (self.vehicle_id, self.gate_id, self.tariff_id,
             datetime.now().isoformat(timespec="seconds"), None),
        )
        conn.commit()
        self.id = cur.lastrowid

        if source_photo and os.path.isfile(source_photo):
            folder = os.path.join("photos", date.today().isoformat())
            os.makedirs(folder, exist_ok=True)
            dest = os.path.join(folder, f"{self.id}.jpg")
            shutil.copy2(source_photo, dest)
            self.photo_path = dest
            conn.execute(
                "UPDATE ParkingSession SET photo_path = ? WHERE session_id = ?",
                (dest, self.id),
            )
            conn.commit()

        conn.close()
        return self.id

    @staticmethod
    def calculate_cost(entry_time: str, exit_time: str, hourly_rate: float) -> float:
        t_in = datetime.fromisoformat(entry_time)
        t_out = datetime.fromisoformat(exit_time)
        hours = max(0.0, (t_out - t_in).total_seconds() / 3600.0)
        return round(hours * hourly_rate, 2)
