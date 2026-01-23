from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Status", callback_data="status")]
    ])

def get_status_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="MEM", callback_data="status_mem")],
        [InlineKeyboardButton(text="CPU", callback_data="status_cpu")],
        [InlineKeyboardButton(text="DISK", callback_data="status_disks")]
    ])