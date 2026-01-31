from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_system_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="System")],
            [KeyboardButton(text="Status"), KeyboardButton(text="Logs")],
            [KeyboardButton(text="Configuration")]
        ],
        resize_keyboard=True,      
        one_time_keyboard=False    
    )

def get_system_usage_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Security", callback_data=f"system_security"), InlineKeyboardButton(text="Systemctl", callback_data=f"system_systemctl")],
        [InlineKeyboardButton(text="Shell", callback_data=f"system_shell")]
    ])

def get_system_systemctl_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Status", callback_data=f"systemctl_status")],
        [InlineKeyboardButton(text="Stop", callback_data=f"systemctl_stop")],
        [InlineKeyboardButton(text="Start", callback_data=f"systemctl_start")],
        [InlineKeyboardButton(text="Restart", callback_data=f"systemctl_restart")]
    ])

def get_status_keyboard(buttonTypes: dict, prefix: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="MEM", callback_data=f"{prefix}mem"), InlineKeyboardButton(text=buttonTypes["mem"], callback_data="tbut:mem")],
        [InlineKeyboardButton(text="CPU", callback_data=f"{prefix}cpu"), InlineKeyboardButton(text=buttonTypes["cpu"], callback_data="tbut:cpu")],
        [InlineKeyboardButton(text="DISK", callback_data=f"{prefix}disks"), InlineKeyboardButton(text=buttonTypes["disks"], callback_data="tbut:disks")]
    ])

def get_logs_keyboard(buttonTypes: dict, prefix: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="syslog", callback_data=f"{prefix}syslog"), InlineKeyboardButton(text=buttonTypes["syslog"], callback_data="tbut:syslog")],
        [InlineKeyboardButton(text="auth", callback_data=f"{prefix}auth"), InlineKeyboardButton(text=buttonTypes["auth"], callback_data="tbut:auth")],
        [InlineKeyboardButton(text="dmesg", callback_data=f"{prefix}dmesg"), InlineKeyboardButton(text=buttonTypes["dmesg"], callback_data="tbut:dmesg")]
    ])

def get_configuration_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Edit configuration", callback_data=f"configuration_edit")]
    ])