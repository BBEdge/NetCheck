#!/usr/bin/env python

import sqlite3

DATABASE = ":memory:"

connection = sqlite3.connect(DATABASE)

with open('templates/schema.sql') as f:
    connection.executescript(f.read())


connection.commit()
connection.close()