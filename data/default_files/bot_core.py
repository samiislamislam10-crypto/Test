# ═══════════════════════════════════════════════════════════════
# bot_core.py — —͞ᏚAMI求 SUPER BOT (প্রথম + দ্বিতীয় স্ক্রিপ্ট একত্রিত)
# ═══════════════════════════════════════════════════════════════

import asyncio, random, json, os, time, math, pickle
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from xC4 import *
from xP import JoinSq, OpenCh, MsqSq, ExitSq, PrOtO
from byte import Encrypt_ID, encrypt_api
from Pb2 import DEcwHisPErMsG_pb2, sQ_pb2

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import random

def get_random_color():
    return random.choice([
        "FF0000",
        "00FF00",
        "0000FF",
        "FFFF00",
        "FF00FF",
        "00FFFF",
        "FF66CC",
        "FFD700",
        "FFFFFF"
    ])

h1_color = get_random_color()
h2_color = get_random_color()
h3_color = get_random_color()
h4_color = get_random_color()
# ═══════════════════════════════════════════════════════════════
# GLOBALS
# ═══════════════════════════════════════════════════════════════

SPAM_TARGETS_FILE = "spam_targets.json"
online_writer = None
whisper_writer = None
spam_running = False
SPAM_INTERVAL = 0.5
bot_uid = None
ToKen = None
region = None
admin_uid = "18880512149"  # ⭐ আপনার UID এখানে সেট করা হয়েছে

pending_ghost_future = None
ghost_team_id = None
ghost_squad_code = None

spm_tasks = {}
ban_task = None
ban_running = False
ban_targets = set()
evo_cycle_running = False
evo_cycle_task = None
freeze_running = False
freeze_task = None
fast_spam_running = False
fast_spam_task = None
custom_spam_running = False
custom_spam_task = None
msg_spam_running = False
msg_spam_task = None
mg_spam_task = None
reject_spam_running = False
reject_spam_task = None
emote_hijack = False
bot_enabled = True

BOT_UID_FOR_HI = None
BOT_PW_FOR_HI  = None

BLOCK_EMOTE_UID = admin_uid
CACHE_FILE      = "status_cache.pkl"
CACHE_TIMEOUT   = 30

# ⭐ Clan Auto Message Globals ⭐
_clan_msg_key = None
_clan_msg_iv = None
_clan_msg_bot_uid = None
_clan_msg_clan_id = None
_clan_message_task = None

# ⭐ Badge Globals ⭐
BADGE_VALUES = {
    "s1": 1048576,
    "s2": 32768,
    "s3": 2048,
    "s4": 64,
    "s5": 262144
}
BADGE_REQUESTS = 5
PACKET_DELAY_ULTRA_FAST = 0.1

EVO_IDS = [
    909000063, 909000075, 909040010, 909000081, 909039011,
    909045001, 909038012, 909042008, 909051003, 909035012,
    909000098, 909033002, 909037011, 909049010, 909041005,
    909038010, 909033001, 909035007, 909000090, 909000085,
    909000068
]

# ═══════════════════════════════════════════════════════════════
# NEW EMOTE SYSTEMS
# ═══════════════════════════════════════════════════════════════

GENERAL_EMOTES_MAP = {}     
EMOTE_MAP          = {}     
NAME_TO_EMOTE_ID   = {}     
EMOTE_MENU         = {}     

try:
    with open("emotes.json", "r", encoding="utf-8") as _f:
        _raw = json.load(_f)
    for _num, _info in _raw.items():
        _id   = int(_info["id"])
        _name = str(_info.get("name", f"emote_{_num}"))
        GENERAL_EMOTES_MAP[str(_num)] = _id
        EMOTE_MAP[int(_num)]          = _id
        EMOTE_MENU[str(_num)]         = _name
        _n = _name.lower().strip()
        if _n and not _n.startswith("emote_") and _n not in NAME_TO_EMOTE_ID:
            NAME_TO_EMOTE_ID[_n] = _id
    print(f"✅ Loaded {len(GENERAL_EMOTES_MAP)} emotes from emotes.json")
    print(f"✅ Built {len(NAME_TO_EMOTE_ID)} name→emote mappings")
except Exception as _e:
    print(f"❌ emotes.json load error: {_e}")

try:
    with open("emote_menu.json", "r", encoding="utf-8") as _f:
        EMOTE_MENU = json.load(_f)
except Exception:
    EMOTE_MENU = {}

NAME_EMOTES = {
    "ak": 909000063, "scar": 909000068, "mp40": 909000075,
    "m1014": 909000081, "xm8": 909000085, "famas": 909000090,
    "ump": 909000098, "m1887": 909035007, "woodpecker": 909042008,
    "groza": 909041005, "m4a1": 909033001, "thompson": 909038010,
    "g18": 909038012, "parafal": 909045001, "p90": 909049010,
    "m60": 909051003, "fist": 909037011, "ring": 909050009,
    "heart": 909038004, "love": 909000010, "dance": 909000027,
    "hello": 909000001, "hi": 909000001, "money": 909000129,
    "lol": 909000002, "sad": 909038005, "angry": 909000014,
    "chicken": 909000006, "dab": 909000005, "selfie": 909000040,
    "shower": 909051004, "flower": 909051002, "petals": 909051013,
}
NUMBER_EMOTES = GENERAL_EMOTES_MAP

# ═══════════════════════════════════════════════════════════════
# ⭐ /menu — paginated emote menu builder
# ═══════════════════════════════════════════════════════════════

def get_menu_page(page=1, per_page=5):
    try:
        items = sorted(EMOTE_MENU.items(), key=lambda x: int(x[0]))
    except Exception:
        items = list(EMOTE_MENU.items())

    total_items = len(items)
    if total_items == 0:
        return "[B][C][FF0000]❌ Emote menu is empty."

    total_pages = max(1, math.ceil(total_items / per_page))
    try:
        page = int(page)
    except Exception:
        page = 1
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end   = start + per_page

    text  = f"[B][C][FF0000]🎭 MENU {page}/{total_pages}\n"
    text += f"[C][FFFFFF]────────────────\n"

    for num, name in items[start:end]:
        text += f"[C][FFFFFF]{num} ➤ [FFFF00]{name}\n"

    text += f"[C][FFFFFF]────────────────\n"
    nav = []
    if page > 1:
        nav.append(f"[00FF00]/menu {page-1} ◀")
    if page < total_pages:
        nav.append(f"[00FF00]/menu {page+1} ▶")
    if nav:
        text += f"[C]{'  '.join(nav)}\n"

    return text

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def load_spam_targets():
    if os.path.exists(SPAM_TARGETS_FILE):
        with open(SPAM_TARGETS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_spam_targets():
    with open(SPAM_TARGETS_FILE, "w") as f:
        json.dump(list(spam_targets), f)

spam_targets = load_spam_targets()


def get_random_color():
    return random.choice(["[FF0000]", "[FFFFFF]"])


def get_random_avatar():
    avatar_list = [
        902050001, 902050002, 902050003, 902039016, 902050004,
        902047011, 902047010, 902049015, 902050006, 902049020
    ]
    return random.choice(avatar_list)


def get_random_sticker():
    sticker_packs = [
        ("1200000001", 1, 24),
        ("1200000004", 1, 15),
        ("1200000002", 1, 13),
    ]
    pack_id, start, end = random.choice(sticker_packs)
    sticker_no = random.randint(start, end)
    return f"[1={pack_id}-{sticker_no}]"


def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i + 3] for i in range(0, len(str(n)), 3))


def fix_num(number):
    fixed = ""
    count = 0
    num_str = str(number)
    for char in num_str:
        if char.isdigit():
            count += 1
        fixed += char
        if count == 3:
            fixed += "[c]"
            count = 0
    return fixed

def fixnum(num):
    num_str = str(num)
    return "[C]" + "[C]".join(num_str) + "[C]"


def dec_to_hex(decimal):
    hex_str = hex(decimal)[2:]
    return hex_str.upper() if len(hex_str) % 2 == 0 else '0' + hex_str.upper()


