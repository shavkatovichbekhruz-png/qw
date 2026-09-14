"""
export_excel.py — bazadagi ma'lumotlarni Excel faylga aylantiradi.
/export buyrug'i chaqirilganda ishlatiladi.
"""

from openpyxl import Workbook
import database as db


def make_excel_file(path: str = "royxat.xlsx") -> str:
    rows = db.get_all()  # barcha yozuvlar, holatidan qat'i nazar

    wb = Workbook()
    ws = wb.active
    ws.title = "Ro'yxat"

    # Sarlavhalar
    ws.append(["ID", "Telegram ID", "Ism", "Raqam", "Holati", "Vaqti"])

    for row in rows:
        # row tartibi database.py dagi jadval ustunlariga mos keladi:
        # id, telegram_id, full_name, phone, screenshot_file_id, status, created_at
        ws.append([row[0], row[1], row[2], row[3], row[5], row[6]])

    wb.save(path)
    return path
