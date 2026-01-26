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

def get_logs_keyboard(buttonTypes: dict) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="syslog", callback_data="logs_syslog"), InlineKeyboardButton(text=buttonTypes["syslog"], callback_data="tbut:syslog")],
        [InlineKeyboardButton(text="auth", callback_data="logs_auth"), InlineKeyboardButton(text=buttonTypes["auth"], callback_data="tbut:auth")],
        [InlineKeyboardButton(text="dmesg", callback_data="logs_dmesg"), InlineKeyboardButton(text=buttonTypes["dmesg"], callback_data="tbut:dmesg")]
    ])