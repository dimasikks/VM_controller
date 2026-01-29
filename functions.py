import keyboards
import asyncio
import yaml

from PIL import Image, ImageDraw, ImageFont
from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

#=======# SERVER #=======#

class waitings(StatesGroup):
    waiting_systemctl = State()

buttonTypesLogs = {
    "syslog": "TXT",
    "auth": "TXT",
    "dmesg": "TXT"
}

buttonTypesStatus = {
    "mem": "TXT",
    "cpu": "TXT",
    "disks": "TXT"
}

systemctl_status = ""

async def answerw(message: Message, state: FSMContext):
    cs = await state.get_state()
    uinput = message.text.strip()
    global systemctl_status

    if len(uinput.split()) > 1:
        await message.answer(
            f"<b>Service name is incorrect, exit</b>",
            parse_mode="HTML"
        )
        return
    
    if cs == waitings.waiting_systemctl:
        check = await command_shell(f"sudo systemctl status {uinput}")

        if "code 4" in check:
            await message.answer(
                f"<b>Service not found, exit</b>",
                parse_mode="HTML"
            )
            return

        if systemctl_status == "status":
            path = await command_image(f"echo 'Checking...\n';sudo systemctl status {uinput} --no-pager")

            img = FSInputFile(path)
            await message.answer_photo(
                img,
                caption=f"<b>Systemctl status {uinput} result</b>",
                parse_mode="HTML"
            )
        elif systemctl_status == "stop":
            path = await command_image(f"echo 'Stopping...\n';sudo systemctl stop {uinput}; echo 'Checking...\n';sudo systemctl status {uinput} --no-pager")

            img = FSInputFile(path)
            await message.answer_photo(
                img,
                caption=f"<b>Systemctl stop {uinput} result</b>",
                parse_mode="HTML"
            )
        elif systemctl_status == "start":
            path = await command_image(f"echo 'Starting...\n';sudo systemctl start {uinput};echo 'Checking...\n';sudo systemctl status {uinput} --no-pager")

            img = FSInputFile(path)
            await message.answer_photo(
                img,
                caption=f"<b>Systemctl start {uinput} result</b>",
                parse_mode="HTML"
            )
        else:
            path = await command_image(f"echo 'Restarting...\n';sudo systemctl restart {uinput}; echo 'Checking...\n';sudo systemctl status {uinput} --no-pager")

            img = FSInputFile(path)
            await message.answer_photo(
                img,
                caption=f"<b>Systemctl restart {uinput} result</b>",
                parse_mode="HTML"
            )

    await state.clear()

