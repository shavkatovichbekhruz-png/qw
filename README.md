# Ovoz yig'ish boti

Oddiy Telegram bot: foydalanuvchi ma'lumotlarini yig'adi, loyiha havolasini beradi,
ovoz berganini tasdiqlovchi skrinshotni qabul qiladi va admin tasdiqlashi uchun yuboradi.

## Fayllar

- `bot.py` — botning asosiy kodi
- `database.py` — SQLite baza bilan ishlash
- `export_excel.py` — ro'yxatni Excel faylga aylantirish
- `requirements.txt` — kerakli kutubxonalar
- `.env.example` — sozlamalar namunasi

## O'z kompyuteringizda ishga tushirish (sinov uchun)

1. Python o'rnatilgan bo'lishi kerak (3.10 yoki undan yuqori)
2. Terminalda shu papkaga kiring va kutubxonalarni o'rnating:
   ```
   pip install -r requirements.txt
   ```
3. `.env.example` faylini nusxalab, nomini `.env` ga o'zgartiring
4. `.env` faylini oching va quyidagilarni to'ldiring:
   - `BOT_TOKEN` — @BotFather'dan olingan token
   - `ADMIN_ID` — @userinfobot orqali olingan shaxsiy ID raqamingiz
   - `PROJECT_LINK` — loyihangizning haqiqiy openbudget.uz havolasi
5. Botni ishga tushiring:
   ```
   python bot.py
   ```
6. Telegram'da botingizni topib, /start bosing

## Doimiy ishlashi uchun (server)

Kompyuteringizni o'chirsangiz, bot ham to'xtaydi. Doimiy ishlashi uchun uni
Railway.app yoki Render.com kabi bepul/arzon xizmatga joylashtirish kerak —
buni alohida, keyingi qadamda ko'rsataman.

## Buyruqlar

- `/start` — botni boshlash (har bir foydalanuvchi uchun)
- `/royxat` — qisqacha hisobot (faqat admin uchun)
- `/export` — to'liq ro'yxatni Excel faylida olish (faqat admin uchun)
