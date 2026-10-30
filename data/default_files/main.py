
import asyncio
import time
import sys
import os
from cfonts import render

import login_engine
import bot_core

from bot_core import (
    TcPOnLine, TcPChaT,
    build_ob55_online_auth, create_auth_token_chat,
    bot_uid, ToKen, region
)
import random

def get_random_color():
    colors = [
        "FF0000",
        "00FF00",
        "0000FF",
        "FFFF00",
        "FF00FF",
        "00FFFF",
        "FF66CC",
        "FFD700"
    ]
    return random.choice(colors)


async def MaiiiinE():
    global bot_uid, ToKen, region

    Uid = '8374949927'
    Pw = '52F60D5AA2471C18DA78082E0AC561952D91122F4FEEA450CC7D89BB32630824'
    REGION_PREF = "BD"

    print_banner()
    log("INFO", "লগইন প্রক্রিয়া শুরু হচ্ছে ...")
    log("INFO", f"লক্ষ্য অঞ্চল: {REGION_PREF}")

    try:
        result = await login_engine.do_login(Uid, Pw, REGION_PREF)
    except Exception as e:
        log("ERROR", f"লগইন সমস্যা: {e}")
        return

    if not result:
        log("ERROR", "লগইন ব্যর্থ হয়েছে।")
        await asyncio.sleep(10)
        return

    bot_core.bot_uid = result["bot_uid"]
    bot_core.ToKen = result["token"]
    bot_core.region = result["region"]

    key = result["key"]
    iv = result["iv"]
    timestamp = result["timestamp"]
    online_ip = result["online_ip"]
    online_port = result["online_port"]
    chat_ip = result["chat_ip"]
    chat_port = result["chat_port"]
    acc_name = result["account_name"]
    clan_id = result.get("clan_id")
    clan_data = result.get("clan_data")

    # FINAL PREMIUM STATUS DISPLAY
    os.system("clear")

    RESET = "\033[0m"
    CYAN = "\033[1;36m"
    GREEN = "\033[1;32m"
    PURPLE = "\033[1;35m"

    print(PURPLE + "╔" + "═" * 58 + "╗" + RESET)
    print(CYAN + r"""
       ███████╗ █████╗ ███╗   ███╗██╗
       ██╔════╝██╔══██╗████╗ ████║██║
       ███████╗███████║██╔████╔██║██║
       ╚════██║██╔══██║██║╚██╔╝██║██║
       ███████║██║  ██║██║ ╚═╝ ██║██║
       ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝
""" + RESET)
    print(PURPLE + "╚" + "═" * 58 + "╝" + RESET)

    print_box("ACCOUNT INFORMATION", [
        f"UID          : {result['bot_uid']}",
        f"NAME         : {acc_name}",
        f"REGION       : {result['region']}",
        f"CLAN ID      : {clan_id or 'None'}",
        f"CHAT SERVER  : {chat_ip}:{chat_port}",
        f"GAME SERVER  : {online_ip}:{online_port}",
    ], GREEN)

    print_box("BOT STATUS", [
        "LOGIN SUCCESSFUL",
        "AUTHENTICATION READY",
        "TCP CONNECTION INITIALIZING",
    ], PURPLE)

    log("INFO", "অথেনটিকেশন টোকেন তৈরি করা হচ্ছে ...")

    ChatAutH = create_auth_token_chat(
        int(result["bot_uid"]), result["token"],
        int(timestamp), key, iv
    )
    OnlineAutH, _ = build_ob55_online_auth(
        int(result["bot_uid"]), result["token"],
        int(timestamp), key, iv
    )

    log("OK", "অথেনটিকেশন টোকেন তৈরি হয়েছে।")

    log("WAIT", "চ্যাট সার্ভারের সাথে সংযোগ স্থাপন করা হচ্ছে ...")
    ready_event = asyncio.Event()

    t1 = asyncio.create_task(
        TcPChaT(
            chat_ip, chat_port, ChatAutH, key, iv,
            ready_event, result["region"],
            clan_id=clan_id,
            clan_data=clan_data,
        )
    )

    await ready_event.wait()
    log("OK", "চ্যাট সার্ভার সংযোগ সফল হয়েছে।")

    await asyncio.sleep(1)

    log("WAIT", "অনলাইন সার্ভারের সাথে সংযোগ স্থাপন করা হচ্ছে ...")

    t2 = asyncio.create_task(
        TcPOnLine(online_ip, online_port, key, iv, OnlineAutH)
    )

    print()
    print("═" * 70)
    print(render('BOT ONLINE', colors=['green', 'white'], align='center'))
    print("═" * 70)
    print_line("Owner", "—͞ᏚAMI求 YT")
    print_line("Region", result['region'])
    print_line("Bot UID", result['bot_uid'])
    print_line("Name", acc_name)
    print_line("Clan", str(clan_id) if clan_id else "None")
    print_line("Status", "\033[1;32m● RUNNING\033[0m")
    print("═" * 70)

    await asyncio.gather(t1, t2)
    
    
