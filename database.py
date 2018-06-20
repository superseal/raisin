import time
import sqlite3
import threading

conn = sqlite3.connect("raisin.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(30),
    money INTEGER DEFAULT 1000
)
""")

def add_user(name):
    if not cursor.execute("SELECT id FROM users WHERE name = ?", (name, )).fetchall():
        cursor.execute("INSERT INTO users(name) VALUES (?)", (name, ))

def user_exists(name):
    result = cursor.execute("SELECT name FROM users WHERE name = ?", (name, )).fetchall()
    return bool(result)

def give_money(sender, amount):
    cursor.execute("UPDATE users SET money = money + ? WHERE name = ?", (amount, sender))
    conn.commit()

def take_money(sender, amount):
    cursor.execute("UPDATE users SET money = money - ? WHERE name = ?", (amount, sender))
    conn.commit()

def ask_money(sender):
    result = cursor.execute("SELECT money FROM users WHERE name = ?", (sender, )).fetchone()
    return result[0] if result else 0
