"""
bot.py — botning "yuzi". Foydalanuvchi bilan gaplashadigan, tugmalarni ko'rsatadigan qism.

Ishlatilgan kutubxona: aiogram (Telegram botlar uchun eng ko'p ishlatiladigan Python kutubxonasi).

Jarayon (oddiy tilda):
1. Foydalanuvchi /start bosadi -> yo'riqnoma va "Ovoz berish" tugmasi ko'rinadi
2. Tugma bosilsa -> ism va telefon raqami so'raladi
3. Bot loyihaning havolasini yuboradi -> "borib ovoz bering, keyin screenshot yuboring" deydi
4. Foydalanuvchi screenshot yuboradi -> bu "kutilmoqda" holatida bazaga yoziladi
5. Sizga (admin) screenshot va "Tasdiqlash" / "Rad etish" tugmalari bilan xabar keladi
6. Siz bosgan tugmangizga qarab, baza yangilanadi
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from dotenv import load_dotenv

import database as db

# --- Sozlamalarni .env faylidan o'qiymiz (maxfiy ma'lumotlar kodda emas) ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PROJECT_LINK = os.getenv("PROJECT_LINK", "https://openbudget.uz/PROJECT_LINK_BU_YERGA")
PROJECT_NAME = os.getenv("PROJECT_NAME", "Bizning loyiha")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# --- "Holat mashinasi" — bot foydalanuvchi bilan qaysi bosqichda ekanini eslab turadi ---
class VotingFlow(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_screenshot = State()


# ========== 1. /start buyrug'i ==========
@dp.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        f"Assalomu alaykum!\n\n"
        f"Bu bot \"{PROJECT_NAME}\" loyihasiga ovoz berish jarayonini tashkillashtirish uchun.\n\n"
        f"Tartib juda oddiy:\n"
        f"1. Ismingiz va raqamingizni qoldirasiz\n"
        f"2. Sizga loyiha havolasi yuboriladi\n"
        f"3. O'sha yerda o'zingiz shaxsan ovoz berasiz\n"
        f"4. Ovoz berganingizni tasdiqlovchi skrinshot yuborasiz\n\n"
        f"Boshlaymizmi?"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗳 Ovoz berish", callback_data="start_voting")]
    ])
    await message.answer(text, reply_markup=keyboard)


# ========== 2. "Ovoz berish" tugmasi bosilganda ==========
@dp.callback_query(F.data == "start_voting")
async def start_voting(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Ismingiz va familiyangizni yozing:")
    await state.set_state(VotingFlow.waiting_name)
    await callback.answer()  # tugmadagi "yuklanmoqda" belgisini olib tashlaydi


@dp.message(VotingFlow.waiting_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)

    # Telefon raqamini so'raymiz — tugma orqali yuborish imkonini ham beramiz
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer(
        "Telefon raqamingizni yuboring (tugmani bosing yoki qo'lda yozing):",
        reply_markup=keyboard
    )
    await state.set_state(VotingFlow.waiting_phone)


@dp.message(VotingFlow.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    # Raqam tugma orqali yuborilgan bo'lishi ham, qo'lda yozilgan bo'lishi ham mumkin
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)

    text = (
        f"Rahmat! Endi quyidagi havola orqali ovoz bering:\n\n"
        f"{PROJECT_LINK}\n\n"
        f"Ovoz berib bo'lgach, tasdiq sifatida sahifaning skrinshotini shu yerga yuboring."
    )
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(VotingFlow.waiting_screenshot)


# ========== 3. Screenshot kelganda ==========
@dp.message(VotingFlow.waiting_screenshot, F.photo)
async def get_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    full_name = data.get("full_name")
    phone = data.get("phone")
    file_id = message.photo[-1].file_id  # eng katta o'lchamdagi rasm

    vote_id = db.add_pending_vote(message.from_user.id, full_name, phone, file_id)

    await message.answer("Rahmat! Skrinshotingiz qabul qilindi, admin tekshirib chiqadi.")
    await state.clear()

    # Adminga xabar yuboramiz — tasdiqlash/rad etish tugmalari bilan
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{vote_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{vote_id}"),
        ]
    ])
    caption = f"Yangi ovoz:\nIsm: {full_name}\nRaqam: {phone}\nID: {vote_id}"
    await bot.send_photo(ADMIN_ID, file_id, caption=caption, reply_markup=admin_keyboard)


@dp.message(VotingFlow.waiting_screenshot)
async def wrong_content(message: Message):
    await message.answer("Iltimos, skrinshot (rasm) yuboring.")


# ========== 4. Admin tugmani bosganda ==========
@dp.callback_query(F.data.startswith("approve_"))
async def approve_vote(callback: CallbackQuery):
    vote_id = int(callback.data.split("_")[1])
    db.set_status(vote_id, "approved")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ TASDIQLANDI")
    await callback.answer("Tasdiqlandi")


@dp.callback_query(F.data.startswith("reject_"))
async def reject_vote(callback: CallbackQuery):
    vote_id = int(callback.data.split("_")[1])
    db.set_status(vote_id, "rejected")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ RAD ETILDI")
    await callback.answer("Rad etildi")


# ========== 5. Admin uchun buyruqlar ==========
@dp.message(Command("royxat"))
async def show_list(message: Message):
    if message.from_user.id != ADMIN_ID:
        return  # faqat admin ko'ra oladi

    approved = db.count_by_status("approved")
    pending = db.count_by_status("pending")
    rejected = db.count_by_status("rejected")
    await message.answer(
        f"📊 Hisobot:\n"
        f"✅ Tasdiqlangan: {approved}\n"
        f"⏳ Kutilmoqda: {pending}\n"
        f"❌ Rad etilgan: {rejected}"
    )


@dp.message(Command("export"))
async def export_excel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    from export_excel import make_excel_file  # 4-qadamda yozamiz
    filepath = make_excel_file()
    await message.answer_document(document=open(filepath, "rb"))


# ========== Botni ishga tushirish ==========
async def main():
    db.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
