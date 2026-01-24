import keyboards
import asyncio

from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

async def command(cmd: str) -> str:
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            output = stdout.decode('utf-8').strip()
        else:
            output = f"ERROR (code {proc.returncode}):\n{stderr.decode('utf-8').strip()}"

        return output
    except Exception as e:
        return f"ERROR EXCEPTION:\n{str(e)}"

async def start(message: Message):
    hostname = await command("hostname")
    ip = await command("hostname -I")

    await message.answer(
        f"USER: {message.from_user.first_name}\n\nVM: {hostname}\nIP: {ip}",
        reply_markup=keyboards.get_start_keyboard()
    )

async def status(message: Message):
    await message.answer(
        "Metrics:",
        reply_markup=keyboards.get_status_keyboard()
    )

async def status_mem(callback: CallbackQuery):
    await callback.answer()

    mem = await command("free -h")

    await callback.message.answer(
        f"{mem}"
    )

async def status_cpu(callback: CallbackQuery):
    await callback.answer()

    cpu = await command("uptime")

    await callback.message.answer(
        f"{cpu}"
    )

async def status_disks(callback: CallbackQuery):
    await callback.answer()

    disks = await command("df -h")

    await callback.message.answer(
        f"{disks}"
    )

async def fallback(message: Message):
    await message.answer("USAGE: /start")


def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command("start"))
    dp.message.register(start, F.text == "Main")
    dp.message.register(status, F.text == "Status")
    dp.message.register(fallback)

    dp.callback_query.register(status_mem, F.data == "status_mem")
    dp.callback_query.register(status_cpu, F.data == "status_cpu")
    dp.callback_query.register(status_disks, F.data == "status_disks")