#!/usr/bin/env python3
"""Vehicle search by plate number — added in branch `features` (LR5, part 5.1)."""

from models import Vehicle


def find_vehicle_by_plate(plate: str):
    """Return the Vehicle row matching plate (case-insensitive), or None."""
    for vehicle in Vehicle.all():
        if vehicle["plate"].upper() == plate.upper():
            return vehicle
    return None


if __name__ == "__main__":
    plate = input("Enter plate number: ").strip()
    result = find_vehicle_by_plate(plate)
    print(dict(result) if result else "Vehicle not found.")