async def encrypt_packet(packet_hex, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    packet_bytes = bytes.fromhex(packet_hex)
    padded_packet = pad(packet_bytes, AES.block_size)
    return cipher.encrypt(padded_packet).hex()


async def nmnmmmmn(packet_hex, key, iv):
    return await encrypt_packet(packet_hex, key, iv)


# ═══════════════════════════════════════════════════════════════
# AUTH TOKEN BUILDERS
# ═══════════════════════════════════════════════════════════════

def build_ob55_online_auth(account_uid, token, kts, key, iv):
    token_bytes = token.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc_token = cipher.encrypt(pad(token_bytes, 16))
    opcode = bytes.fromhex("830c")
    uid_bytes = int(account_uid).to_bytes(8, byteorder="big")
    kts_bytes = int(kts).to_bytes(4, byteorder="big")
    len_bytes = len(enc_token).to_bytes(8, byteorder="big")
    return opcode + uid_bytes + kts_bytes + len_bytes + enc_token, enc_token


def create_auth_token_chat(account_id, jwt_token, timestamp, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv) if isinstance(iv, str) else iv
        jwt_bytes = jwt_token.encode('utf-8')
        ct = AES.new(K, AES.MODE_CBC, V).encrypt(pad(jwt_bytes, AES.block_size))
        uid_b = int(account_id).to_bytes(8, 'big')
        ts_b = int(timestamp).to_bytes(4, 'big')
        len_b = len(ct).to_bytes(4, 'big')
        header = bytes.fromhex('6d19') + uid_b + ts_b + len_b
        return (header + ct).hex()
    except Exception as e:
        print(f"[AUTH TOKEN ERROR] {e}")
        return None


async def cHTypE(H):
    if not H:
        return 'Squid'
    elif H == 1:
        return 'CLan'
    elif H == 2:
        return 'PrivaTe'


async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto


async def GeTSQDaTa(D):
    try:
        return D['5']['data']['1']['data'], D['5']['data']['17']['data'], D['5']['data']['31']['data']
    except KeyError:
        return None, None, None


async def get_colorful_message(message_text, message_number):
    color = "FF0000" if message_number % 2 else "FFFFFF"
    return f"[C][B][{color}]{message_text}"


# ═══════════════════════════════════════════════════════════════
# PACKET BUILDERS
# ═══════════════════════════════════════════════════════════════

async def NewClanChatPacket(message_text, key, iv, clan_id=3102281341):
    fields = {1: 16801068917, 2: 18, 4: 1, 5: {1: 16801068917, 2: clan_id, 3: 1, 4: 'ᏚAMI YT',
        5: 1785944381, 7: 6, 9: {1: message_text, 4: 301, 8: '♧ᏚAMI YT♧', 13: '',
        14: {1: 16801068917}, 18: {1: 16801068917, 3: 1, 4: ''}},
        10: 'ar', 13: {2: 1, 3: 1}, 14: '', 16: int(time.time() * 1000)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)


async def AuthClan(clan_id, clan_compiled_data, key, iv):
    if isinstance(clan_compiled_data, str):
        try:
            clan_compiled_data = clan_compiled_data.encode(
                'latin-1', errors='surrogateescape'
            )
        except Exception:
            clan_compiled_data = clan_compiled_data.encode(
                'utf-8', errors='surrogateescape'
            )
    fields = {1: 3, 2: {1: int(clan_id), 2: 1, 4: clan_compiled_data}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1201', key, iv)


async def SEndMsG(H, message, Uid, chat_id, key, iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid':
        return await xSEndMsgsQ(message, chat_id, key, iv, region or "BD")
    elif TypE == 'CLan':
        try:
            return await xSEndMsg(message, 1, chat_id, chat_id, key, iv)
        except Exception as e:
            print(f"Guild old packet error, fallback: {e}")
            return await NewClanChatPacket(message, key, iv, chat_id)
    elif TypE == 'PrivaTe':
        return await xSEndMsg(message, 2, Uid, Uid, key, iv)


async def SEndPacKeT(OnLinE, ChaT, TypE, PacKeT):
    if TypE == 'ChaT' and ChaT:
        whisper_writer.write(PacKeT); await whisper_writer.drain()
    elif TypE == 'OnLine':
        online_writer.write(PacKeT); await online_writer.drain()


async def safe_send_message(chat_type, message, uid, chat_id, key, iv, max_retries=3):
    for attempt in range(max_retries):
        try:
            packet = await SEndMsG(chat_type, message, uid, chat_id, key, iv)
            if packet:
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', packet)
                return True
        except Exception as e:
            print(f"❌ Send fail (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)
    return False


# ═══════════════════════════════════════════════════════════════
# WELCOME (invite accept করার পর delay দিয়ে)
# ═══════════════════════════════════════════════════════════════

HELP_DELAY = 0.1
WELCOME_DELAY = 1
WELCOME_COOLDOWN = 1800

WELCOME_TEXT = (
    "╔══════════════════════════════╗\n"
    "║            TCP BOT         ║\n"
    "║        WELCOME USER          ║\n"
    "╚══════════════════════════════╝\n"
    "\n"
    "  Hello, Welcome to TCP BOT!\n"
    "\n"
    "╭─────── ✦ FEATURES ✦ ───────╮\n"
    "➤  AI System\n"
    "➤  Fun Commands\n"
    "➤  Tools System\n"
    "➤  Download System\n"
    "➤  Fast Response\n"
    "╰────────────────────────────╯\n"
    "\n"
    "  Type /help to see all commands\n"
    "  Type menu to open menu\n"
    "\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "         TCP BOT PREMIUM  \n"
    "       Fast • Secure • Smart\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)
WELCOMED = {}


async def send_welcome(chat_code, key, iv, delay=None):
    now = time.time()
    last = WELCOMED.get(chat_code)
    if last and now - last < WELCOME_COOLDOWN:
        return
    WELCOMED[chat_code] = now
    await asyncio.sleep(WELCOME_DELAY if delay is None else delay)
    await safe_send_message(0, WELCOME_TEXT, None, chat_code, key, iv)

# ═══════════════════════════════════════════════════════════════
# ⭐ CLAN AUTO MESSAGE ⭐
# ═══════════════════════════════════════════════════════════════
async def clan_message_loop():
    """Send clan message on startup and every 5 hours"""
    global _clan_msg_key, _clan_msg_iv, _clan_msg_bot_uid, _clan_msg_clan_id
    try:
        await asyncio.sleep(5)
        if _clan_msg_clan_id and _clan_msg_clan_id > 0 and _clan_msg_key and _clan_msg_iv:
            clan_msg = "Dev UID: 🤫52🤫76🤫59🤫27🤫66🤫"
            await safe_send_message(1, clan_msg, _clan_msg_bot_uid, _clan_msg_clan_id, _clan_msg_key, _clan_msg_iv)
            print(f"[CLAN] Startup message sent to clan {_clan_msg_clan_id}")
        
        while True:
            await asyncio.sleep(18000)  # 5 hours
            if _clan_msg_clan_id and _clan_msg_clan_id > 0 and _clan_msg_key and _clan_msg_iv:
                clan_msg = "Dev UID: 🤫52🤫76🤫59🤫27🤫66🤫"
                await safe_send_message(1, clan_msg, _clan_msg_bot_uid, _clan_msg_clan_id, _clan_msg_key, _clan_msg_iv)
                print(f"[CLAN] 5-hour message sent to clan {_clan_msg_clan_id}")
    except asyncio.CancelledError:
        print("[CLAN] Message loop cancelled")
    except Exception as e:
        print(f"[CLAN] Message loop error: {e}")


# ═══════════════════════════════════════════════════════════════
# DEVIL BANNER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

async def base_to_hex(number):
    hex_str = hex(number)[2:]
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return hex_str.upper()

async def DEVIL(client_id, key, iv):
    banner_text = f""" 
.
.
.










    
[B][C][00FF00]★  N E - H O S T 		T E A M★
[FF0000]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][FF9900]D O N E   H A C K I N G
[B][C][E75480]Y O U R   A C C O U N T
[81DACA]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][FF0000]F U C K   Y O U
[CCFFCC]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][81DACA]P O W E R E D   B Y  D E V I L
[FFFF00]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][00FF00]F O L L O W   M E   O N    T I  K
T O k :
[B][C][FFFFFF]@shihab_editz_843
[00008B]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][81DACA]I F   Y O U   D O N T   F O L L O W   M E
[B][C][FF0000]I   W I L L   B A N   Y O U R   A C C O U N T
        """
    fields = {
        1: 5,
        2: {1: int(client_id), 2: 1, 3: int(client_id), 4: banner_text}
    }
    packet = await CrEaTe_ProTo(fields)
    packet_hex = packet.hex()
    encrypted_packet = await EnC_PacKeT(packet_hex, key, iv)
    header_length = len(encrypted_packet) // 2
    header_length_final = await DecodE_HeX(header_length)
    if len(header_length_final) == 2:
        final_packet = "0515000000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 3:
        final_packet = "051500000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 4:
        final_packet = "05150000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 5:
        final_packet = "0515000" + header_length_final + encrypted_packet
    else:
        final_packet = "0515000000" + header_length_final + encrypted_packet
    return bytes.fromhex(final_packet)


async def DEVIL1(client_id, key, iv):
    gay_text = f""" 
.
.
.










    
[B][C][00FF00]★  N E - H O S T 		T E A M★
[FF0000]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][FF9900]D O N E   H A C K I N G
[B][C][E75480]Y O U R   A C C O U N T
[81DACA]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][FF0000]F U C K   Y O U
[CCFFCC]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][81DACA]P O W E R E D   B Y  D E V I L
[FFFF00]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][00FF00]F O L L O W   M E   O N    T I  K
T O k :
[B][C][FFFFFF]@shihab_editz_843
[00008B]━━━━━━━━━━━━━━━━━━━━━━━━━━
[B][C][81DACA]I F   Y O U   D O N T   F O L L O W   M E
[B][C][FF0000]I   W I L L   B A N   Y O U R   A C C O U N T
        """
    fields = {1: int(client_id), 2: 5, 4: 50, 5: {1: int(client_id), 2: gay_text}}
    packet = await CrEaTe_ProTo(fields)
    packet_hex = packet.hex()
    encrypted_packet = await EnC_PacKeT(packet_hex, key, iv)
    header_length = len(encrypted_packet) // 2
    header_length_final = await DecodE_HeX(header_length)
    if len(header_length_final) == 2:
        final_packet = "0515000000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 3:
        final_packet = "051500000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 4:
        final_packet = "05150000" + header_length_final + encrypted_packet
    elif len(header_length_final) == 5:
        final_packet = "0515000" + header_length_final + encrypted_packet
    else:
        final_packet = "0515000000" + header_length_final + encrypted_packet
    return bytes.fromhex(final_packet)


# ═══════════════════════════════════════════════════════════════
# BADGE COMMAND FUNCTIONS
# ═══════════════════════════════════════════════════════════════

async def request_join_with_badge(target_uid, badge_value, key, iv, region):
    fields = {
        1: 33,
        2: {
            1: int(target_uid),
            2: region.upper(),
            3: 1,
            4: 1,
            5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]),
            6: "iG:[C][B][FF0000] KRISHNA",
            7: 330,
            8: 1000,
            10: region.upper(),
            11: bytes([49, 97, 99, 52, 98, 56, 48, 101, 99, 102, 48, 52, 55, 56, 97, 52, 52, 50, 48, 51, 98, 102, 56, 102, 97, 99, 54, 49, 50, 48, 102, 53]),
            12: 1,
            13: int(target_uid),
            14: {
                1: 2203434355,
                2: 8,
                3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
            },
            16: 1,
            17: 1,
            18: 312,
            19: 46,
            23: bytes([16, 1, 24, 1]),
            24: int(get_random_avatar()),
            26: "",
            28: "",
            31: {
                1: 1,
                2: int(badge_value)
            },
            32: int(badge_value),
            34: {
                1: int(target_uid),
                2: 8,
                3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])
            }
        },
        10: "en",
        13: {
            2: 1,
            3: 1
        }
    }
    packet = (await CrEaTe_ProTo(fields)).hex()
    if region.lower() == "ind":
        packet_type = '0514'
    elif region.lower() == "bd":
        packet_type = "0519"
    else:
        packet_type = "0515"
    return await GeneRaTePk(packet, packet_type, key, iv)

async def handle_badge_command(cmd, inPuTMsG, uid, chat_id, key, iv, region, chat_type):
    parts = inPuTMsG.strip().split()
    if len(parts) < 2:
        error_msg = f"[B][C][FF0000]❌ Usage: /{cmd} (uid)\nExample: /{cmd} 123456789\n"
        await safe_send_message(chat_type, error_msg, uid, chat_id, key, iv)
        return
    target_uid = parts[1]
    badge_value = BADGE_VALUES.get(cmd, 1048576)
    if not target_uid.isdigit():
        error_msg = f"[B][C][FF0000]❌ Please write a valid player ID!\n"
        await safe_send_message(chat_type, error_msg, uid, chat_id, key, iv)
        return
    total_requests = BADGE_REQUESTS
    packet_delay = PACKET_DELAY_ULTRA_FAST
    badge_names = {
        's1': 'Craftland Badge 🏆',
        's2': 'New V-Badge 🔥',
        's3': 'Moderator Badge 👮',
        's4': 'Small V-Badge ⚡',
        's5': 'Pro Badge 💎'
    }
    badge_name = badge_names.get(cmd, 'Unknown Badge')
    initial_msg = f"[B][C][1E90FF]🌀 {badge_name}\n🎯 Target: {target_uid}\n📦 Requests: {total_requests}\n⚡ Speed: {packet_delay}s\n"
    await safe_send_message(chat_type, initial_msg, uid, chat_id, key, iv)
    try:
        leave_packet = await ExiT(None, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)
        await asyncio.sleep(0.3)
        
        join_packet = await request_join_with_badge(target_uid, badge_value, key, iv, region)
        for i in range(total_requests):
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
            await asyncio.sleep(packet_delay)
            
        success_msg = f"[B][C][00FF00]✅ {badge_name} COMPLETE!\n🎯 Target: {target_uid}\n📦 Sent: {total_requests} requests\n⚡ Speed: {packet_delay}s\n"
        await safe_send_message(chat_type, success_msg, uid, chat_id, key, iv)
    except Exception as e:
        error_msg = f"[B][C][FF0000]❌ Error in /{cmd}: {str(e)}\n"
        await safe_send_message(chat_type, error_msg, uid, chat_id, key, iv)

async def Room_Spam(Uid, Rm, Nm, K, V):
    badge_sequence = [1048576, 32768, 2048, 64, 262144]
    badge_index = 0
    for i in range(3000): 
        try:
            current_badge_value = badge_sequence[badge_index % 5]
            fields = {
                1: 78, 2: {1: int(Rm), 2: "iG:[C][B][FF0000]DEVIL CODEX", 3: {2: 1, 3: 1}, 4: 330, 5: 6000, 6: 201,
                    10: int(get_random_avatar()), 11: int(Uid), 12: 1,
                    15: {1: 1, 2: current_badge_value}, 16: current_badge_value,
                    18: {1: 11481904755, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
                    31: {1: 1, 2: current_badge_value}, 32: current_badge_value,
                    34: {1: int(Uid), 2: 8, 3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])}}}
            spam_packet = await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0e15', K, V)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', spam_packet)
            badge_index += 1
            await asyncio.sleep(PACKET_DELAY_ULTRA_FAST)
        except Exception: await asyncio.sleep(0.1)
    return True


# ═══════════════════════════════════════════════════════════════
# FULL PACKET BUILDERS (NO SHORTCUTS)
# ═══════════════════════════════════════════════════════════════

async def JoinSq_original(code, K, V):
    skinz = {1: 4, 2: {4: "\u0001\u0007\t\n\u000b\u0012\u0019 '", 5: str(code), 6: 6, 8: 1,
        9: {1: "08FFF3BE903F27DF0203110111110000006B0003006800169194106F13CF106E4676251411010404dfe9e8b5ca3ca4f96a3119c00000004f03060301cacfa16d",
            2: 130, 3: "tY_S\u0013\b\u0001M\u0002\u0000T\u0000\u0005\u000e\b\t\u0002\u0000\u0003U\u0003\u0001V\u000fR\u000e\tRQ\u0002\u0004\u0005US\u0003XS\u0005\u0001\u0002\u0011\u0001\u0002JuTAEN\u001e\u0002\u001c\u0002\u001f\u0013\b\u0003M\u001cDbz_Q@}p_QOgsC\u001dYVI\u0004UAAj_ga\u0004\u0012\u0000K\u001d\u0007_t\u0019b\bCx\u0002UeGat\u001fTTCBLER`\u0006\u0001\r\f\u0012\u0006\u0005N^^\u0002acH~r\u0004_\u0003RO|\u000bcd_@~`Rnqrgh\n\u0015\nL\\Nh\u0000~G\u000et\u0000eb]VQ\u0006t^F[ZIGxCdZD\u000b\u0011\u0002OA~LP@\u000fcSDyATQApaT^{|wa]\\\u0001E\u000f\u0013\nJfxve}\u0004J\u0003c{YL\u0007^^yDYQf\bhe\u0005_wg\r\u0010\u0007\bEHpX@||\u0002Z\\uTGyA\u0001JP\u0005t~VkTE\u0000J\\\u000b\u0013\nMr\u0018zTzK}qE]vnvwROuheYvwduvQ\r\u001a\u0005M\u0006z\u001dfXfzvHFc~dXUz}O\u001aB\u0005t\u0002i\u001co_\u0004\u0012\u0003\u0007J\u0006b\u0003\u000eqlfvbEstgu~wB\u0001v@`yI\u0002ZPx\f\u0014\u0003NR\u0002yBZvuD_cd\u0004q]lH]\u0007bD}pCe\t\u0004t\n",
            4: "w^_R", 6: 11, 7: "\u0014\u0004aqrg\u0015\u0013", 8: "1.132.1", 9: 3, 10: 2,
            11: "\u0003bbSQ6wxegh9qAdV2KyoVleA17yPmYF+yTnOrl+JMknmppeUBe5ZsiHueP2mZZ4KOs6b2Ail1S9z3qIeU9hGFZ2M6PP39/zjIc/RFVPAkgDagySswMVmYaPhkzU5IqNPow2843fyQUz9xI10NdMhl1WiI4Y6wCXBotiUS9wSgujQ4j0fWXUyklCxBWo8r27hyoGSVrPdTPXFMnJJpPRRFFmWqc3fWvMg+BNfxSRJOZRSrkzG0nNvSIJ4uZB2pqAlHIPEYx7bI6zsgwUVDiLZJKTUTyuCGbOd1DegDUFfazFesTG1LJknT5WhgzCsrBIy+f2l+LeJe5DW7wEwNaHambM7ECXcJcLIhB9kJJsW0tFvXkk3HSdcQ8N1K6wjSKWhpkW0kV8Zrjj0jkhS/7AZ6T9GJRIA827YDtTorBvbx1UkXjYrqYI1nSa2GaMexGnqlurc5DE3v1R+mUBI9GqmjEPgTSYVBxyeCdQMHaMXGtspAhvkiO84ToU87sP45pylDEfFOVoc/rcmdzWeqlYPsv6txKRtIHcb0cO+MoVShoU8ZUVRDF3znbqzVrscPIfplBaa79lwvQqzRubLl9XY="},
        11: {1: "IDC4", 2: 281, 3: "ME"}, 13: "fr", 16: "7OR\u0019", 20: "\b\u0015", 27: "\bH\u0010\u0003"}}
    return await GeneRaTePk((await CrEaTe_ProTo(skinz)).hex(), '0515', K, V)


