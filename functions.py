import keyboards
import asyncio
import yaml

from PIL import Image, ImageDraw, ImageFont
from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command

#=======# SERVER #=======#

buttonTypes = {
    "syslog": "TXT",
    "auth": "TXT",
    "dmesg": "TXT"
}

async def tbut(callback: CallbackQuery):
    type_button = callback.data.split(":", 1)[1]

    buttonTypes[type_button] = "IMG" if buttonTypes[type_button] == "TXT" else "TXT"
        
    await callback.answer()
    await callback.message.edit_text(
        text="Types:",
        reply_markup=keyboards.get_logs_keyboard(buttonTypes)
    )


with open("configs/image.yml", "r", encoding="utf-8") as config:
    image_settings = yaml.safe_load(config)

fp = image_settings['font_path']
fs = image_settings['font_size']
p0 = image_settings['padding'][0]
p1 = image_settings['padding'][1]
lh = image_settings['line_height']
bc = image_settings['bg_color']
tc = image_settings['text_color']
sp = image_settings['save_path']
mw = image_settings['max_image_width']
mh = image_settings['max_image_height']

def render_image(text: str) -> str:
    try:
        font = ImageFont.truetype(fp, fs)
    except OSError:
        print("ERROR: FONT NOT FOUND")

    lines = text.splitlines() or [""]
    
    MAX_WIDTH_CHARS = 94
    processed_lines = []
    for line in lines:
        if len(line) > MAX_WIDTH_CHARS:
            line = line[:MAX_WIDTH_CHARS - 1] + ">"
        processed_lines.append(line)
    lines = processed_lines

    if hasattr(font, 'getbbox'):
        char_width = font.getbbox("A")[2]
    else:
        char_width = font.getsize("A")[0]

    img_width = min(len(max(lines, key=len)) * char_width + 2 * p0, mw)
    img_height = min(len(lines) * lh + 2 * p1, mh)

    img = Image.new("RGB", (img_width, img_height), bc)
    draw = ImageDraw.Draw(img)

    y = p1
    for line in lines:
        draw.text((p0, y), line, fill=tc, font=font)
        y += lh

    img.save(sp)
    return sp

async def command_image(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    output = stdout.decode('utf-8', errors='replace')
    
    if not output.strip():
        output = "[OUTPUT IS EMPTY]"

    image_path = render_image(output)
    return image_path

async def command_shell(cmd: str) -> str:
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

#=======# START #=======#

async def start(message: Message):
    hostname = await command_shell("hostname")
    ip = await command_shell("hostname -I")

    await message.answer(
        f"USER: {message.from_user.first_name}\n\nVM: {hostname}\nIP: {ip}",
        reply_markup=keyboards.get_start_keyboard()
    )

#=======# STATUS #=======#

async def status(message: Message):
    await message.answer(
        "Metrics:",
        reply_markup=keyboards.get_status_keyboard()
    )

async def status_mem(callback: CallbackQuery):
    await callback.answer()

    mem = await command_shell("free -h")

    await callback.message.answer(
        f"{mem}"
    )

async def status_cpu(callback: CallbackQuery):
    await callback.answer()

    cpu = await command_shell("uptime")

    await callback.message.answer(
        f"{cpu}"
    )

async def status_disks(callback: CallbackQuery):
    await callback.answer()

    disks = await command_shell("df -h")

    await callback.message.answer(
        f"<code>{disks}</code>",
        parse_mode="HTML"
    )

#=======# LOGS #=======#

log_paths = {
    "logs_syslog": "/var/log/syslog",
    "logs_auth": "/var/log/auth.log",
    "logs_dmesg": "/var/log/dmesg",
}
log_lines = 15

async def logs(message: Message):
    await message.answer(
        "Types:",
        reply_markup=keyboards.get_logs_keyboard(buttonTypes)
    )

async def logs_syslog(callback: CallbackQuery):
    await callback.answer()

    path = await command_image(f"sudo tail -n {log_lines} {log_paths['logs_syslog']}")

    img = FSInputFile(path)
    await callback.message.answer_photo(img)

    # await callback.message.answer(
    #     f"<b>Last {log_lines} of {log_paths['logs_syslog']}:</b>\n\n"
    #     f"<pre>{output}</pre>",
    #     parse_mode="HTML"
    # )

async def logs_dmesg(callback: CallbackQuery):
    await callback.answer()

    cpu = await command_shell("uptime")

    await callback.message.answer(
        f"{cpu}"
    )

async def logs_dmesg(callback: CallbackQuery):
    await callback.answer()

    cpu = await command_shell("uptime")

    await callback.message.answer(
        f"{cpu}"
    )

#=======# FALLBACK #=======#

async def fallback(message: Message):
    await message.answer("USAGE: /start")

def register_handlers(dp: Dispatcher):
    dp.callback_query.register(tbut, F.data.startswith("tbut:"))

    dp.message.register(start, Command("start"))
    dp.message.register(start, F.text == "Main")
    dp.message.register(status, F.text == "Status")
    dp.message.register(logs, F.text == "Logs")
    # dp.message.register(statistics, F.text == "Statistics")
    # dp.message.register(systmed, F.text == "Systemd")
    dp.message.register(fallback)

    dp.callback_query.register(status_mem, F.data == "status_mem")
    dp.callback_query.register(status_cpu, F.data == "status_cpu")
    dp.callback_query.register(status_disks, F.data == "status_disks")

    dp.callback_query.register(logs_syslog, F.data == "logs_syslog")