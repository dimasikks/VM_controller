import functions

from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

async def start(message: Message):
    await message.answer(
        "Привет! Выбери действие:",
        reply_markup=functions.get_start_keyboard()
    )

async def handle_status(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("📊 Система работает!")

async def fallback(message: Message):
    await message.answer("❓ Используй /start.")


def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command("start"))
    dp.message.register(fallback)

    dp.callback_query.register(handle_status, F.data == "status")