def log(level, message):
    icons = {
        "INFO":  ("\033[1;36m", "ℹ"),
        "OK":    ("\033[1;32m", "✔"),
        "WAIT":  ("\033[1;33m", "⏳"),
        "WARN":  ("\033[1;33m", "⚠"),
        "ERROR": ("\033[1;31m", "✘"),
        "BOT":   ("\033[1;35m", "★"),
    }

    color, icon = icons.get(
        level,
        ("\033[1;37m", "•")
    )

    reset = "\033[0m"
    timestamp = time.strftime("%H:%M:%S")

    print(
        f"\033[1;90m[{timestamp}]{reset} "
        f"{color}{icon} {level:<5}{reset} │ {message}"
    )
#________________________________________________________SAMI UI________________#


def log(level, message):
    icons = {
        "INFO": ("\033[1;36m", "ℹ"),
        "OK": ("\033[1;32m", "✔"),
        "WAIT": ("\033[1;33m", "⏳"),
        "WARN": ("\033[1;33m", "⚠"),
        "ERROR": ("\033[1;31m", "✘"),
        "BOT": ("\033[1;35m", "★"),
    }

    color, icon = icons.get(level, ("\033[1;37m", "•"))
    reset = "\033[0m"
    ts = time.strftime("%H:%M:%S")

    print(f"\033[1;90m[{ts}]{reset} {color}{icon} {level:<5}{reset} │ {message}")



def print_banner():
    color = get_random_color()

    print(f"\033[1;35m{'═' * 60}\033[0m")
    print(render("💎 SAMI YT 💎", colors=["red", "white"], align="center"))
    print(render("PREMIUM TCP BOT", colors=["red", "white"], align="center"))
    print(f"\033[1;35m{'═' * 60}\033[0m")
    print(render("★ EVO • TEAM • MATCH ★", colors=["cyan", "white"], align="center"))
    print(render("© SAMI BOT PREMIUM", colors=["yellow", "white"], align="center"))
    print(f"\033[1;35m{'═' * 60}\033[0m")

def print_box(title, lines, color="\033[1;35m"):
    width = 60
    reset = "\033[0m"

    print(f"\n{color}┌{'─' * width}┐{reset}")
    print(f"{color}│{reset} {title.center(width - 1)}{color}│{reset}")
    print(f"{color}├{'─' * width}┤{reset}")

    for line in lines:
        print(f"{color}│{reset} {line:<{width - 1}}{color}│{reset}")

    print(f"{color}└{'─' * width}┘{reset}")


def print_line(title, value, icon="➤"):
    print(
        f"  {icon} \033[1;36m{title:<14}\033[0m : "
        f"\033[1;33m{value}\033[0m"
    )



async def StarTinG():
    attempt = 0

    while True:
        attempt += 1

        try:
            log("BOT", f"সেশন #{attempt} শুরু হচ্ছে")
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)

        except asyncio.TimeoutError:
            log("WARN", "সেশন শেষ হয়েছে। পুনরায় চালু হচ্ছে ...")
            await asyncio.sleep(3)

        except KeyboardInterrupt:
            log("WARN", "বট বন্ধ করা হয়েছে।")
            sys.exit(0)

        except Exception as e:
            log("ERROR", f"সমস্যা: {e}")
            await asyncio.sleep(5)


if __name__ == '__main__':
    try:
        asyncio.run(StarTinG())
    except KeyboardInterrupt:
        print("\nবট বন্ধ করা হয়েছে।")
