#!/usr/bin/env python3
"""Entry point

MVC layout:
  models.py     — Model (entities + SQLite)
  view.py       — View (console I/O)
  controller.py — Controller (business logic)
"""

from controller import Controller


def main():
    Controller().run()


if __name__ == "__main__":
    main()
