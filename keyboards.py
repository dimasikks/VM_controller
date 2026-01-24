from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_start_keyboard() -> InlineKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Main")],
            [KeyboardButton(text="Status"), KeyboardButton(text="Logs")],
            [KeyboardButton(text="Statistics"), KeyboardButton(text="Systemctl")]
        ],
        resize_keyboard=True,      
        one_time_keyboard=False    
    )

def get_status_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="MEM", callback_data="status_mem")],
        [InlineKeyboardButton(text="CPU", callback_data="status_cpu")],
        [InlineKeyboardButton(text="DISK", callback_data="status_disks")]
    ])