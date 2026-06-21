# APMS — Automated Parking Management System

Academic project for the "Software Development" course.  
Domain: automated vehicle entry control (checkpoint / barrier gate).

## Architecture (MVC)

| File | Layer | Purpose |
|------|-------|---------|
| `models.py` | Model | Domain entities + SQLite persistence |
| `view.py` | View | Console input/output |
| `controller.py` | Controller | Business logic, main menu |
| `main.py` | — | Entry point |
| `search.py` | — | Vehicle search by plate (branch `features`) |

## Entities

`User`, `Vehicle`, `Gate`, `Tariff`, `ParkingSession`

## Running

```bash
python3 main.py
```

`parking.db` is created automatically on first run.

## Photo storage

When an ANPR camera snapshot is provided, it is saved to:

```
photos/<YYYY-MM-DD>/<session_id>.jpg
```

The directory is created automatically. The path is stored in `ParkingSession.photo_path`.  
Photos are retained for 30 days.