async def ᏚAMIAccepted(uid, code, K, V, region):
    fields = {1: 4, 2: {1: int(uid), 3: int(uid), 4: "rYUW\u0017\t\u0007NR\u000f\u0005\u0004\\W\u0002\u000fV\u0004TPQ\u0003\u000f\u0005\u0004]\u0005\u000b\u0000\u0002W\u0005\r\nVY\u0004\u0007\u0007\u0007\u0017\u0001\bNQ\fS\u0005\u000e\u0006\f\u0005\rT\u0002\r\u0000TS\u0007U\u0004X\u0006RY\u0005\u0003\u0003SW\u0000\u000eQ\u0000^\u0014\u0003\u0004JXS\u000f\u0000g{gqfePblEZJp{_xU\bmQW\f\u0007\u000f\u0015\u0007H\\U^CHXh@Ax`\u000f~\rPN~Nz\\\u001fr_ckPU\u000b\u0015\u0005\u0003Ekfp\u007fcY\u0001nWV\u0002\u0005azE~N\u0007HTg\u0007w}@\u0002{\t\u0013\u0001NeNP]DUf|]ugINs{\u0001\\rAgB_\u0004fA]\u0004\r\u001a\u0000HpOv\\\u0005|gS\u0019\\A\u007fWW\u0003\u007fTqFGi\u0004Qr\u0019dW\u0004\u0011\rD\u0002yeZ]A\u0016a\u0007Ungeg\u0007E\\P\u001b\u000b\u0004\u0005dd\ff\r\u000f\u0017\t\u000fNRyZd\u0012tZ\fe\u0007AGv\u007fw]{P\u001c\u007f\u000ff\u0005ZJK\u0004\u0005\u0014\u0001Jgq\u001frymsB\u0001\u000fd`\u001bj~[}\u0004SDZ|IxKB\u0000\n\u0011\u0002J^`tjYN\u0007WQdE[PQ\u0002_{VP`S\t\u007f\u001dP\n\u000f\u000f\u0015\u0004\u0004L{V\u0003@yP[rgJ{Hpk\u0001\u000bw\u0001Agt_\u0003HxPc\u000b\u0017\u0005E`y\ngWoy\u0006S{A\u001b``Y\u0002Xzw}dDWOKsg\t\u0013\u000eNf\u000e\\`\u0005AwJc\u0003BM\u0001^\u0000R\u0002Qoh]tbS~`G\r\u001a\u0004HibAQ\u000f^XNt~kDUWaeaNqcLQ]Py[G\u0004",
            8: 1, 9: {1: "08FBA33CFF105FDD02030A01111100000003000100020000B687046B0D6D2083467625141101030175a63c900e748c3f6a311e04000000ff00040202cacfa16d",
            2: 197, 3: "735154531406054a035305025a0e50560f5100040250020f5e0401520653000303505e0d520302501500064d705548424e1f051a001e12040a441d45677f5a56477574565e4f6274451d585849005a4f456d5b64670c1400496d017842740c670100040069536e72586c02016e657e566b524403081500044d0d515b637f757c19095c7c510b00417f565e5e066f5b584d6e02400a160e4d58496d0177400e750763605c575d0f7d5f475e5f4c407f4b60534b0b140549751e66407a4860726e44400e6103557e515c646f43577106077b60051b0f4b4e474e58457e4f615c01406000051e0361516e7b67614e040102540c1609004a0e40730f62517f446a135179507e706850547f7e7a67795553597c0a1206445b456640046265725c4d505d446d50737b7c42035970486370645e0b12034d506f5c7a1c554f574b0e765a0f0a7364505203477569456c6c420f0a1604014b647149136c186f795f5d78755e550e7842545e53747b08705f7f5d0a14004a08666b5a5b5f00045c7f5e584d72584262705f56055c61475564790515004b76514178587f52797a0f077a070953507d7f4d784f794f667b4256081b0e4a75627d4778417a06717574747c4c78557b4b7a0a697f0e714573600a",
            4: "{Y_R", 6: 13, 7: "1c6f017306741513", 8: "2.126.22", 9: 2, 10: 1,
            11: "036262535136784d584e38742b416456324b796f566c6537392f763672324d4773683377706379634f6b6b6f7447397934523930517432797246474c464c624c777a7747344d4d5257623146756d2b6556777a62597736743973492b787059612f55596e43465a59485235713348705830306c485a6f3632565145574e7145705866414c38734a754646575247386d376f5444566a4c484c576e714c52576f4e653236437a734c346a4144482b71694b55384d71476c5936546669544863716c487a345568463869396a365233366d49774b71746c36714f797568513854367945714b69742f45466d2b3636634b787649304f384d6c41385166454b6253467366477a2f30684e6a543873305369722f3962635a2f4679376c752f61632f366765704d415734566b442b36374f535756473665377a775a79312b797a42334b70632b7571782b577437414d39727761644439575765704570567849526d66654f5847627775787a68574b5664344c49586f415a364b387063647450627953575857455135706a542b653669365a2f6177444a3179356f774d5a534f64487262392b7877424a4d444f7848565a7a483372547a30314a316738517675466b656c3042433746473630683456427041494457487956684e794b4f5145507139467a4a6272686b316146306768766578512f6a2f484767426a5268675134645243372b477a5a687a2b77505967376454746f2b494d56363774642b54435653314234346b4148395a6d415872763758615941626477644e664f533170484875736b7336346f72463452534d3772656345417661484e61484854314c5545686e786a5a616d4d4f303d"},
            10: str(code), 11: {1: "IDC3", 2: 84, 3: "BD"}, 13: "en", 16: "374f5219",
            20: {1: 21}, 23: "a_1477547277882450725", 27: {1: 2, 2: 8}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)


async def accept_squad_invite(group_id, joiner_account_id, invitee_type, key, iv, region="bd"):
    fields = {1: 38, 2: {1: int(group_id), 2: int(joiner_account_id), 8: int(invitee_type)}}
    pkt_type = '0514' if region.lower() == "ind" else ('0519' if region.lower() == "bd" else '0515')
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pkt_type, key, iv)


async def leave_channel_req(channel_id, channel_type, key, iv):
    fields = {1: 4, 2: {1: int(channel_id), 2: int(channel_type), 3: "en"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', key, iv)


async def SPamSqForSpm(Uid, K, V):
    same_value = random.choice([4096, 16384, 8192])
    fields = {1: 33, 2: {1: int(Uid), 2: "ME", 3: 1, 4: 1,
        5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]), 6: "iG:[C][B][FF0000] @shihab231",
        7: 330, 8: 1000, 10: "ME",
        11: bytes([49,97,99,52,98,56,48,101,99,102,48,52,55,56,97,52,52,50,48,51,98,102,56,102,97,99,54,49,50,48,102,53]),
        12: 1, 13: int(Uid),
        14: {1: 2203434355, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
        16: 1, 17: 1, 18: 312, 19: 46, 23: bytes([16, 1, 24, 1]),
        24: await xBunnEr(), 26: "", 28: "",
        31: {1: 1, 2: same_value}, 32: same_value,
        34: {1: int(Uid), 2: 8, 3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])}},
        10: "en", 13: {2: 1, 3: 1}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)


async def GhostPakcet(player_id, nm, secret_code, key, iv):
    fields = {1: 61, 2: {1: int(player_id), 2: {1: int(player_id), 2: 1159,
        3: f"[b][c]{get_random_color()}{nm}", 5: 12, 6: 999, 7: 1,
        8: {2: 1, 3: 1}, 9: 3}, 3: secret_code}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)


async def xSKINZxLag(K, I):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 15, 2: {1: 804266360, 2: 1}})).hex(), '0515', K, I)


async def xBaNchaTxSkInZ(uidd, K, V):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 3, 2: {1: int(uidd), 3: "fr", 4: "1750728024661459697_3qind8eeqs"}})).hex(), '1215', K, V)


async def create_lw5_packet1(key, iv):
    fields = {1: 1, 2: {2: "0b", 3: 43, 4: 1, 5: "en", 8: {1: "IDC3", 2: 109, 3: "BD"},
        9: 1, 10: "01090a0b12192027", 11: 1, 13: 1,
        14: {1: "08FBA33CFF11B915020FEB099999000002BF000C02B3024798E574700E9B7471467625142200004375a63c900e748c3f6a311e04000000ff42002b09cacfa16d",
            2: 1023, 3: "715c5f561b06054a03530500570555590f5100040250000255010e520653000303525306570c02501500064d72584347411f051a001e1206074f184a677f5a564775765b554a6d74451d58584902574440625b64670c14004b600a7d4d740c670100040264586b7d586c02016e657c5b60574b03081500044d60795258726206047f04600f405b18710347746242085f055442530a160e4d58496f0c7c4501750763605c575f02765a485e5f4c407f4b625e400e1b054973535b40655e5151566e6507797e6b47727a1c6e455762637d650708100a447e704c1e530200437a604b66065d595f58444c5a06095a6c44677a0c14040b4f705b7d75624374067840416d60067353017f5972506356014354680a12044950406940046265725c4f5d56416250737b7c42035b7d43667f645e0b12034d5262577f13554f574b0e76580201766b50520347756947616747000a1604014b6473441869176f795f5d78755c58057d4d545e53747b08725274580514004a08666b585654050b5c7f5e584d725a4f69755056055c61475566740e100f4b76514178587d5f727f00077a070953507f72467d40794f667b42560a16054f7a627d4778417a047c7e717b7c4c78557b4b7807627a01714573600a",
            4: "{Y_R", 6: 13, 7: "136601706b6f54001513", 8: "2.126.20", 9: 2, 10: 1,
            11: "0362625351367a6e2f56386835416456324b796f566c576a3265735033734558335070623443526c656c47355732327673496e477a425a49677375684a664336766942532f4277526d3632374a624a724c562b586b664c516c6749424634615664544e34473869494c456e4c7643347754354670754e66444b7746367765466d675a2b2b36704d57694549677343415756457144554a454d737271515a306b544266635a45334959485661774d5332622b4f6b5a477a755171576e3645624c6a3932646c31307754614d55714e355556796742506f454572376651673249754332545a773333796c71493838627562512f6e425072353577785436617955544d63624d2b756d4542345a736c5165504d58725365737864622f30577967786849384a352f73484f685730494a49643450534b6d6a41734b315251495257634c35646355554b457a6d33334475735877384a5267483364412b66414b336433726a4241317954327451326c2f73584c6d4b4b6456707062624b4f3272694c384947382b634a3863506533314241456d517876744f495631323658394c4b35414c6a38533631526d6159617077676e4579724a5a7a624d4c596c3542554b6d7934473546334c6152454c4e6d726a684f557065462f39686f64356c526378623250777244566d455665715355764a456548644e375279344c707035563466392f6f6d3837426b5a6c6159364c5439396b5579554266434c5538647a4a2b43655a35784a44585064654a51686e46496945506e7a506d32334b637a2b512b384a51307a522b5a5a41762b694873454748516a536e61467862356a517a526c374f5a793241385731437263513d"},
        19: 329, 21: "374f5219", 24: {1: 21}, 27: "a_1477547277882450725"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)


async def create_lw5_packet2(key, iv):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 17, 2: {1: 17165783357, 2: 1, 3: 4, 4: 6100, 5: b'\x1a', 8: 5, 13: 329}})).hex(), '0515', key, iv)


async def send_sticker_packet(target_uid, chat_id, key, iv, nickname="SB"):
    try:
        sticker_value = get_random_sticker()
        fields = {1: 1, 2: {1: int(target_uid), 2: int(chat_id),
            5: int(time.time()), 8: f'{{"StickerStr" : "{sticker_value}", "type":"Sticker"}}',
            9: {1: f"[C][B][FF0000]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007,
                8: "SB TEAM", 10: 1, 11: 66, 12: 66, 13: {1: 2},
                14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}},
            10: "en", 13: {2: 2, 3: 1}, 14: {}}}
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Sticker error: {e}")
        return None


