"""
sheets.py — Google Sheets bilan bog'lanish uchun.

Har bir yangi ovoz tasdiqlanganda, shu modul orqali Google jadvaliga
avtomatik yangi qator qo'shiladi.

Kerakli narsalar (.env yoki Railway Variables ichida):
- GOOGLE_CREDS_JSON — Google Cloud'dan olingan service account kalitining
  TO'LIQ JSON matni (bitta qator qilib joylashtirilgan)
- SPREADSHEET_ID — Google Sheet havolasidagi /d/ va /edit orasidagi qism
"""

import json
import os

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_client = None
_sheet = None


def _get_sheet():
    """
    Google'ga bog'lanishni faqat bir marta o'rnatadi (keyingi chaqiruvlarda
    qayta bog'lanmaydi, tezroq ishlaydi). Bu "lazy loading" deb ataladi.
    """
    global _client, _sheet
    if _sheet is not None:
        return _sheet

    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    if not creds_json or not spreadsheet_id:
        return None  # sozlanmagan bo'lsa, jim o'tkazib yuboramiz

    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    _client = gspread.authorize(creds)
    _sheet = _client.open_by_key(spreadsheet_id).sheet1
    return _sheet


def append_row(vote_id: int, telegram_id: int, full_name: str, phone: str, status: str, created_at: str):
    """
    Jadvalga bitta qator qo'shadi. Agar Google Sheets sozlanmagan bo'lsa
    (GOOGLE_CREDS_JSON yoki SPREADSHEET_ID yo'q bo'lsa), botni yiqitmaslik
    uchun xatoni faqat konsolga chiqaradi va davom etadi.
    """
    try:
        sheet = _get_sheet()
        if sheet is None:
            return
        sheet.append_row([vote_id, telegram_id, full_name, phone, status, created_at])
    except Exception as e:
        print(f"[sheets.py] Google Sheets'ga yozishda xato: {e}")
