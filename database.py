"""
database.py — botning "xotira" qismi.
Bu fayl SQLite bazasi bilan ishlaydi: yozuv qo'shish, o'qish, tasdiqlash/rad etish.
SQLite — alohida server talab qilmaydigan, bitta faylda saqlanadigan sodda baza.
"""

import sqlite3
from datetime import datetime

DB_PATH = "votes.db"


def init_db():
    """
    Bot birinchi marta ishga tushganda chaqiriladi.
    Agar jadval mavjud bo'lmasa, yaratadi. Mavjud bo'lsa, hech narsa qilmaydi.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            full_name TEXT,
            phone TEXT,
            screenshot_file_id TEXT,
            status TEXT DEFAULT 'pending',   -- pending | approved | rejected
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_pending_vote(telegram_id: int, full_name: str, phone: str, screenshot_file_id: str) -> int:
    """
    Foydalanuvchi screenshot yuborganda chaqiriladi.
    Yozuvni "pending" (kutilmoqda) holatida bazaga qo'shadi va uning ID raqamini qaytaradi.
    Bu ID raqami admin uchun tasdiqlash/rad etish tugmalarida ishlatiladi.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO votes (telegram_id, full_name, phone, screenshot_file_id, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)
    """, (telegram_id, full_name, phone, screenshot_file_id, datetime.now().isoformat()))
    conn.commit()
    vote_id = cur.lastrowid
    conn.close()
    return vote_id


def set_status(vote_id: int, status: str):
    """
    Admin tugmani bosganda chaqiriladi: status 'approved' yoki 'rejected' bo'ladi.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE votes SET status = ? WHERE id = ?", (status, vote_id))
    conn.commit()
    conn.close()


def get_vote(vote_id: int):
    """Bitta yozuvni ID bo'yicha topib qaytaradi."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM votes WHERE id = ?", (vote_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_all(status: str = None):
    """
    Barcha yozuvlarni qaytaradi.
    Agar status berilsa (masalan 'approved'), faqat o'sha holatdagilarni qaytaradi.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if status:
        cur.execute("SELECT * FROM votes WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cur.execute("SELECT * FROM votes ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def count_by_status(status: str) -> int:
    """Berilgan holatdagi (masalan 'approved') yozuvlar sonini qaytaradi."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM votes WHERE status = ?", (status,))
    count = cur.fetchone()[0]
    conn.close()
    return count