async def animation_packet(animation_id, key, iv):
    fields = {1: 88, 2: {1: {1: int(animation_id)}}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    pl = len(encrypted) // 2
    hl = format(pl, 'x')
    final = "051500" + "0" * (6 - len(hl)) + hl + encrypted
    return bytes.fromhex(final)


async def Look_Changer(bundle_id, key, iv, look_type=1, region="bd"):
    fields = {1: 88, 2: {1: {1: bundle_id, 2: look_type}, 2: 2}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if region.lower() == "ind":
        pt = "0514"
    elif region.lower() == "bd":
        pt = "0519"
    else:
        pt = "0515"
    if len(hl) == 2:
        h = f"{pt}000000"
    elif len(hl) == 3:
        h = f"{pt}00000"
    elif len(hl) == 4:
        h = f"{pt}0000"
    elif len(hl) == 5:
        h = f"{pt}000"
    else:
        h = f"{pt}000000"
    return bytes.fromhex(h + hl + encrypted)


async def banecipher(target_uid, key, iv):
    banner_text = ".\n.\n.\n[b][FF0000]—͞ᏚAMI求[FFFFFF] ⚡\n.\n.\n."
    fields = {1: 5, 2: {1: int(target_uid), 2: 1, 3: int(target_uid), 4: banner_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2:
        f = "0515000000"
    elif len(hl) == 3:
        f = "051500000"
    elif len(hl) == 4:
        f = "05150000"
    elif len(hl) == 5:
        f = "0515000"
    else:
        f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)


async def banecipher1(target_uid, key, iv):
    gay_text = ".\n.\n.\n[b][FF0000]—͞ᏚAMI求 ⚡[FFFFFF]\n.\n.\n."
    fields = {1: int(target_uid), 2: 5, 4: 50, 5: {1: int(target_uid), 2: gay_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2:
        f = "0515000000"
    elif len(hl) == 3:
        f = "051500000"
    elif len(hl) == 4:
        f = "05150000"
    elif len(hl) == 5:
        f = "0515000"
    else:
        f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)


async def convert_kyro_to_your_system(target_uid, chat_id, key, iv, nickname="SB", title_id=None):
    try:
        if title_id is None:
            available_titles = [905090075, 904990072, 904990069, 905190079, 904090014, 904090015,
                                904090024, 904090025, 904090026, 904090027, 904990070, 904990071]
            title_id = random.choice(available_titles)
        fields = {1: 1, 2: {1: int(target_uid), 2: int(chat_id),
            5: int(time.time()),
            8: f'{{"TitleID":{title_id},"type":"Title"}}',
            9: {1: f"[C][B][FF0000]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007,
                8: "SB TEAM", 10: 1, 11: 1, 13: {1: 2},
                14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}},
            10: "en", 13: {2: 2, 3: 1}, 14: {}}}
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Title error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# LOOPS
# ═══════════════════════════════════════════════════════════════

async def spm_loop(uid, key, iv, interval=0.5):
    while True:
        try:
            if online_writer is not None:
                packet = await SPamSqForSpm(uid, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', packet)
            else:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"spm_loop error for {uid}: {e}")
        await asyncio.sleep(interval)


async def ban_loop(key, iv, interval=0.5):
    global ban_running, ban_targets
    ban_running = True
    while ban_running:
        if online_writer is not None and ban_targets:
            for uid in list(ban_targets):
                try:
                    ban_pkt = await xBaNchaTxSkInZ(uid, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', ban_pkt)
                except Exception as e:
                    print(f"Ban error: {e}")
        await asyncio.sleep(interval)


async def evo_gun_cycle(uids, evo_ids_list, key, iv, region):
    global evo_cycle_running
    cc = 0
    while evo_cycle_running:
        cc += 1
        for emote_id in evo_ids_list:
            if not evo_cycle_running:
                break
            for uid_str in uids:
                try:
                    H = await Emote_k(int(uid_str), int(emote_id), key, iv, region)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                except Exception as e:
                    print(f"Emote error: {e}")
            if evo_cycle_running:
                for i in range(5):
                    if not evo_cycle_running:
                        break
                    await asyncio.sleep(1)
        if evo_cycle_running:
            await asyncio.sleep(2)


async def fast_emote_spam(uids, emote_id, key, iv, region):
    global fast_spam_running
    count = 0
    while fast_spam_running and count < 25:
        for uid in uids:
            try:
                H = await Emote_k(int(uid), int(emote_id), key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception:
                pass
        count += 1
        await asyncio.sleep(0.1)


async def custom_emote_spam(uid, emote_id, times, key, iv, region):
    global custom_spam_running
    count = 0
    while custom_spam_running and count < times:
        try:
            H = await Emote_k(int(uid), int(emote_id), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            count += 1
            await asyncio.sleep(0.1)
        except Exception:
            break


async def reject_spam_loop(target_uid, key, iv):
    global reject_spam_running
    count = 0
    while reject_spam_running and count < 150:
        try:
            p1 = await banecipher1(target_uid, key, iv)
            p2 = await banecipher(target_uid, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p1)
            await asyncio.sleep(0.1)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p2)
            count += 1
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"Reject error: {e}")
            break
    return count


async def msg_spam_loop(message_text, times, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    while msg_spam_running and count < times:
        try:
            colorful = await get_colorful_message(message_text, count + 1)
            msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
            if msg_packet and whisper_writer:
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                count += 1
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Msg error: {e}")
            break
    return count


async def xSEndMsgsQQ(Msg, id, K, V):
    fields = {1: id, 2: id, 4: Msg, 5: 1756580149, 7: 2, 8: 904990072,
        9: {1: "SB - C4", 2: get_random_avatar(), 4: 330, 5: 1001000001,
            8: "SB - C4", 10: 1, 11: 1, 13: {1: 2},
            14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}},
        10: "en", 13: {2: 2, 3: 1}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)


async def send_wave_messages(message_text, repeats, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    total_cycles = 0
    while msg_spam_running and total_cycles < repeats:
        try:
            for i in range(1, len(message_text) + 1):
                if not msg_spam_running:
                    break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            for i in range(len(message_text) - 1, 0, -1):
                if not msg_spam_running:
                    break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            total_cycles += 1
        except Exception as e:
            print(f"Wave error: {e}")
            break
    return count, total_cycles


async def freeze_emote_spam(uid, key, iv, region, chat_type, chat_id, sender_uid):
    global freeze_running
    FREEZE_EMOTES = [909052010, 909052010, 909052010]
    cycles = 0
    while freeze_running and cycles < 10:
        for emote_id in FREEZE_EMOTES:
            if not freeze_running:
                break
            try:
                emote_packet = await Emote_k(int(uid), emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', emote_packet)
                await asyncio.sleep(0.1)
            except Exception:
                pass
        cycles += 1
        await asyncio.sleep(1)
    return cycles


# ═══════════════════════════════════════════════════════════════
# API CALLS
# ═══════════════════════════════════════════════════════════════

async def send_friend_request(target_uid, token, region):
    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        ep = cipher.encrypt(pad(bytes.fromhex(payload), AES.block_size)).hex()
        url = "https://clientbp.ggpolarbear.com/RequestAddingFriend"
        headers = {"Authorization": f"Bearer {token}", "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1", "ReleaseVersion": "OB55",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=bytes.fromhex(ep), ssl=False) as r:
                return (True, "✅ ফ্রেন্ড রিকোয়েস্ট পাঠানো হয়েছে") if r.status == 200 else (False, f"❌ স্টেটাস: {r.status}")
    except Exception as e:
        return False, f"❌ ত্রুটি: {str(e)}"


async def remove_friend(target_uid, token, region):
    try:
        import RemoveFriend_Req_pb2
        msg = RemoveFriend_Req_pb2.RemoveFriend()
        msg.AuthorUid = int(admin_uid); msg.TargetUid = int(target_uid)
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        eb = cipher.encrypt(pad(msg.SerializeToString(), AES.block_size))
        url = "https://clientbp.ggpolarbear.com/RemoveFriend"
        headers = {'Authorization': f"Bearer {token}", 'User-Agent': "Dalvik/2.1.0 (Linux; Android 9)",
            'Content-Type': "application/x-www-form-urlencoded", 'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1", 'ReleaseVersion': "OB55"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=eb, headers=headers, ssl=False) as r:
                return (True, "✅ ফ্রেন্ড রিমুভ করা হয়েছে") if r.status == 200 else (False, f"❌ স্টেটাস: {r.status}")
    except Exception as e:
        return False, f"❌ ত্রুটি: {str(e)}"


async def check_banned(player_id):
    try:
        url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10)", "Accept": "application/json",
            "referer": "https://ff.garena.com/en/support/",
            "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as r:
                if r.status == 200:
                    return True, await r.json()
                return False, f"ব্যর্থ: {r.status}"
    except Exception as e:
        return False, f"ত্রুটি: {str(e)}"


async def get_player_info(player_id):
    try:
        url = f"https://nirob-x-info.vercel.app/info?uid={player_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as r:
                if r.status == 200:
                    return True, await r.json()
                return False, f"ব্যর্থ: {r.status}"
    except Exception as e:
        return False, f"ত্রুটি: {str(e)}"


def format_player_info(data):
    basic = data.get("basicInfo", {}); clan = data.get("clanBasicInfo", {})
    captain = data.get("captainBasicInfo", {}); pet = data.get("petInfo", {})
    social = data.get("socialInfo", {}); credit = data.get("creditScoreInfo", {})
    diamond = data.get("diamondCostRes", {})
    def x(v): return str(v) if v else "0"
    m1 = f"[b][c]{get_random_color()} 🎮 প্লেয়ার ইনফো\n[b][c][FFFFFF]নাম : {captain.get('nickname', basic.get('nickname', 'অজানা'))}\n[b][c][FFFFFF]ইউআইডি : {x(captain.get('accountId', basic.get('accountId', '0')))}\n[b][c][FFFFFF]লাইক : {x(captain.get('liked', basic.get('liked', '0')))}\n[b][c][FFFFFF]লেভেল : {captain.get('level', basic.get('level', '0'))}\n[b][c][FFFFFF]রিজিওন : {captain.get('region', basic.get('region', 'অজানা'))}"
    m2 = f"[b][c]{get_random_color()} 🏰 গিল্ড ইনফো\n[b][c][FFFFFF]গিল্ড : {clan.get('clanName', 'কোন গিল্ড নেই')}\n[b][c][FFFFFF]গিল্ড আইডি : {x(clan.get('clanId', '0'))}\n[b][c][FFFFFF]লিডার : {x(clan.get('captainId', 'অজানা'))}\n[b][c][FFFFFF]সদস্য : {clan.get('memberNum', '0')}/{clan.get('capacity', '0')}\n[b][c][FFFFFF]লেভেল : {clan.get('clanLevel', '0')}"
    m3 = f"[b][c]{get_random_color()} ℹ️ অতিরিক্ত তথ্য\n[b][c][FFFFFF]পেট : {pet.get('name', 'N/A')} (Lv {pet.get('level', 'N/A')})\n[b][c][FFFFFF]ক্রেডিট : {credit.get('creditScore', 'N/A')}\n[b][c][FFFFFF]ডায়মন্ড : {diamond.get('diamondCost', 'N/A')}\n[b][c][FFFFFF]বায়ো : {social.get('signature', 'N/A')}"
    return m1, m2, m3


def format_check_result(data):
    try:
        return f"[b][c]{get_random_color()} 🔍 ব্যান চেক\n[b][c][FFFFFF]ধরন: {data.get('ban_type', 'অজানা')}\n[b][c][FFFFFF]সময়কাল: {data.get('ban_duration', 'অজানা')}"
    except Exception as e:
        return f"[b][c]ত্রুটি: {str(e)}"


# ═══════════════════════════════════════════════════════════════
# /status helpers
# ═══════════════════════════════════════════════════════════════

async def createpacketinfo(uid, key, iv):
    try:
        ida = await EnC_Uid(uid, Tp='Uid')
        if len(ida) == 8:
            packet = f'080112080a04{ida}1005'
        elif len(ida) == 10:
            packet = f"080112090a05{ida}1005"
        else:
            packet = f"080112090A05{ida}1005"
        return await GeneRaTePk(packet, '0f15', key, iv)
    except Exception as e:
        print(f"createpacketinfo error: {e}")
        return None


def get_available_room(hex_packet):
    try:
        return json.dumps(PrOtO(hex_packet))
    except Exception as e:
        print(f"get_available_room error: {e}")
        return None


def get_player_status(packet):
    j = get_available_room(packet)
    if not j:
        return "OFFLINE"
    p = json.loads(j)
    try:
        data = p["5"]["data"]["1"]["data"]
        st   = data["3"]["data"]
        if st == 1:                return "SOLO"
        if st == 2:
            if "9" in data and "data" in data["9"]:
                gc = data["9"]["data"]
                mx = data["10"]["data"] + 1
                return f"INSQUAD ({gc}/{mx})"
            return "INSQUAD"
        if st in (3, 5):           return "INGAME"
        if st == 4:                return "IN ROOM"
        if st in (6, 7):           return "IN SOCIAL ISLAND MODE"
        return "NOTFOUND"
    except Exception:
        return "OFFLINE"


def get_idroom_by_idplayer(packet):
    try:
        p = json.loads(get_available_room(packet))
        return p["5"]["data"]["1"]["data"]["15"]["data"]
    except Exception:
        return None


def get_leader(packet):
    try:
        p = json.loads(get_available_room(packet))
        return p["5"]["data"]["1"]["data"]["8"]["data"]
    except Exception:
        return None


def save_to_cache(player_id, data):
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                cache = pickle.load(f)
        except Exception:
            cache = {}
    data["saved_at"] = time.time()
    cache[str(player_id)] = data
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)


def load_from_cache(player_id):
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "rb") as f:
            cache = pickle.load(f)
    except Exception:
        return None
    key = str(player_id)
    if key in cache:
        if time.time() - cache[key].get("saved_at", 0) > CACHE_TIMEOUT:
            del cache[key]
            with open(CACHE_FILE, "wb") as f:
                pickle.dump(cache, f)
            return None
        return cache[key]
    return None


def clear_cache_entry(player_id):
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                cache = pickle.load(f)
            cache.pop(str(player_id), None)
            with open(CACHE_FILE, "wb") as f:
                pickle.dump(cache, f)
        except Exception:
            pass


def debug_file_cache():
    if not os.path.exists(CACHE_FILE):
        print("Cache: file does not exist")
        return
    try:
        with open(CACHE_FILE, "rb") as f:
            cache = pickle.load(f)
        print(f"Cache: {len(cache)} entries")
        for k, v in cache.items():
            age = time.time() - v.get("saved_at", 0)
            print(f"  {k}: {v.get('status','?')} (age {age:.1f}s)")
    except Exception as e:
        print(f"Cache debug error: {e}")


# ═══════════════════════════════════════════════════════════════
# /mimic helpers
# ═══════════════════════════════════════════════════════════════

async def extract_emote_info(data_hex, key, iv):
    try:
        packet_json = json.loads(await DeCode_PackEt(data_hex[10:]))
    except Exception:
        return None
    for extractor in (extract_type_21, extract_type_26,
                      extract_type_5, generic_extract):
        info = extractor(packet_json)
        if info and info.get("sender_uid"):
            return info
    return None


def extract_type_21(packet_json):
    if packet_json.get("1") == 21:
        try:
            nested = packet_json["2"]["data"]["5"]["data"]
            sender = nested.get("1", {}).get("data")
            emote  = nested.get("3", {}).get("data")
            if sender and emote:
                return {"sender_uid": sender, "emote_id": emote,
                        "packet_type": 21, "confidence": "high"}
        except Exception:
            pass
    return None


def extract_type_26(packet_json):
    if packet_json.get("1") == 26:
        try:
            data   = packet_json["2"]["data"]
            sender = data.get("1", {}).get("data")
            emote  = data.get("2", {}).get("data")
            if sender and emote:
                return {"sender_uid": sender, "emote_id": emote,
                        "packet_type": 26, "confidence": "high"}
        except Exception:
            pass
    return None


def extract_type_5(packet_json):
    if packet_json.get("1") == 5:
        try:
            data   = packet_json["2"]["data"]
            sender = data.get("1", {}).get("data")
            emote  = data.get("4", {}).get("data") or 909051015
            if sender:
                return {"sender_uid": sender, "emote_id": emote,
                        "packet_type": 5, "confidence": "medium"}
        except Exception:
            pass
    return None


def generic_extract(packet_json):
    uid, emote_id = None, None
    def search(obj):
        nonlocal uid, emote_id
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "data" and isinstance(v, (int, str)) and str(v).isdigit():
                    num = int(v)
                    if 1_000_000 < num < 99_999_999_999 and not uid:
                        uid = num
                    elif str(v).startswith("909") and len(str(v)) >= 9:
                        emote_id = num
                elif isinstance(v, dict):
                    search(v)
                elif isinstance(v, list):
                    for item in v:
                        search(item)
    search(packet_json)
    if uid:
        return {"sender_uid": uid,
                "emote_id":   emote_id or 909051015,
                "packet_type": "generic", "confidence": "medium"}
    return None


# ═══════════════════════════════════════════════════════════════
# /hi — equip HI emote (admin only)
# ═══════════════════════════════════════════════════════════════

async def CHINKOR_equip_Hi_emote(sender_uid, chat_id, chat_type, key, iv, region_default="IND"):
    def fmt_num(n): return str(n)
    def first_n(s, n=15):
        if not s: return "None"
        s = str(s)
        return s[:n] + ("..." if len(s) > n else "")

    if str(sender_uid) != admin_uid:
        await safe_send_message(chat_type, f"[B][C][FF0000]❌ This command is only for the bot owner (UID {fmt_num(admin_uid)}).", sender_uid, chat_id, key, iv)
        return

    if not BOT_UID_FOR_HI or not BOT_PW_FOR_HI:
        await safe_send_message(chat_type, "[B][C][FF0000]❌ Bot credentials not loaded from main.py.", sender_uid, chat_id, key, iv)
        return

    await safe_send_message(chat_type, f"[B][C][FFFF00]🔐 STEP {fmt_num(1)}: Loading credentials\n[FFFFFF]📁 UID      : [FFFF00]{fmt_num(first_n(BOT_UID_FOR_HI, 5))}...\n[FFFFFF]🔑 Password : [FFFF00]{first_n(BOT_PW_FOR_HI, 5)}...", sender_uid, chat_id, key, iv)
    await asyncio.sleep(0.5)

    try:
        import login_engine
        result = await login_engine.do_login(BOT_UID_FOR_HI, BOT_PW_FOR_HI, region_default)
    except Exception as e:
        await safe_send_message(chat_type, f"[B][C][FF0000]❌ Login error: {str(e)[:100]}", sender_uid, chat_id, key, iv)
        return

    if not result:
        await safe_send_message(chat_type, "[B][C][FF0000]❌ Login failed (MajorLogin / GetLoginData rejected).", sender_uid, chat_id, key, iv)
        return

    jwt_token = result["token"]
    region    = result.get("region", region_default) or region_default

    await safe_send_message(chat_type, f"[B][C][00FF00]✅ STEP {fmt_num(2)}: Login success\n[FFFFFF]🌍 Region : [FFFF00]{region}\n[FFFFFF]🔑 JWT    : [FFFF00]{first_n(jwt_token, 15)}...", sender_uid, chat_id, key, iv)
    await asyncio.sleep(0.5)

    region_server_map = {
        "BD":  "https://clientbp.ggpolarbear.com",
        "IND": "https://client.ind.freefiremobile.com",
        "PK":  "https://clientbp.ggpolarbear.com",
        "ME":  "https://clientbp.ggpolarbear.com",
        "VN":  "https://clientbp.ggpolarbear.com",
        "SG":  "https://clientbp.ggpolarbear.com",
        "ID":  "https://clientbp.ggpolarbear.com",
        "TH":  "https://clientbp.ggpolarbear.com",
        "BR":  "https://client.us.freefiremobile.com",
        "NA":  "https://client.us.freefiremobile.com",
        "US":  "https://client.us.freefiremobile.com",
        "RU":  "https://clientbp.ggpolarbear.com",
    }
    server_url = region_server_map.get(region.upper())
    if not server_url:
        await safe_send_message(chat_type, f"[B][C][FF0000]❌ Region '{region}' not supported.", sender_uid, chat_id, key, iv)
        return

    await safe_send_message(chat_type, f"[B][C][FFFF00]📡 STEP {fmt_num(3)}: Sending ChooseEmote\n[FFFFFF]🌐 URL  : [FFFF00]{server_url}/ChooseEmote\n[FFFFFF]🎭 Emote: [FFFF00]HI (ID: {fmt_num('909000001')})", sender_uid, chat_id, key, iv)
    await asyncio.sleep(1.5)

    emote_data = bytes.fromhex("CAF683222A25C7BEFEB51F59544DB313")
    headers = {
        "Accept-Encoding": "gzip",
        "Connection":      "Keep-Alive",
        "Content-Type":    "application/x-www-form-urlencoded",
        "Expect":          "100-continue",
        "ReleaseVersion":  "OB55",
        "User-Agent":      "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
        "X-GA":            "v1 1",
        "X-Unity-Version": "2018.4.11f1",
        "Authorization":   f"Bearer {jwt_token}",
    }
    url = f"{server_url}/ChooseEmote"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=emote_data, ssl=False, timeout=10) as resp:
                status_code   = resp.status
                response_body = await resp.read()
                response_text = response_body.decode("utf-8", errors="replace")
    except Exception as e:
        await safe_send_message(chat_type, f"[B][C][FF0000]❌ Request failed: {str(e)[:100]}", sender_uid, chat_id, key, iv)
        return

    bot_nick = result.get("account_name", "Bot")

    if status_code == 200:
        result_msg = (f"[B][C][00FF00]✅ STEP {fmt_num(4)}: EMOTE EQUIPPED!\n[FFFFFF]────────────────────────────\n[FFFF00]👤 Nickname : [00FF00]{bot_nick}\n[FFFF00]🆔 UID      : [00FF00]{fmt_num(result['bot_uid'])}\n[FFFF00]🎭 Emote    : [00FF00]HI\n[FFFF00]🌍 Region   : [00FF00]{region}\n[FFFF00]📊 HTTP     : [00FF00]{fmt_num(status_code)}\n[FFFFFF]────────────────────────────")
    elif b"BR_INVENTORY_NOT_ENOUGH_ITEMS" in response_body:
        result_msg = (f"[B][C][FFFF00]⚠️ EMOTE NOT IN VAULT!\n[FFFFFF]────────────────────────────\n[FFFF00]👤 Bot     : [00FF00]{bot_nick}\n[FFFF00]🆔 UID     : [00FF00]{fmt_num(result['bot_uid'])}\n[FFFF00]📊 HTTP    : {fmt_num(status_code)}\n[FFFF00]📄 Response: [FF0000]Emote not owned – buy it first.\n[FFFFFF]────────────────────────────")
    else:
        short_response = response_text[:200] + ("..." if len(response_text) > 200 else "")
        result_msg = (f"[B][C][FF0000]❌ FAILED!\n[FFFFFF]────────────────────────────\n[FFFF00]📊 HTTP : {fmt_num(status_code)}\n[FFFF00]📄 Body :\n[FF0000]{short_response}\n[FFFFFF]────────────────────────────")

    await safe_send_message(chat_type, result_msg, sender_uid, chat_id, key, iv)


# ═══════════════════════════════════════════════════════════════
# /check — ban status
# ═══════════════════════════════════════════════════════════════

async def check_ban_auto(uid):
    name, region_code = "N/A", "N/A"
    try:
        ok, data = await get_player_info(uid)
        if ok:
            b = data.get("basicInfo", {}) or {}
            name = b.get("nickname", "N/A")
            region_code = b.get("region", "N/A")
    except Exception:
        pass

    is_banned, period = 0, 0
    try:
        ok, bd = await check_banned(uid)
        if ok:
            is_banned = bd.get("data", {}).get("is_banned", 0)
            period    = bd.get("data", {}).get("period", 0)
    except Exception:
        pass

    status_text  = "BANNED"     if is_banned else "NOT BANNED"
    status_color = "FF0000"     if is_banned else "00FF00"
    if is_banned:
        period_text  = f"{period} days" if period else "Permanent"
        period_color = "FF4444"
    else:
        period_text, period_color = "N/A", "00FF00"

    return (f"[C][B][5DA9FF]━━━━━━━━━━━━━\n[C][B][FF6EC7]BAN STATUS CHECK\n[C][5DA9FF]━━━━━━━━━━━━━\n[C][E6E6FA]Name    : [9AD0FF]{name}\n[C][E6E6FA]UID     : [9AD0FF]{xMsGFixinG(uid)}\n[C][E6E6FA]Region  : [9AD0FF]{region_code}\n[C][E6E6FA]Status  : [{status_color}]{status_text}\n[C][E6E6FA]Period  : [{period_color}]{period_text}\n[C][B][5DA9FF]━━━━━━━━━━━━━")


# ═══════════════════════════════════════════════════════════════
# TCP ONLINE HANDLER
# ═══════════════════════════════════════════════════════════════

async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer, whisper_writer, region, pending_ghost_future, ghost_team_id, ghost_squad_code, emote_hijack, bot_uid
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            token_bytes = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            writer.write(token_bytes); await writer.drain()
            print(f"✅ ONLINE connected to {ip}:{port}")
            while True:
                data = await reader.read(9999)
                if not data:
                    break
                hex_data = data.hex()

                if hex_data.startswith("0f00") and len(hex_data) > 100:
                    try:
                        print("📡 Received status response packet")
                        proto_part = f'08{hex_data.split("08", 1)[1]}'
                        parsed = get_available_room(proto_part)
                        if parsed:
                            pj = json.loads(parsed)
                            if "2" in pj and pj["2"]["data"] == 15:
                                player_id     = pj["5"]["data"]["1"]["data"]["1"]["data"]
                                player_status = get_player_status(proto_part)
                                entry = {
                                    "status":       player_status,
                                    "packet":       proto_part,
                                    "timestamp":    time.time(),
                                    "full_packet":  hex_data,
                                    "parsed_json":  pj,
                                }
                                d1 = pj["5"]["data"]["1"]["data"]
                                if (d1.get("3", {}).get("data") == 1 and
                                        d1.get("11", {}).get("data") == 1):
                                    entry["special_state"] = "SOLO_WITH_FLAG_1"
                                if "IN ROOM" in player_status:
                                    rid = get_idroom_by_idplayer(proto_part)
                                    if rid:
                                        entry["room_id"] = rid
                                elif "INSQUAD" in player_status:
                                    lid = get_leader(proto_part)
                                    if lid:
                                        entry["leader_id"] = lid
                                save_to_cache(player_id, entry)
                                print(f"✅ Cached status: {player_id} = {player_status}")
                    except Exception as e:
                        print(f"❌ status parse error: {e}")
                    continue

                if hex_data.startswith('05') and len(hex_data) > 20 and emote_hijack:
                    try:
                        import re
                        payload = hex_data[10:]
                        packet_str = await DeCode_PackEt(payload)
                        if not packet_str or '9090' not in packet_str:
                            try:
                                decrypted = await DEc_PacKeT(payload, key, iv)
                                packet_str = await DeCode_PackEt(decrypted)
                            except:
                                pass
                        
                        if packet_str and '9090' in packet_str:
                            emote_match = re.search(r'"data":\s*(9090\d{5})', packet_str)
                            if emote_match:
                                emote_id = emote_match.group(1)
                                all_ids = re.findall(r'"data":\s*(\d{8,12})', packet_str)
                                sender_uid = None
                                for u in all_ids:
                                    if str(u) != str(bot_uid) and not str(u).startswith('9090'):
                                        sender_uid = u
                                        break
                                
                                if emote_id and sender_uid and str(sender_uid) != str(bot_uid):
                                    bot_self_emote = await Emote_k(int(bot_uid), int(emote_id), key, iv, region)
                                    if online_writer:
                                        online_writer.write(bot_self_emote)
                                        await online_writer.drain()
                                    print(f"\n🎯 MIMIC SUCCESS!\n   👤 From: {sender_uid}\n   🎭 Emote: {emote_id}")
                    except Exception as e:
                        print(f"❌ Mimic error: {e}")

                if not hex_data.startswith("0500"):
                    continue
                try:
                    packet_json = json.loads(await DeCode_PackEt(hex_data[10:]))
                except Exception:
                    continue

                try:
                    if ('5' in packet_json and 'data' in packet_json['5'] and
                        '1' in packet_json['5']['data'] and '8' in packet_json['5']['data']):
                        owner = packet_json['5']['data']['1']['data']
                        code = packet_json['5']['data']['8']['data']
                        print(f"📩 স্কোয়াড ইনভাইট from {owner}")
                        join_pkt = await ᏚAMIAccepted(owner, code, key, iv, region)
                        if join_pkt and online_writer:
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_pkt)
                except Exception:
                    pass

                try:
                    uid_g, chat_code, squad_code = await GeTSQDaTa(packet_json)
                    if uid_g is not None:
                        INV_JOIN = await AutH_Chat(3, uid_g, chat_code, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', INV_JOIN)
                        asyncio.create_task(send_welcome(uid_g, key, iv))
                        
                        # ⭐ DEVIL Banner on Join ⭐
                        try:
                            p1 = await DEVIL1(uid_g, key, iv)
                            p2 = await DEVIL(uid_g, key, iv)
                            if p1 and online_writer: online_writer.write(p1); await online_writer.drain(); await asyncio.sleep(0.2)
                            if p2 and online_writer: online_writer.write(p2); await online_writer.drain()
                        except Exception: pass
                except Exception:
                    pass

                try:
                    if pending_ghost_future and not pending_ghost_future.done():
                        f5 = packet_json.get('5', {}).get('data', {})
                        if '31' in f5:
                            ghost_squad_code = f5['31'].get('data')
                        if '1' in f5:
                            ghost_team_id = f5['1'].get('data')
                        if ghost_team_id and ghost_squad_code:
                            pending_ghost_future.set_result(True)
                except Exception:
                    pass

                try:
                    if packet_json.get('4', {}).get('data') == 8:
                        f5 = packet_json.get('5', {}).get('data', {})
                        if f5.get('2', {}).get('data') == 5:
                            chat_code = f5.get('17', {}).get('data')
                            if chat_code is not None:
                                WELCOMED.pop(chat_code, None)
                                LeAvE = await leave_channel_req(chat_code, 3, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', LeAvE)
                                print("🚪 কিক হয়েছে! চ্যানেল ছেড়ে গেছে")
                except Exception:
                    pass

            writer.close(); await writer.wait_closed(); online_writer = None
        except Exception as e:
            print(f"Online error: {ip}:{port} - {e}")
            online_writer = None
        await asyncio.sleep(reconnect_delay)


# ═══════════════════════════════════════════════════════════════
# TCP CHAT HANDLER
# ═══════════════════════════════════════════════════════════════

async def TcPChaT(ip, port, AutHToKen, key, iv, ready_event, region, clan_id=None, clan_data=None, reconnect_delay=0.5):
    global whisper_writer, online_writer, spm_tasks, ToKen, bot_uid, bot_enabled, emote_hijack
    global spam_targets, evo_cycle_running, evo_cycle_task, ban_task, ban_running, ban_targets
    global fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task
    global msg_spam_running, msg_spam_task, mg_spam_task, reject_spam_running, reject_spam_task, freeze_running, freeze_task
    global _clan_message_task, _clan_msg_key, _clan_msg_iv, _clan_msg_bot_uid, _clan_msg_clan_id

    print(f"📡 {region} → TCP CHAT connecting...")
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            whisper_writer.write(bytes_payload); await whisper_writer.drain()
            ready_event.set()
            print(f"✅ CHAT connected to {ip}:{port}")

            if clan_id and clan_data:
                try:
                    pK = await AuthClan(clan_id, clan_data, key, iv)
                    whisper_writer.write(pK)
                    await whisper_writer.drain()
                    print(f"✅ AuthClan sent for clan {clan_id}")
                except Exception as e:
                    print(f"❌ AuthClan failed: {e}")
            else:
                print(f"⚠️ No clan_id/clan_data — clan chat unavailable")

            # ⭐ CLAN Auto Message Task ⭐
            if clan_id and clan_id > 0:
                if _clan_message_task is None or _clan_message_task.done():
                    _clan_msg_key = key
                    _clan_msg_iv = iv
                    _clan_msg_bot_uid = int(bot_uid)
                    _clan_msg_clan_id = int(clan_id)
                    _clan_message_task = asyncio.create_task(clan_message_loop())
                    print(f"[CLAN] Auto-message task started for clan {_clan_msg_clan_id}")

            for tgt in spam_targets:
                if tgt not in spm_tasks or spm_tasks[tgt].done():
                    spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))

            while True:
                data = await reader.read(9999)
                if not data: break
                if not data.hex().startswith("120000"): continue
                try:
                    response = await DecodeWhisperMessage(data.hex()[10:])
                    uid = response.Data.uid
                    chat_id = response.Data.Chat_ID
                    XX = response.Data.chat_type
                    inPuTMsG = response.Data.msg.lower()
                    msg_raw = response.Data.msg
                except Exception:
                    continue

                # ═══════════════════════════════════════════════════════════════
                # ⭐ STICKER & TITLE DETECTION + AUTO REPLY ⭐
                # ═══════════════════════════════════════════════════════════════
                try:
                    msg_str = await DeCode_PackEt(data.hex()[10:])
                    chatdata = json.loads(msg_str) if msg_str else {}
                    
                    if "5" in chatdata and "data" in chatdata["5"]:
                        inner = chatdata["5"]["data"]
                        
                        if "8" in inner and "data" in inner["8"]:
                            raw_data = inner["8"]["data"]
                            try:
                                data_json = json.loads(raw_data)
                                packet_type = data_json.get("type")
                                
                                # ১. স্টিকার ডিটেকশন
                                if packet_type == "Sticker":
                                    target_uid = inner["1"]["data"]
                                    if str(target_uid) != str(bot_uid) and NUMBER_EMOTES:
                                        random_emote_key = random.choice(list(NUMBER_EMOTES.keys()))
                                        emote_id = NUMBER_EMOTES[random_emote_key]
                                        emote_packet = await Emote_k(int(target_uid), int(emote_id), key, iv, region)
                                        if emote_packet and online_writer:
                                            online_writer.write(emote_packet)
                                            await online_writer.drain()
                                            print(f"🎭 Sticker Reply: Emote {emote_id} sent to {target_uid}")
                                        sticker_reply = "[B][C][FFFF00] CHINKOR STYLE TCP"
                                        await safe_send_message(XX, sticker_reply, target_uid, chat_id, key, iv)

                                # ২. টাইটেল কপি ডিটেকশন
                                elif packet_type == "Title":
                                    sender_uid = inner["1"]["data"]
                                    title_id = data_json.get("TitleID")
                                    
                                    if str(sender_uid) != str(bot_uid):
                                        try:
                                            nickname = response.Data.Details.Nickname
                                        except Exception:
                                            nickname = "Player"

                                        # মালিকের জন্য আলাদা মেসেজ
                                        if str(sender_uid) == str(admin_uid):
                                            reply_msg = f"[B][C][00FF00]স্বাগতম আমার মালিক {nickname} ভাই! [FFFF00]আপনার টাইটেলটি অসাধারণ। [00FFFF]আমি এটি এখনই কপি করে দিচ্ছি।"
                                        else:
                                            reply_msg = f"[B][C][00FF00]এই {nickname} বোকাচো🖕দা টাইটেল দেখাশ কেন?[FFFF00]এসব কি আমাদের নাই নাকি? [00FFFF]টাইটেল তো আমাদের আইডির নিচে পড়ে থাকে !! [FFD700] এই দেখ lol... বোকা চন্দ্র !! ☆"

                                        await safe_send_message(XX, reply_msg, sender_uid, chat_id, key, iv)
                                        await asyncio.sleep(0.5)

                                        # টাইটেল কপি করা
                                        title_packet = await convert_kyro_to_your_system(
                                            target_uid=sender_uid,
                                            chat_id=chat_id,
                                            key=key,
                                            iv=iv,
                                            nickname="<I'm_back>",
                                            title_id=title_id
                                        )
                                        if title_packet and whisper_writer:
                                            whisper_writer.write(title_packet)
                                            await whisper_writer.drain()
                                            print(f"✅ Title {title_id} copied from {sender_uid}")

                                        # ইমোট পাঠানো
                                        if NUMBER_EMOTES:
                                            random_key = random.choice(list(NUMBER_EMOTES.keys()))
                                            emote_id = NUMBER_EMOTES[random_key]
                                            emote_pkt = await Emote_k(int(sender_uid), int(emote_id), key, iv, region)
                                            if emote_pkt and online_writer:
                                                online_writer.write(emote_pkt)
                                                await online_writer.drain()
                                                print(f"🎭 Title Reply: Emote {emote_id} sent to {sender_uid}")
                            except Exception as inner_e:
                                pass
                except Exception as outer_e:
                    pass

                if not bot_enabled and not inPuTMsG.strip().startswith('/on'):
                    if inPuTMsG.strip() != '/on':
                        continue

                # ⭐ /menu ⭐
                if inPuTMsG.strip().startswith('/menu'):
                    parts = inPuTMsG.strip().split()
                    page = 1
                    if len(parts) >= 2:
                        try: page = int(parts[1])
                        except Exception: page = 1
                    try:
                        menu_text = get_menu_page(page, per_page=5)
                        await safe_send_message(XX, menu_text, uid, chat_id, key, iv)
                        print(f"📋 /menu page {page} sent")
                    except Exception as e:
                        print(f"/menu error: {e}")
                        await safe_send_message(XX, f"[B][C][FF0000]❌ Menu error: {str(e)[:60]}", uid, chat_id, key, iv)
                # ═══════════════════════════════════════════════
                # HELP
                # ═══════════════════════════════════════════════
                if inPuTMsG.strip() in ("/help", "help", "bot help", "/ᏚAMI"):
                    h1_color = get_random_color()
                    h2_color = get_random_color()
                    h3_color = get_random_color()
                    h4_color = get_random_color()

                    h1 = f"""[B][C]{h1_color}╭━━━〔 SAMI BOT 〕━━━╮
[C][B][FFFFFF]┃ ➤ /join <code> [00FFFF]» Join Squad
[C][B][FFFFFF]┃ ➤ /exit [00FFFF]» Leave Squad
[C][B][FFFFFF]┃ ➤ /spm <uid> [00FFFF]» Send Requests
[C][B][FFFFFF]┃ ➤ /stp <uid> [00FFFF]» Stop Requests
[C][B][FFFFFF]┃ ➤ /s1 [00FFFF]» spam craftland
[C][B][FFFFFF]┃ ➤ /s2 [00FFFF]» spam v1
[C][B][FFFFFF]┃ ➤ /s3 [00FFFF]» spam v2
[C][B][FFFFFF]┃ ➤ /s4 [00FFFF]» spam moderator
[C][B][FFFFFF]┃ ➤ /s5 [00FFFF]» spam sp
[C][B][FFFFFF]┃ ➤ GET BAN [00FFFF]» UPDATE MAJORLOGIN OR NEED MAJORLOGIN JOIN OUR TELEGRAM GROUP 
[C][B][FFFFFF]┃ ➤ IMPORTANT NOTICE [00FFFF]» THERER ARE NO HIDDEN COMMAND OK
[B][C]{h1_color}╰━━━━━━━━━━━━━━━━━━━━╯"""

                    h2 = f"""[B][C]{h2_color}╭━━━〔 GAME COMMANDS 〕━━━╮
[C][B][FFFFFF]┃ ➤ /e <uid> <emote> [00FFFF]» Send Emote
[C][B][FFFFFF]┃ ➤ /e <name> [00FFFF]» Named Emote
[C][B][FFFFFF]┃ ➤ /evo <uid> <1-21> [00FFFF]» Evo Emote
[C][B][FFFFFF]┃ ➤ /evos [00FFFF]» Evo Cycle
[C][B][FFFFFF]┃ ➤ /sevos [00FFFF]» Stop Cycle
[C][B][FFFFFF]┃ ➤ /sticker [00FFFF]» Random Sticker
[C][B][FFFFFF]┃ ➤ /b <1-13> [00FFFF]» Send Bundle
[C][B][FFFFFF]┃ ➤ /animation <1-12> [00FFFF]» Animation
[C][B][FFFFFF]┃ ➤ /magic <code> [00FFFF]» Magic Bundle
[B][C]{h2_color}╰━━━━━━━━━━━━━━━━━━━━━━━━╯"""

                    h3 = f"""[B][C]{h3_color}╭━━━〔 FUN COMMANDS 〕━━━╮
[C][B][FFFFFF]┃ ➤ /love <name> [00FFFF]» Love Messages
[C][B][FFFFFF]┃ ➤ /gali <name> [00FFFF]» Gaali Messages
[C][B][FFFFFF]┃ ➤ /rt <name> [00FFFF]» Roast
[C][B][FFFFFF]┃ ➤ /praisa <name> [00FFFF]» Praise
[C][B][FFFFFF]┃ ➤ /later <name> [00FFFF]» Love Letter
[C][B][FFFFFF]┃ ➤ /sadlater <name> [00FFFF]» Sad Letter
[C][B][FFFFFF]┃ ➤ /joke [00FFFF]» Hindi Joke
[C][B][FFFFFF]┃ ➤ /luck <name> [00FFFF]» Fortune
[C][B][FFFFFF]┃ ➤ /quiz [00FFFF]» Quiz Game
[B][C]{h3_color}╰━━━━━━━━━━━━━━━━━━━━╯"""

                    h4 = f"""[B][C]{h4_color}╭━━━━〔 SAMI PREMIUM 〕━━━━╮
[C][B][FFFFFF]┃ TCP BOT       [00FFFF]» @DM টাকা
[C][B][FFFFFF]┃ GLORY BOT    [00FFFF]» @DM টাকা
[C][B][FFFFFF]┃ LEVEL UP BOT [00FFFF]» @DM টাকা
[C][B][FFFFFF]┃ LIKE BOT     [00FFFF]» @DM টাকা
[B][C]{h4_color}╰━━━━━━━━━━━━━━━━━━━━━━━━╯

[B][C]{h4_color}╭━━━━━━〔 CONTACT 〕━━━━━━╮
[C][B][FFFFFF]┃ Telegram: @samiislambd
[B][C]{h4_color}╰━━━━━━━━━━━━━━━━━━━━━━━━╯"""

                    for m in (h1, h2, h3, h4):
                        try:
                            P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                            if P: await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(HELP_DELAY)
                        except Exception: pass

                elif inPuTMsG.strip() == "/admin":
                    msg = f"""[b][c]{get_random_color()} ═══ —͞ᏚAMI求 BOT ═══

[b][c][FFFFFF]🎯 উপলব্ধ বট:
[b][c][FFFFFF]✅ Tomb Bots
[b][c][FFFFFF]✅ Glory Bots
[b][c][FFFFFF]✅ Friend Bots
[b][c][FFFFFF]✅ Clan Bots
[b][c][FFFFFF]✅ TCP Online Bots

[b][c][FFFFFF]💎 ডেভেলপার: —͞ᏚAMI求
[b][c][FFFFFF]✈️ টেলিগ্রাম: @samiislambd
[b][c][FFFFFF]🔗 লিংক: https://t.me/your link

[b][c]{get_random_color()} কেনার জন্য যোগাযোগ করুন!"""
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/on':
                    if str(uid) != admin_uid:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ শুধু অ্যাডমিন /on ব্যবহার করতে পারে", uid, chat_id, key, iv)
                    else:
                        bot_enabled = True
                        await safe_send_message(XX, f"[B][C][FFFFFF]✅ বট এখন চালু", uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/off':
                    if str(uid) != admin_uid:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ শুধু অ্যাডমিন /off ব্যবহার করতে পারে", uid, chat_id, key, iv)
                    else:
                        bot_enabled = False
                        await safe_send_message(XX, f"[B][C][FF0000]⛔ বট এখন বন্ধ", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/s1'): await handle_badge_command('s1', inPuTMsG, uid, chat_id, key, iv, region, XX)
                elif inPuTMsG.strip().startswith('/s2'): await handle_badge_command('s2', inPuTMsG, uid, chat_id, key, iv, region, XX)
                elif inPuTMsG.strip().startswith('/s3'): await handle_badge_command('s3', inPuTMsG, uid, chat_id, key, iv, region, XX)
                elif inPuTMsG.strip().startswith('/s4'): await handle_badge_command('s4', inPuTMsG, uid, chat_id, key, iv, region, XX)
                elif inPuTMsG.strip().startswith('/s5'): await handle_badge_command('s5', inPuTMsG, uid, chat_id, key, iv, region, XX)

                elif inPuTMsG.startswith('/join '):
                    try:
                        code = inPuTMsG.split('/join ')[1].strip()
                        EM = await JoinSq_original(code, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\n✅ স্কোয়াডে জয়েন হয়েছে: {code}", uid, chat_id, key, iv)
                    except Exception as e:
                        print(f"Join error: {e}")

                elif inPuTMsG.startswith('/exit') or inPuTMsG.startswith('/leave'):
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(uid, key, iv))
                    await safe_send_message(XX, f"[B][C]{get_random_color()}\n✅ স্কোয়াড ছেড়ে দেওয়া হয়েছে", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/spm '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        tgt = parts[1]
                        if tgt in spm_tasks: spm_tasks[tgt].cancel()
                        spam_targets.add(tgt)
                        save_spam_targets()
                        spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))
                        await safe_send_message(XX, f"[B][C][FFFFFF]✅ {tgt} এর জন্য স্প্যাম শুরু", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /spm <uid>", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/stp '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1] in spm_tasks:
                        spm_tasks[parts[1]].cancel()
                        del spm_tasks[parts[1]]
                        if parts[1] in spam_targets:
                            spam_targets.remove(parts[1])
                            save_spam_targets()
                        await safe_send_message(XX, f"[B][C][FFFFFF]✅ স্প্যাম বন্ধ", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ কোন সক্রিয় স্প্যাম নেই", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/gh '):
                    parts = inPuTMsG.split(' ', 2)
                    if len(parts) >= 3 and bot_uid is not None:
                        teamcode = parts[1].strip()
                        name = parts[2].strip()
                        try:
                            pending_ghost_future = asyncio.Future()
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await JoinSq_original(teamcode, key, iv))
                            try:
                                await asyncio.wait_for(pending_ghost_future, timeout=8.0)
                            except asyncio.TimeoutError:
                                await safe_send_message(XX, f"[B][C][FF0000]❌ কোন সাড়া নেই", uid, chat_id, key, iv)
                                pending_ghost_future = None
                                continue
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                            await asyncio.sleep(0.2)
                            for _ in range(4):
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await GhostPakcet(ghost_team_id, name, ghost_squad_code, key, iv))
                                await asyncio.sleep(0.1)
                            await safe_send_message(XX, f"[B][C][FFFFFF]✅ {name} হিসেবে ঘোস্ট জয়েন হয়েছে", uid, chat_id, key, iv)
                            pending_ghost_future = None
                        except Exception as e:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ {e}", uid, chat_id, key, iv)
                            pending_ghost_future = None

                elif inPuTMsG.startswith('/msg '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) < 3:
                        await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /msg <text> <times>", uid, chat_id, key, iv)
                    else:
                        try:
                            times = int(parts[-1])
                            message = ' '.join(parts[1:-1])
                            if msg_spam_task and not msg_spam_task.done():
                                msg_spam_running = False
                                msg_spam_task.cancel()
                                await asyncio.sleep(0.1)
                            msg_spam_running = True
                            msg_spam_task = asyncio.create_task(msg_spam_loop(message, times, chat_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C][FFFFFF]✅ {times}x পাঠানো হচ্ছে: {message}", uid, chat_id, key, iv)
                        except ValueError:
                            await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /msg <text> <times>", uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/stop msg':
                    if msg_spam_task and not msg_spam_task.done():
                        msg_spam_running = False
                        msg_spam_task.cancel()
                        await safe_send_message(XX, f"[B][C][FFFFFF]✅ মেসেজ স্প্যাম বন্ধ", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/mg '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) < 2:
                        await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /mg <text> [repeats]", uid, chat_id, key, iv)
                    else:
                        try:
                            message = parts[1]
                            repeats = int(parts[2]) if len(parts) > 2 else 5
                            if repeats > 10: repeats = 10
                            if mg_spam_task and not mg_spam_task.done():
                                msg_spam_running = False
                                mg_spam_task.cancel()
                                await asyncio.sleep(0.1)
                            msg_spam_running = True
                            mg_spam_task = asyncio.create_task(send_wave_messages(message, repeats, chat_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C][FFFFFF]✅ ওয়েভ শুরু: {message} x{repeats}", uid, chat_id, key, iv)
                        except ValueError:
                            await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /mg <text> [repeats]", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/ban '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        if ban_task and not ban_task.done():
                            ban_running = False
                            ban_task.cancel()
                            ban_targets.clear()
                            await asyncio.sleep(0.3)
                        ban_targets.add(parts[1])
                        ban_task = asyncio.create_task(ban_loop(key, iv))
                        await safe_send_message(XX, f"[B][C][FFFFFF]✅ {parts[1]} এ ব্যান শুরু", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /ban <uid>", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/reject '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        if reject_spam_task and not reject_spam_task.done():
                            reject_spam_running = False
                            reject_spam_task.cancel()
                            await asyncio.sleep(0.3)
                        await safe_send_message(XX, f"[B][C][FFFFFF]🌀 {parts[1]} এ রিজেক্ট স্প্যাম শুরু", uid, chat_id, key, iv)
                        reject_spam_running = True
                        reject_spam_task = asyncio.create_task(reject_spam_loop(parts[1], key, iv))
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /reject <uid>", uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/reject_stop':
                    if reject_spam_task and not reject_spam_task.done():
                        reject_spam_running = False
                        reject_spam_task.cancel()
                        await safe_send_message(XX, f"[B][C][FFFFFF]✅ রিজেক্ট স্প্যাম বন্ধ", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/evos'):
                    parts = inPuTMsG.strip().split()
                    uids = [str(uid)]
                    for p in parts[1:]:
                        if p.isdigit() and len(p) >= 7:
                            uids.append(p)
                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False
                        evo_cycle_task.cancel()
                        await asyncio.sleep(0.3)
                    evo_cycle_running = True
                    evo_cycle_task = asyncio.create_task(evo_gun_cycle(uids, EVO_IDS, key, iv, region))
                    await safe_send_message(XX, f"[B][C][FFFFFF]✅ ইভো সাইকেল শুরু", uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/sevos':
                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False
                        evo_cycle_task.cancel()
                        await safe_send_message(XX, f"[B][C][FFFFFF]✅ ইভো সাইকেল বন্ধ", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/fast '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 3:
                        uids = []
                        emote_id = None
                        for p in parts[1:]:
                            if p.isdigit():
                                if len(p) > 3: uids.append(p)
                                else: emote_id = p
                        if uids and emote_id:
                            if fast_spam_task and not fast_spam_task.done():
                                fast_spam_running = False
                                fast_spam_task.cancel()
                            fast_spam_running = True
                            fast_spam_task = asyncio.create_task(fast_emote_spam(uids, emote_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C][FFFFFF]✅ দ্রুত স্প্যাম শুরু", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/p '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 4:
                        try:
                            tgt = parts[1]
                            emote_id = parts[2]
                            times = int(parts[3])
                            if times > 100: times = 100
                            if custom_spam_task and not custom_spam_task.done():
                                custom_spam_running = False
                                custom_spam_task.cancel()
                                await asyncio.sleep(0.2)
                            custom_spam_running = True
                            custom_spam_task = asyncio.create_task(custom_emote_spam(tgt, emote_id, times, key, iv, region))
                            await safe_send_message(XX, f"[B][C][FFFFFF]✅ কাস্টম স্প্যাম শুরু: {emote_id} x{times}", uid, chat_id, key, iv)
                        except ValueError:
                            await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /p <uid> <emote> <times>", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/e '):
                    parts = inPuTMsG.strip().split()
                    try:
                        if len(parts) < 2:
                            await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /e <name> or /e <uid> <name>", uid, chat_id, key, iv)
                            continue
                        last = parts[-1].lower()
                        is_num = last.isdigit() and last in NUMBER_EMOTES
                        is_name = last in NAME_EMOTES or last in NAME_TO_EMOTE_ID
                        if not (is_num or is_name):
                            await safe_send_message(XX, f"[B][C][FF0000]❌ ইমোট '{last}' পাওয়া যায়নি", uid, chat_id, key, iv)
                            continue
                        tgt_uids = [int(uid)] if len(parts) == 2 else [int(p) for p in parts[1:-1] if p.isdigit()]
                        emote_id = NUMBER_EMOTES.get(last) if is_num else (NAME_EMOTES.get(last) or NAME_TO_EMOTE_ID.get(last))
                        sc = 0
                        for t in tgt_uids:
                            try:
                                H = await Emote_k(t, int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                sc += 1
                                await asyncio.sleep(0.1)
                            except Exception: pass
                        if sc > 0:
                            await safe_send_message(XX, f"[B][C][FFFFFF]✅ {sc} জনকে ইমোট পাঠানো হয়েছে", uid, chat_id, key, iv)
                    except Exception as e:
                        print(f"E cmd error: {e}")

                elif inPuTMsG.startswith('/evo ') and not inPuTMsG.startswith('/evos'):
                    parts = inPuTMsG.strip().split()
                    try:
                        num = None
                        uids_l = []
                        for p in parts[1:]:
                            if p.isdigit():
                                if len(p) <= 2 and num is None: num = p
                                else: uids_l.append(p)
                        if not num or not uids_l:
                            await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /evo <uid> <1-21>", uid, chat_id, key, iv)
                            continue
                        num_i = int(num)
                        if num_i not in EMOTE_MAP:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ নাম্বার ১-২১ হতে হবে", uid, chat_id, key, iv)
                            continue
                        emote_id = EMOTE_MAP[num_i]
                        for t in uids_l:
                            try:
                                H = await Emote_k(int(t), int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                await asyncio.sleep(0.1)
                            except Exception: pass
                        await safe_send_message(XX, f"[B][C][FFFFFF]✅ ইভো ইমোট {num_i} পাঠানো হয়েছে", uid, chat_id, key, iv)
                    except Exception as e:
                        print(f"Evo error: {e}")

                elif inPuTMsG.strip().startswith('/title') or inPuTMsG.strip().startswith('/alltitles'):
                    titles_list = [905090075, 904990072, 904990069, 905190079, 904090014, 904090015, 904090024, 904090025, 904090026, 904090027, 904990070, 904990071]
                    await safe_send_message(XX, f"[B][C][FFFFFF]🎖️ {len(titles_list)} টি টাইটেল পাঠানো হচ্ছে...", uid, chat_id, key, iv)
                    for tid in titles_list:
                        try:
                            pkt = await convert_kyro_to_your_system(int(uid), chat_id, key, iv, nickname="SB", title_id=tid)
                            if pkt and whisper_writer:
                                whisper_writer.write(pkt)
                                await whisper_writer.drain()
                            await asyncio.sleep(2)
                        except Exception as e:
                            print(f"Title error: {e}")
                    await safe_send_message(XX, f"[B][C][FFFFFF]✅ সব টাইটেল পাঠানো হয়েছে!", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/animation'):
                    parts = inPuTMsG.strip().split()
                    anim_ids = {"1": 914000002, "2": 914000003, "3": 914038001, "4": 914039001, "5": 914042001, "6": 914044001, "7": 914047001, "8": 914047002, "9": 914048001, "10": 914050001, "11": 914051001, "12": 914053001}
                    if len(parts) < 2:
                        lst = "1-rampage\n2-cannibal\n3-devil\n4-scorpio\n5-frostfire\n6-paradox\n7-naruto\n8-aurora\n9-midnight\n10-itachi\n11-dreamspace\n12-eclipse"
                        await safe_send_message(XX, f"[B][C][FFFFFF]অ্যানিমেশন:\n{lst}", uid, chat_id, key, iv)
                    elif parts[1] in anim_ids:
                        try:
                            pkt = await animation_packet(anim_ids[parts[1]], key, iv)
                            if pkt and online_writer:
                                online_writer.write(pkt); await online_writer.drain()
                            await safe_send_message(XX, f"[B][C][FFFFFF]✅ অ্যানিমেশন {parts[1]} পাঠানো হয়েছে!", uid, chat_id, key, iv)
                        except Exception as e:
                            print(f"Anim error: {e}")
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ অ্যানিমেশন পাওয়া যায়নি", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/b '):
                    parts = inPuTMsG.strip().split()
                    bundle_ids = {"1": 914000002, "2": 914000003, "3": 914038001, "4": 914039001, "5": 914042001, "6": 914044001, "7": 914047001, "8": 914047002, "9": 914048001, "10": 914050001, "11": 914051001, "12": 914053001, "13": 914055001}
                    if len(parts) < 2:
                        await safe_send_message(XX, f"[B][C][FFFFFF]ব্যবহার: /b <1-12>", uid, chat_id, key, iv)
                    elif parts[1] in bundle_ids:
                        bid = bundle_ids[parts[1]]
                        try:
                            anim_pkt = await animation_packet(bid, key, iv)
                            if anim_pkt and online_writer:
                                online_writer.write(anim_pkt); await online_writer.drain()
                            await asyncio.sleep(3)
                            b_pkt = await Look_Changer(bid, key, iv, look_type=1, region=region)
                            if b_pkt and online_writer:
                                online_writer.write(b_pkt); await online_writer.drain()
                            await safe_send_message(XX, f"[B][C][FFFFFF]✅ বান্ডেল {parts[1]} পাঠানো হয়েছে!", uid, chat_id, key, iv)
                        except Exception as e:
                            print(f"Bundle error: {e}")
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ বান্ডেল পাওয়া যায়নি", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/sticker'):
                    try:
                        pkt = await send_sticker_packet(uid, chat_id, key, iv)
                        if pkt and whisper_writer:
                            whisper_writer.write(pkt); await whisper_writer.drain()
                    except Exception as e:
                        print(f"Sticker error: {e}")

                elif inPuTMsG.strip().startswith('/love '):
                    try:
                        name = inPuTMsG.strip()[6:].strip()
                        msgs = [f"[B][C][FF0000]❤️ {name} তুমি আমার জান! ❤️", f"[B][C][FF0000]💕 {name} তোমাকে ছাড়া কিছু নেই! 💕", f"[B][C][FFFFFF]💖 {name} তুমিই আমার সব! 💖", f"[B][C][FF0000]💗 {name} তুমি আমার দুনিয়া! 💗", f"[B][C][FF0000]💘 {name} আমি তোমাকে অনেক ভালোবাসি! 💘"]
                        for m in msgs:
                            P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(1.5)
                    except Exception as e:
                        print(f"Love error: {e}")

                elif inPuTMsG.strip().startswith('/gali '):
                    try:
                        name = inPuTMsG.strip()[6:].strip()
                        blocked = ["rafin", "rafin txt", "rafin.txt"]
                        if name.lower() in blocked:
                            await safe_send_message(XX, f"[B][C][FF0000]⚠️ বট মালিককে টার্গেট করা যাবে না!", uid, chat_id, key, iv)
                            continue
                        msgs = [f"[B][C][FF0000]{name} খানকির বাচ্চা! 🤬", f"[B][C][FF0000]{name} নোংরা নালার কীট! 🐛", f"[B][C][FF0000]{name} ভোসড়ির! 💢", f"[B][C][FF0000]{name} মাদারচোদ! 😡", f"[B][C][FF0000]{name} হারামী! 💀"]
                        for m in msgs:
                            P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(1.5)
                    except Exception as e:
                        print(f"Gali error: {e}")

                elif inPuTMsG.strip().startswith('/rt '):
                    try:
                        name = inPuTMsG.strip()[4:].strip()
                        msgs = [f"[B][C][FF0000]😆 {name} তো বট, বট! 🤖", f"[B][C][FF0000]🎮 {name} তো ট্রেনিং গ্রাউন্ডের পুতুল! 🗿", f"[B][C][FF0000]😂 {name} তো ফ্রি ফায়ারের সবচেয়ে বড় নুব! 🎯"]
                        for m in msgs:
                            P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(1.5)
                    except Exception as e:
                        print(f"RT error: {e}")

                elif inPuTMsG.strip().startswith('/praisa '):
                    try:
                        name = inPuTMsG.strip()[8:].strip()
                        msgs = [f"[B][C][FFFFFF]🌟 {name} তুমি অসাধারণ মানুষ! 🌟", f"[B][C][FFFFFF]🔥 {name} তোমার পরিশ্রম একদিন রঙ দেবে! 🔥", f"[B][C][FFFFFF]💎 {name} তুমি ইউনিক! 💎"]
                        for m in msgs:
                            P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(0.8)
                    except Exception as e:
                        print(f"Praisa error: {e}")

                elif inPuTMsG.strip().startswith('/later '):
                    try:
                        name = inPuTMsG.strip()[7:].strip()
                        msg = f"[B][C][FF0000]💌 প্রিয় {name} 💌\n\nতোমার স্মৃতিতে দিন কেটে যায়,\nতোমাকে ছাড়া মন কাঁদে।\n\n💕 তোমার চিরকাল 💕"
                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except Exception as e:
                        print(f"Later error: {e}")

                elif inPuTMsG.strip().startswith('/sadlater '):
                    try:
                        name = inPuTMsG.strip()[10:].strip()
                        msg = f"[B][C][FFFFFF]💔 {name} 💔\n\nভাঙা মনের আওয়াজ শোনো,\nপ্রতি রাতে তোমার স্মৃতি আসে।\n\n💔 একা 💔"
                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except Exception as e:
                        print(f"Sad error: {e}")

                elif inPuTMsG.strip() == '/joke':
                    jokes = ["শিক্ষক: হোমওয়ার্ক কেন করনি?\nছাত্র: স্যার, কারেন্ট চলে গিয়েছিল।\nশিক্ষক: দিনে কেন করনি?\nছাত্র: দিনে তো ঘুম আসে।\n🤣", "স্ত্রী: জানু, আমাকে একটা কথা বলো।\nস্বামী: হ্যাঁ বলো।\nস্ত্রী: আমি সুন্দরী নাকি তোমার মা?\nস্বামী: দুজনেই অনেক সুন্দরী।\n😂"]
                    P = await SEndMsG(XX, f"[B][C][FFFFFF]😂 জোকস 😂\n\n{random.choice(jokes)}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/dare':
                    P = await SEndMsG(XX, f"[B][C][FFFFFF]🎲 ডেয়ার 🎲\n\n{random.choice(['🔥 ৫ মিনিট চোখ বন্ধ করে রাখো!', '😂 পরের ১০ মিনিট শুধু হাসতে থাকো!', '🐔 মুরগির মতো ডাকো!'])}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/truth':
                    P = await SEndMsG(XX, f"[B][C][FFFFFF]🤔 ট্রুথ 🤔\n\n{random.choice(['💕 তুমি কাকে সবচেয়ে বেশি ভালোবাসো?', '🤫 তোমার সবচেয়ে বড় সিক্রেট কী?', '💔 তোমার ক্রাশ কে?'])}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/wyr':
                    a, b = random.choice([("অদৃশ্য হওয়ার শক্তি", "উড়ার শক্তি"), ("সুপারম্যান হওয়া", "ব্যাটম্যান হওয়া")])
                    P = await SEndMsG(XX, f"[B][C][FFFFFF]🤔 তুমি কোনটা চাও?\n\nA) {a}\n\nB) {b}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/quiz':
                    q, a = random.choice([("বাংলাদেশের রাজধানী?", "ঢাকা"), ("১ কিলোমিটার = কত মিটার?", "১০০০")])
                    P = await SEndMsG(XX, f"[B][C][FFFFFF]🧠 কুইজ 🧠\n\n❓ {q}\n\n✅ উত্তর: {a}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/roll':
                    d1, d2 = random.randint(1, 6), random.randint(1, 6)
                    faces = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
                    P = await SEndMsG(XX, f"[B][C][FFFFFF]🎲 ডাইস 🎲\n\n🎯 ডাইস ১: {faces[d1]} {d1}\n🎯 ডাইস ২: {faces[d2]} {d2}\n\n📊 মোট: {d1+d2}/12", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() in ('/zodiac', '/rashi'):
                    signs = {"মেষ ♈": ("লাল", "৯", "মঙ্গলবার"), "বৃষ ♉": ("সবুজ", "৬", "শুক্রবার")}
                    s, d = random.choice(list(signs.items()))
                    P = await SEndMsG(XX, f"[B][C][FFFFFF]🌟 রাশিফল 🌟\n\n🔮 রাশি: {s}\n🎨 রঙ: {d[0]}\n🔢 নাম্বার: {d[1]}\n📅 দিন: {d[2]}\n\n📜 {random.choice(['আজ তোমার দিন দুর্দান্ত যাবে!', 'ভালোবাসায় আজ সুখবর আসতে পারে!'])}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() in ('/weather', '/abohawa'):
                    city = random.choice(["ঢাকা", "চট্টগ্রাম", "খুলনা", "রাজশাহী"])
                    P = await SEndMsG(XX, f"[B][C][FFFFFF]🌤️ আবহাওয়া 🌤️\n\n📍 শহর: {city}\n🌡️ তাপমাত্রা: {random.randint(20, 40)}°C\n☁️ আবহাওয়া: {random.choice(['☀️ রোদ', '🌤️ আংশিক মেঘ', '🌧️ বৃষ্টি'])}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/luck '):
                    name = inPuTMsG.strip()[6:].strip().title()
                    P = await SEndMsG(XX, f"[B][C][FFFFFF]🔮 ভাগ্য 🔮\n\n👤 নাম: {name}\n\n{random.choice([f'🌟 {name} তুমি শীঘ্রই বড় সাফল্য পাবে!', f'💰 {name} তোমার জীবনে অনেক টাকা আসবে!'])}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/info '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        await safe_send_message(XX, f"[B][C][FFFFFF]🔍 {parts[1]} এর তথ্য আনা হচ্ছে...", uid, chat_id, key, iv)
                        try:
                            ok, data = await get_player_info(parts[1])
                            if ok:
                                m1, m2, m3 = format_player_info(data)
                                for m in (m1, m2, m3):
                                    P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    await asyncio.sleep(0.5)
                            else:
                                await safe_send_message(XX, f"[B][C][FF0000]❌ {data}", uid, chat_id, key, iv)
                        except Exception as e:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ ত্রুটি: {e}", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /info <uid>", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/check '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            reply = await check_ban_auto(parts[1])
                        except Exception as e:
                            reply = f"[B][C][FF0000]❌ ত্রুটি: {e}"
                        P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                        if P: await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]ব্যবহার: /check <uid>", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/status'):
                    parts = inPuTMsG.strip().split()
                    if len(parts) < 2 or not parts[1].isdigit():
                        await safe_send_message(XX, "[B][C][FF0000]❌ Usage:  /status <player_uid>\nExample:  /status 123456789", uid, chat_id, key, iv)
                    else:
                        target_uid = parts[1]
                        debug_file_cache()
                        clear_cache_entry(target_uid)
                        await safe_send_message(XX, f"[B][C][FFFF00]🔍 Checking status of {fix_num(target_uid)}...", uid, chat_id, key, iv)
                        try:
                            status_packet = await createpacketinfo(target_uid, key, iv)
                            if not status_packet:
                                await safe_send_message(XX, "[B][C][FF0000]❌ Failed to create status packet!\n", uid, chat_id, key, iv)
                            else:
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', status_packet)
                                response_received = False
                                for attempt in range(12):
                                    cache_data = load_from_cache(target_uid)
                                    if cache_data:
                                        response_received = True
                                        status_msg = f"[B][C][FFFF00]📊 PLAYER STATUS\n────────────────\n👤 UID: {fix_num(target_uid)}\n📊 Status: {cache_data['status']}\n"
                                        if "IN ROOM" in cache_data['status'] and 'room_id' in cache_data:
                                            status_msg += f"🏠 Room ID: {fix_num(cache_data['room_id'])}\n"
                                        elif "INSQUAD" in cache_data['status'] and 'leader_id' in cache_data:
                                            status_msg += f"👑 Leader: {fix_num(cache_data['leader_id'])}\n"
                                        elif "OFFLINE" in cache_data['status']: status_msg += f"🔴 Player is offline\n"
                                        elif "INGAME" in cache_data['status']: status_msg += f"🎮 Player is in a match\n"
                                        elif "SOLO" in cache_data['status']: status_msg += f"👤 Player is solo\n"
                                        status_msg += f"────────────────\n✅ Real-time data\n"
                                        await safe_send_message(XX, status_msg, uid, chat_id, key, iv)
                                        break
                                    await asyncio.sleep(0.5)
                                if not response_received:
                                    error_msg = f"[B][C][FF0000]❌ STATUS CHECK FAILED\n👤 UID: {fix_num(target_uid)}\n📛 No response from server\n"
                                    await safe_send_message(XX, error_msg, uid, chat_id, key, iv)
                        except Exception as e:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ Error: {str(e)[:50]}\n", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/ai '):
                    question = inPuTMsG.strip()[4:].strip()
                    if question:
                        await safe_send_message(XX, f"[B][C][FFFFFF]🤖 এআই ভাবছে...", uid, chat_id, key, iv)
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(f"https://9x-ai.vercel.app/ask?key=SUMON9X&message={question}", timeout=aiohttp.ClientTimeout(total=15)) as r:
                                    if r.status == 200:
                                        answer = (await r.text()).strip()
                                        msg = f"[B][C][FFFFFF]🤖 এআই উত্তর:\n\n[FFFFFF]{answer}"
                                    else: msg = f"[B][C][FF0000]❌ এআই ত্রুটি: {r.status}"
                        except Exception as e: msg = f"[B][C][FF0000]❌ ত্রুটি: {e}"
                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/mth'):
                    parts = inPuTMsG.strip().split(maxsplit=1)
                    if len(parts) < 2:
                        await safe_send_message(XX, f"[B][C][FFFFFF]ব্যবহার: /mth 2+2", uid, chat_id, key, iv)
                    else:
                        expr = parts[1].strip().replace("×", "*").replace("÷", "/").replace("x", "*")
                        try:
                            import re as _re
                            if not _re.match(r'^[\d\s\+\-\*\/\.\(\)\%]+$', expr): raise ValueError("Invalid")
                            result = eval(expr)
                            if isinstance(result, float) and result == int(result): result = int(result)
                            P = await SEndMsG(XX, f"[B][C][FFFFFF]🧮 ক্যালকুলেটর\n\nএক্সপ্রেশন: {expr}\nফলাফল: {result}", uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        except Exception:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ ভুল এক্সপ্রেশন", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith("/add ") and str(uid) == admin_uid:
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, msg = await send_friend_request(parts[1], ToKen, region)
                            reply = f"[B][C]{get_random_color()} {msg}"
                        except Exception as e: reply = f"[B][C][FF0000]ত্রুটি: {e}"
                    else: reply = f"[B][C][FF0000]ব্যবহার: /add <uid>"
                    P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith("/remove ") and str(uid) == admin_uid:
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, msg = await remove_friend(parts[1], ToKen, region)
                            reply = f"[B][C]{get_random_color()} {msg}"
                        except Exception as e: reply = f"[B][C][FF0000]ত্রুটি: {e}"
                    else: reply = f"[B][C][FF0000]ব্যবহার: /remove <uid>"
                    P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/hi': await CHINKOR_equip_Hi_emote(uid, chat_id, XX, key, iv, region)
                elif inPuTMsG.strip() == '/mimic_on': emote_hijack = True; await safe_send_message(XX, "[B][C][FF0000]The Mimic Is Now On", uid, chat_id, key, iv)
                elif inPuTMsG.strip() == '/mimic_off': emote_hijack = False; await safe_send_message(XX, "[B][C][FF0000]The Mimic Is Now OFF", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/ice '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2:
                        tgt = parts[1] if parts[1].lower() not in ('me', 'self') else str(uid)
                        if freeze_task and not freeze_task.done(): freeze_running = False; freeze_task.cancel(); await asyncio.sleep(0.3)
                        freeze_running = True
                        freeze_task = asyncio.create_task(freeze_emote_spam(tgt, key, iv, region, XX, chat_id, uid))
                        await safe_send_message(XX, f"[B][C][FFFFFF]❄️ {tgt} এ ফ্রিজ শুরু", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/room '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 3:
                        tgt, rid = parts[1], parts[2]
                        try:
                            for i in range(3000):
                                spam_p = await Room_Spam(tgt, rid, "SB", key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', spam_p)
                                if (i + 1) % 50 == 0: print(f"রুম স্প্যাম অগ্রগতি: {i+1}/3000")
                                await asyncio.sleep(0.05)
                            await safe_send_message(XX, f"[B][C][FFFFFF]✅ রুম স্প্যাম সম্পন্ন", uid, chat_id, key, iv)
                        except Exception as e:
                            print(f"Room spam error: {e}")

                elif inPuTMsG.strip().isdigit() or (inPuTMsG.strip().count('*') == 1 and all(p.isdigit() for p in inPuTMsG.strip().split('*'))):
                    number_part = inPuTMsG.strip()
                    emote_id = None
                    times = 1
                    if '*' in number_part:
                        parts = number_part.split('*')
                        number = parts[0]
                        times = min(int(parts[1]), 100)
                    else:
                        number = number_part
                    if number in NUMBER_EMOTES:
                        emote_id = NUMBER_EMOTES[number]
                    elif number.isdigit() and 900_000_000 <= int(number) <= 999_999_999:
                        emote_id = int(number)
                    if emote_id:
                        try:
                            await safe_send_message(XX, "[B][C][FAFAFA] ওই কি👽রে.. ওই কিরে... ম👽ধু ম👽ধু রস👽মালাই", uid, chat_id, key, iv)
                            for _ in range(times):
                                H = await Emote_k(int(uid), int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                await asyncio.sleep(0.05)
                            print(f"✅ Number emote: {number} → {emote_id} x{times}")
                        except Exception as e:
                            print(f"Number emote error: {e}")

                elif inPuTMsG.strip().lower() in NAME_TO_EMOTE_ID:
                    try:
                        emote_id = NAME_TO_EMOTE_ID[inPuTMsG.strip().lower()]
                        H = await Emote_k(int(uid), int(emote_id), key, iv, region)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                        print(f"✅ Name emote: {inPuTMsG.strip()} → {emote_id}")
                    except Exception as e:
                        print(f"Name emote error: {e}")

                else:
                    if inPuTMsG.strip().startswith('/') and len(inPuTMsG.strip()) > 2:
                        pass

            writer.close(); await writer.wait_closed(); whisper_writer = None
        except Exception as e:
            print(f"Chat error: {ip}:{port} - {e}")
            whisper_writer = None
        await asyncio.sleep(reconnect_delay)


# ═══════════════════════════════════════════════════════════════
# OLD (ᏚAMI YT_LAST_FILE) squad/group packets - /5 group invite
# Ei function gulo old file theke ana; notun version gulo *_new naam e ache
# ═══════════════════════════════════════════════════════════════

async def OpEnSq(K , V,region):
    fields = {1: 1, 2: {2: "\u0001", 3: 1, 4: 1, 5: "en", 9: 1, 11: 1, 13: 1, 14: {2: 5756, 6: 11, 8: "1.111.5", 9: 2, 10: 4}}}
    if region.lower() == "ind":
        packet = '0514'
    elif region.lower() == "bd":
        packet = "0519"
    else:
        packet = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , packet , K , V)

async def cHSq(Nu , Uid , K , V,region):
    fields = {1: 17, 2: {1: int(Uid), 2: 1, 3: int(Nu - 1), 4: 62, 5: "\u001a", 8: 5, 13: 329}}
    if region.lower() == "ind":
        packet = '0514'
    elif region.lower() == "bd":
        packet = "0519"
    else:
        packet = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , packet , K , V)

async def SEnd_InV(Nu , Uid , K , V,region):
    
    fields = {1: 2 , 2: {1: int(Uid) , 2: region , 4: int(Nu)}}

    if region.lower() == "ind":
        packet = '0514'
    elif region.lower() == "bd":
        packet = "0519"
    else:
        packet = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , packet , K , V)

async def GenJoinSquadsPacket(code,  K , V):
    fields = {}
    fields[1] = 4
    fields[2] = {}
    fields[2][4] = bytes.fromhex("01090a0b121920")
    fields[2][5] = str(code)
    fields[2][6] = 6
    fields[2][8] = 1
    fields[2][9] = {}
    fields[2][9][2] = 800
    fields[2][9][6] = 11
    fields[2][9][8] = "1.111.1"
    fields[2][9][9] = 5
    fields[2][9][10] = 1
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '0515' , K , V)


# ═══════════════════════════════════════════════════════════════
# OLD (ᏚAMI YT_LAST_FILE) xSEndMsg - guild/private chat message (delay fix)
# Notun version: xSEndMsg_new
# ═══════════════════════════════════════════════════════════════
async def xSEndMsg(Msg , Tp , Tp2 , id , K , V):
    feilds = {1: id , 2: Tp2 , 3: Tp, 4: Msg, 5: 1735129800, 7: 2, 9: {1: "[FFFFFF]ᏚAMI YT", 2: int(await xBunnEr()), 3: 901048020, 4: 330, 5: 1001000001, 8: "xBesTo - C4", 10: 1, 11: 1, 13: {1: 2}, 14: {1: 12484827014, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}, 12: 0}, 10: "en", 13: {3: 1}}    
    Pk = (await CrEaTe_ProTo(feilds)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)


# ═══════════════════════════════════════════════════════════════
# OLD (ᏚAMI YT_LAST_FILE) xSEndMsgsQ - squad chat message (welcome fix)
# Notun version: xSEndMsgsQ_new
# ═══════════════════════════════════════════════════════════════
async def xSEndMsgsQ(Msg, id, K, V, region="BD"):
    """Fixed version - exactly like small bot"""
    
    avatar = await xBunnEr()
    
    fields = {
        1: id, 
        2: id, 
        4: Msg, 
        5: 1756580149, 
        8: 904990072, 
        9: {
            1: "[FFFFFF]ᏚAMI YT",  # আপনার bot name
            2: avatar, 
            3: 2,                 # ⭐ CRITICAL
            4: 329, 
            5: 1001000001, 
            6: 66,
            7: 66,                # ⭐ CRITICAL
            8: "xBe4!sTo - C4", 
            9: 66,
            10: 66, 
            11: 66, 
            12: 66,
            13: {1: 68, 2:67}, 
            14: {
                1: 1158053040, 
                2: 8, 
                3: b"\x10\x15\x08\x0A\x0B\x15\x0C\x0F\x11\x04\x07\x02\x03\x0D\x0E\x12\x01\x05\x06"
            }
        }, 
        10: "en", 
        13: {66: 66, 66: 66},
        14: {                    # ⭐ CRITICAL - এই field টা যোগ করুন
            11: {
                1: 3,
                2: 7,
                3: 170,
                4: 999,
                5: 1,
                6: region,
                7: 2,
                8: 2,
                9: 2
            }
        }
    }
    
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)