async def tbut(callback: CallbackQuery):
    type_button = callback.data.split(":", 1)[1]

    if type_button in buttonTypesLogs:
        buttonTypesLogs[type_button] = "IMG" if buttonTypesLogs[type_button] == "TXT" else "TXT"
            
        await callback.answer()
        await callback.message.edit_reply_markup(
            reply_markup=keyboards.get_logs_keyboard(buttonTypesLogs, log_prefix)
        )
    elif type_button in buttonTypesStatus:
        buttonTypesStatus[type_button] = "IMG" if buttonTypesStatus[type_button] == "TXT" else "TXT"
            
        await callback.answer()
        await callback.message.edit_reply_markup(
            reply_markup=keyboards.get_status_keyboard(buttonTypesStatus, status_prefix)
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
        print("E: FONT NOT FOUND")

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
            output = f"E: (code {proc.returncode}):\n{stderr.decode('utf-8').strip()}"

        return output
    except Exception as e:
        return f"E: EXCEPTION - \n{str(e)}"

#=======# START #=======#

async def start(message: Message):
    await message.answer(
        f"<b>Activated admin keyboard</b>",
        parse_mode="HTML",
        reply_markup=keyboards.get_system_keyboard()
    )

#=======# SYSTEM #=======#

security_lastlogs = 5

async def system(message: Message):
    hostname = await command_shell("hostname")
    ip = await command_shell("hostname -I")

    await message.answer(
        f"<b>USER: </b>{message.from_user.first_name}\n\n"
        f"<b>VM: </b>{hostname}\n"
        f"<b>IP: </b>{ip}\n",
        parse_mode="HTML",
        reply_markup=keyboards.get_system_usage_keyboard()
    )

async def system_security(callback: CallbackQuery):
    uname = await command_shell("uname -a")
    users = await command_shell("who")
    lastl = await command_image(f"last -n {security_lastlogs}")

    await callback.message.answer(
            f"<b><u>SYSTEM SECURITY</u></b>\n"
            f"\n<b>VM extended:</b>\n"
            f"<pre>{uname}</pre>\n"
            f"\n<b>Users in system: </b>\n"
            f"<pre>{users}</pre>",
            parse_mode="HTML"
            )

    img = FSInputFile(lastl)
    await callback.message.answer_photo(
        img,
        caption=f"<b>Last {security_lastlogs} logins in system</b>",
        parse_mode="HTML"
    )

systemctl_statuses = [
    "status",
    "start",
    "stop",
    "restart"
]

async def system_systemctl(callback: CallbackQuery):
    await callback.answer()

    svc_active = await command_shell("sudo systemctl list-units --all --type=service --state=active | grep service | wc -l")
    svc_inactive = await command_shell("sudo systemctl list-units --all --type=service --state=inactive | grep service | wc -l")

    await callback.message.answer(
        f"<b><u>SYSTEMCTL STATUS</u></b>\n\n"
        f"<b>Active services:</b> {svc_active}\n"
        f"<b>Inactive services:</b> {svc_inactive}",
        parse_mode="HTML",
        reply_markup=keyboards.get_system_systemctl_keyboard()
    )

async def systemctl_definer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    global systemctl_status

    if callback.data == "systemctl_status":
        systemctl_status = "status"
    elif callback.data == "systemctl_stop":
        systemctl_status = "stop"
    elif callback.data == "systemctl_start":
        systemctl_status = "start"
    else:
        systemctl_status = "restart"

    await callback.message.answer(
        f"<b>Enter systemctl UNIT name to <u>{systemctl_status}</u></b>",
        parse_mode="HTML"
    )
    await state.set_state(waitings.waiting_systemctl)

#=======# STATUS #=======#

status_prefix = "status_"
status_lines = 10
statuses = [
    f"{status_prefix}mem",
    f"{status_prefix}cpu",
    f"{status_prefix}disks"
]
scan_disks = [
    "/dev/*"
]
ps_limiter = 10

async def status(message: Message):
    hostname = await command_shell("hostname")
    ip = await command_shell("hostname -I")
    la = await command_shell(f"uptime | grep -Eo '[0-9],[0-9]{{2}}.*'")

    mem_total = await command_shell(r"""free -m | awk 'NR==2 {printf "%.2f\n",$2/1024}'""")
    mem_used = await command_shell(r"""free -m | awk 'NR==2 {printf "%.2f\n",$3/1024}'""")
    mem_avail = await command_shell(r"""free -m | awk 'NR==2 {printf "%.2f\n",$7/1024}'""")

    cpus = await command_shell(r"""top -bn1 | grep -Eo "[0-9].*" | awk 'NR==3 {print}' | column | sed 's/,  /  /g'""")
    uptime = await command_shell(f"uptime -p")

    counter = 1
    priv_disks = await command_shell(f"df -h | awk 'NR==1 {{print}}'") + "\n"
    for disk in scan_disks:
        output = await command_shell(f"df -h | grep -E '^{disk}'")

        if counter == len(scan_disks):
            priv_disks += f"{output}"
        else:
            priv_disks += f"{output}\n"        

    await message.answer(
        f"<b>Status of {hostname}</b>\n"
        f"{uptime}\n"
        f"\n<b><u>MEMORY STATUS</u></b>\n"
        f"<b>T/U/A: {mem_total} Gb | {mem_used} Gb | {mem_avail} Gb</b>\n"
        f"\n<b><u>CPU STATUS</u></b>\n"
        f"<b>Load Average:</b> {la}\n"
        f"<b>CPUs:</b> {cpus}\n"
        f"\n<b><u>DISKS STATUS</u></b>\n"
        f"<pre>{priv_disks}</pre>",
        parse_mode="HTML",
        reply_markup=keyboards.get_status_keyboard(buttonTypesStatus, status_prefix)
    )

async def status_definer(callback: CallbackQuery):
    await callback.answer()

    if callback.data == f"{status_prefix}mem":
        if buttonTypesStatus["mem"] == "TXT":

            mem_top = await command_shell(f"ps -eo 'pid ppid user %mem %cpu command' --sort=-%mem | awk '{{print substr($0,1,50)}}' | head -n {ps_limiter}")

            await callback.message.answer(
                f"<b>TOP {ps_limiter} MEMORY PROCESSES</b>\n\n"
                f"<pre>{mem_top}</pre>",
                parse_mode="HTML"
                )
        else:
            path = await command_image(f"ps -eo 'pid ppid user %mem %cpu command' --sort=-%mem | head -n {ps_limiter}")

            img = FSInputFile(path)
            await callback.message.answer_photo(
                img,
                caption=f"<b>Last {ps_limiter} lines of ps sorted by memory usage</b>",
                parse_mode="HTML"
            )
    elif callback.data == f"{status_prefix}cpu":
        if buttonTypesStatus["cpu"] == "TXT":
            cpu_top = await command_shell(f"ps -eo 'pid ppid user %mem %cpu command' --sort=-%cpu | awk '{{print substr($0,1,50)}}' | head -n {ps_limiter}")

            await callback.message.answer(
                f"<b>TOP {ps_limiter} CPU PROCESSES</b>\n\n"
                f"<pre>{cpu_top}</pre>",
                parse_mode="HTML"
                )
        else:
            path = await command_image(f"ps -eo 'pid ppid user %mem %cpu command' --sort=-%cpu | head -n {ps_limiter}")

            img = FSInputFile(path)
            await callback.message.answer_photo(
                img,
                caption=f"<b>Last {ps_limiter} lines of ps sorted by CPU usage</b>",
                parse_mode="HTML"
            )
    else:
        if buttonTypesStatus["disks"] == "TXT":
            df_stat = await command_shell("df -h")
            lsblk = await command_shell("lsblk | grep -v 'loop'")

            await callback.message.answer(
                f"<b>DF</b>\n"
                f"<pre>{df_stat}</pre>\n"
                f"\n<b>LSBLK</b>\n"
                f"<pre>{lsblk}</pre>",
                parse_mode="HTML"
                )
        else:
            path = await command_image("echo '|=============| DF |=============|\n';df -h; echo '\n|=============| LSBLK |=============|\n';lsblk | grep -v 'loop'")

            img = FSInputFile(path)
            await callback.message.answer_photo(
                img,
                caption=f"<b>Disks information</b>",
                parse_mode="HTML"
            )

#=======# LOGS #=======#

log_prefix = "logs_"
log_lines = 20
main_log_dir = "/var/log"
log_paths = {
    f"{log_prefix}syslog": "/var/log/syslog",
    f"{log_prefix}auth": "/var/log/auth.log",
    f"{log_prefix}dmesg": "/var/log/dmesg"
}
log_commands = {
    f"{log_prefix}syslog": f"sudo tail -n {log_lines} {log_paths[f'{log_prefix}syslog']}",
    f"{log_prefix}auth": f"sudo tail -n {log_lines} {log_paths[f'{log_prefix}auth']}",
    f"{log_prefix}dmesg": f"sudo tail -n {log_lines} {log_paths[f'{log_prefix}dmesg']}"
}

async def logs(message: Message):
    du_logs = await command_shell("sudo du -sh /var/log | awk '{print $1}'")

    await message.answer(
        f"<b>Log directory:</b> {main_log_dir}\n"
        f"<b>Size:</b> {du_logs}",
        parse_mode="HTML",
        reply_markup=keyboards.get_logs_keyboard(buttonTypesLogs, log_prefix)
    )

async def logs_definer(callback: CallbackQuery):
    await callback.answer()

    for log_type, path in log_paths.items():
        if log_type == callback.data:
            command = log_commands[log_type]

            if buttonTypesLogs[log_type[len(log_prefix):]] == "TXT":

                output = await command_shell(command)

                await callback.message.answer(
                f"<b>Last {log_lines} of {log_paths[log_type]}</b>\n\n"
                f"<pre>{output}</pre>",
                parse_mode="HTML"
                )
            else:
                path = await command_image(command)

                img = FSInputFile(path)
                await callback.message.answer_photo(
                    img,
                    caption=f"<b>Last {log_lines} of {log_paths[log_type]}</b>",
                    parse_mode="HTML"
                )

#=======# FALLBACK #=======#

async def fallback(message: Message):
    await message.answer(
        f"<b>Activate admin keyboard:</b> /start",
        parse_mode="HTML"
    )

#=======# HANDLERS #=======#

def register_handlers(dp: Dispatcher):
    dp.callback_query.register(tbut, F.data.startswith("tbut:"))

    dp.message.register(start, Command("start"))
    dp.message.register(system, F.text == "System")
    dp.message.register(status, F.text == "Status")
    dp.message.register(logs, F.text == "Logs")

    dp.callback_query.register(system_security, F.data == "system_security")
    dp.callback_query.register(system_systemctl, F.data == "system_systemctl")
    dp.message.register(answerw, waitings.waiting_systemctl)

    for fsystemctl_type_data in systemctl_statuses:
        dp.callback_query.register(systemctl_definer, F.data == f"systemctl_{fsystemctl_type_data}")

    for fstatus_type_data in statuses:
        dp.callback_query.register(status_definer, F.data == fstatus_type_data)
        
    for flog_type_data, path in log_paths.items():
        dp.callback_query.register(logs_definer, F.data == flog_type_data)
    
    dp.message.register(fallback)