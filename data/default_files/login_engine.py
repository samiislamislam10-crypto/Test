#════════════════════════════

import asyncio
import random
import uuid
import time
import json
import sys
from datetime import datetime

import httpx
from google_play_scraper import app as play_scraper
from protobuf_decoder.protobuf_decoder import Parser
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from Pb2 import MajoRLoGinrEs_pb2, PorTs_pb2


# ═══════════════════════════════════════════════════════════════
#              ★ প্রিমিয়াম কনসোল ডিজাইন ইউটিল (—͞ᏚAMI求 YT) ★
# ═══════════════════════════════════════════════════════════════

def _c(text, color):
    """সহজ রঙিন টেক্সট হেল্পার"""
    colors = {
        "cyan":    "\033[1;36m",
        "green":   "\033[1;32m",
        "yellow":  "\033[1;33m",
        "red":     "\033[1;31m",
        "magenta": "\033[1;35m",
        "white":   "\033[1;37m",
        "gray":    "\033[1;90m",
        "reset":   "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def log(level, msg):
    """টাইমস্ট্যাম্প ও আইকনসহ প্রিমিয়াম লগ"""
    icons = {
        "INFO":  ("cyan",    "ℹ"),
        "OK":    ("green",   "✔"),
        "WAIT":  ("yellow",  "⏳"),
        "WARN":  ("yellow",  "⚠"),
        "ERROR": ("red",     "✘"),
        "BOT":   ("magenta", "★"),
        "NET":   ("cyan",    "⇄"),
    }
    color, icon = icons.get(level, ("white", "•"))
    ts = time.strftime("%H:%M:%S")
    print(f"{_c(f'[{ts}]', 'gray')} {_c(f'{icon} {level:<5}', color)} │ {msg}")


def print_banner():
    """লগইন ইঞ্জিনের প্রিমিয়াম ব্যানার"""
    print("\n" + "═" * 68)
    print(_c("      ★  S A M I - Y T  —  P R E M I U M   L O G I N  ★", "magenta"))
    print(_c("             Free Fire OB55 Guest Login Engine", "cyan"))
    print("═" * 68 + "\n")


def print_box(title, pairs):
    """সুন্দর বক্সে কী-ভ্যালু দেখাবে"""
    width = 60
    print(_c(f"┌{'─' * width}┐", "magenta"))
    print(_c("│", "magenta") + _c(f" {title.center(width - 2)} ", "yellow") + _c("│", "magenta"))
    print(_c(f"├{'─' * width}┤", "magenta"))
    for k, v in pairs:
        line = f"  {_c(f'{k:<16}', 'cyan')}: {_c(str(v), 'green')}"
        pad_len = width - 4 - len(k) - len(str(v))
        print(_c("│", "magenta") + f" {line}{' ' * max(pad_len, 0)}" + _c("│", "magenta"))
    print(_c(f"└{'─' * width}┘", "magenta") + "\n")


# ═══════════════════════════════════════════════════════════════
#              ★ কনস্ট্যান্ট (—͞ᏚAMI求 YT এডিশন) ★
# ═══════════════════════════════════════════════════════════════

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV  = b'6oyZDr22E3ychjM%'

REGION_LANG = {
    "BD": "bn", "IND": "hi", "PK": "ur", "SG": "en", "ID": "id",
    "ME": "ar", "VN": "vi", "TW": "zh", "CIS": "ru", "TH": "th",
    "EU": "en", "US": "en", "SAC": "es", "LK": "en", "BR": "pt",
}

DEFAULT_HEADERS = {
    'User-Agent': 'UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Expect': '100-continue',
    'X-Unity-Version': '2018.4.12f1',
    'X-GA-SV': '1789535859',
    'X-GA': 'v1 1',
    'ReleaseVersion': 'OB55',
}


# ═══════════════════════════════════════════════════════════════
#              ★ Protobuf হেল্পার ফাংশন ★
# ═══════════════════════════════════════════════════════════════

def _pb_varint(n):
    if n < 0:
        n = (1 << 64) + n
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        out.append(b)
        if not n:
            break
    return bytes(out)


def _pb_tag(f, w):
    return _pb_varint((f << 3) | w)


def _pb_field(f, v):
    if isinstance(v, bool):
        v = int(v)
    if isinstance(v, int):
        return _pb_tag(f, 0) + _pb_varint(v)
    if isinstance(v, str):
        d = v.encode('utf-8')
        return _pb_tag(f, 2) + _pb_varint(len(d)) + d
    if isinstance(v, (bytes, bytearray)):
        d = bytes(v)
        return _pb_tag(f, 2) + _pb_varint(len(d)) + d
    return b""


# ═══════════════════════════════════════════════════════════════
#              ★ AES + Protobuf পার্স হেল্পার ★
# ═══════════════════════════════════════════════════════════════

async def aes_encrypt(payload, key, iv):
    """AES-CBC দিয়ে পেলোড এনক্রিপ্ট করবে"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(payload, AES.block_size))


def get_proto_field(d, key, default=None):
    """পার্সড ডিকশনারি থেকে ফিল্ড বের করবে"""
    if not d or not isinstance(d, dict):
        return default
    if key in d:
        return d[key].get('data', default)
    if str(key) in d:
        return d[str(key)].get('data', default)
    return default


async def parse_results(parsed_results):
    """protobuf-decoder এর ফলাফলকে ডিকশনারিতে রূপান্তর"""
    result_dict = {}
    for result in parsed_results:
        field_data = {"wire_type": result.wire_type}
        if result.wire_type in ("varint", "string", "bytes"):
            field_data["data"] = result.data
        elif result.wire_type == "length_delimited":
            if hasattr(result.data, "results"):
                field_data["data"] = await parse_results(result.data.results)
            elif isinstance(result.data, list):
                field_data["data"] = await parse_results(result.data)
            else:
                field_data["data"] = str(result.data)
        result_dict[str(result.field)] = field_data
    return result_dict


# ═══════════════════════════════════════════════════════════════
#              ★ ভার্সন কনফিগ ও অ্যাক্সেস টোকেন ★
# ═══════════════════════════════════════════════════════════════

async def get_playstore_version():
    """Google Play Store থেকে Free Fire এর সর্বশেষ ভার্সন বের করবে"""
    loop = asyncio.get_event_loop()
    try:
        res = await loop.run_in_executor(
            None,
            lambda: play_scraper('com.dts.freefireth', lang='hi', country='id'),
        )
        return res.get("version", "1.132.8")
    except Exception:
        return "1.132.8"


async def version_config(client_http, region="IND"):
    """গেমের লেটেস্ট ভার্সন কনফিগারেশন আনবে"""
    app_version = await get_playstore_version()
    lang = REGION_LANG.get(region, "hi")
    api_url = (
        f"https://version.ggwhitehawk.com/live/ver.php?version={app_version}"
        f"&lang={lang}&device=android&channel=android&appstore=googleplay"
        f"&region={region}&whitelist_version=1.3.0&whitelist_sp_version=1.0.0"
    )
    try:
        res = await client_http.get(api_url)
        data = res.json()
        return (
            data.get("latest_release_version"),
            data.get("remote_version"),
            data.get("server_url"),
        )
    except Exception:
        return None


async def get_access_token(client_http, uid, password):
    """গেস্ট অ্যাকাউন্টের জন্য অ্যাক্সেস টোকেন আনবে"""
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    hdrs = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B Build/SP1A.210812.016)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    data = {
        "uid": str(uid),
        "password": str(password),
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    for attempt in range(3):
        try:
            r = await client_http.post(url, headers=hdrs, data=data)
            if r.status_code == 200:
                rd = r.json()
                return rd.get("open_id"), rd.get("access_token"), rd.get("platform", 4)
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return None


# ═══════════════════════════════════════════════════════════════
#              ★ MajorLogin পেলোড তৈরি ★
# ═══════════════════════════════════════════════════════════════

async def build_majorlogin_payload_new(open_id, access_token, platform, client_version):
    """MajorLogin protobuf পেলোড তৈরি করবে"""
    try:
        from Pb2 import MajoRLoGinrEq_pb2 as ML
        proto = ML.MajorLogin()
        proto.event_time = str(datetime.now())[:-7]
        proto.game_name = "free fire"
        proto.platform_id = 1
        proto.client_version = "1.132.9"
        proto.client_version_code = "2019121229"
        proto.system_software = "Android OS 15 / API-35 (AP3A.240905.015.A2/185014)"
        proto.system_hardware = "Handheld"
        proto.device_type = "Handheld"
        proto.screen_width = 1600
        proto.screen_height = 719
        proto.screen_dpi = "234"
        proto.processor_details = "ARM64 FP ASIMD AES | 1820 | 8"
        proto.memory = 2798
        proto.gpu_renderer = "Mali-G57"
        proto.gpu_version = "OpenGL ES 3.2 v1.r49p1-04eac0.2848c17a2fd4e9340e06555168eaa3c9"
        proto.unique_device_id = f"Google|36e47927-a336-4e7e-b4f2-62ec087963e1"
        proto.client_ip = "166.191.87.230"
        proto.language = "en"
        proto.open_id = str(open_id)
        proto.open_id_type = "4"
        proto.login_open_id_type = 4
        proto.access_token = str(access_token)
        proto.login_by = 2
        proto.platform_sdk_id = 1
        proto.origin_platform_type = "4"
        proto.primary_platform_type = "4"
        proto.reg_avatar = 1
        proto.channel_type = 3
        proto.telecom_operator = "JIO"
        proto.network_operator_a = "JIO"
        proto.network_type = "WIFI"
        proto.network_type_a = "WIFI"
        proto.cpu_type = 2
        proto.cpu_architecture = "64"
        proto.graphics_api = "OpenGLES2"
        proto.supported_astc_bitset = 8191
        proto.client_using_version = "7428b253defc164018c604a1ebbfebdf"
        proto.loading_time = 15078
        proto.release_channel = "android"
        proto.extra_info = "KqsHTx3+QOmBRR1WKvaWewlcpqJBfjki+PPHQoQG8+0yV+Uos7gUFFjHMQ/e7u6han6Fl77r7c3vMN3p8UbKgN+nfycQCgwBmWgBzomx2gj84c+p"
        proto.android_engine_init_flag = 111207
        proto.if_push = 1
        proto.is_vpn = 0
        proto.memory_available.version = 55
        proto.memory_available.hidden_value = 81
        proto.external_storage_total = 49973
        proto.external_storage_available = 11338
        proto.internal_storage_total = 854
        proto.internal_storage_available = 11466
        proto.game_disk_storage_total = 49973
        proto.game_disk_storage_available = 11466
        proto.external_sdcard_total_storage = 49973
        proto.external_sdcard_avail_storage = 11466
        proto.library_path = "/data/app/~~lHFxTCCbupG2QVJmsURtZw==/com.dts.freefireth-N3aCHpHNXpdxjD80uIIbww==/lib/arm64"
        proto.library_token = "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~lHFxTCCbupG2QVJmsURtZw==/com.dts.freefireth-N3aCHpHNXpdxjD80uIIbww==/base.apk"

        base_payload = proto.SerializeToString()

        # অতিরিক্ত protobuf ফিল্ড
        extra = b""
        extra += _pb_field(96, '{"cur_rate":[90,60,120],"support_etc2":false}')
        extra += _pb_field(97, 1)
        extra += _pb_field(99, "4")
        extra += _pb_field(100, "4")
        extra += _pb_field(102, b"\x17]ENWU\x0eR5")
        extra += _pb_field(104, 52882)
        extra += _pb_field(105, 1)
        extra += _pb_field(106, "https://dl.ak.freefiremobile.com/live/ABHotUpdates/|https://core-ak.freefiremobile.com/live/ABHotUpdates/|6b2078db9d22dd98f8e9386a39af8462")
        extra += _pb_field(107, "c8e41b7a93f02d56e1a94c7b8203f5d1")

        return await aes_encrypt(base_payload + extra, AES_KEY, AES_IV)
    except Exception as e:
        log("ERROR", f"পেলোড তৈরিতে সমস্যা : {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#     ★ OLD MajorLogin (—͞ᏚAMI求 YT_LAST_FILE theke ana) ★
#     USE_OLD_MAJORLOGIN = True  -> old payload (client 1.123.2)
#     USE_OLD_MAJORLOGIN = False -> notun payload (build_majorlogin_payload_new)
# ═══════════════════════════════════════════════════════════════

USE_OLD_MAJORLOGIN = False


async def build_majorlogin_payload_old(open_id, access_token):
    """Old main.py er EncRypTMajoRLoGin hubohu - protobuf + AES"""
    from Pb2 import MajoRLoGinrEq_pb2 as ML
    major_login = ML.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.123.2"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    return await aes_encrypt(major_login.SerializeToString(), AES_KEY, AES_IV)


async def build_majorlogin_payload(open_id, access_token, platform, client_version):
    """Dispatcher - do_login() ei function e call kore"""
    if USE_OLD_MAJORLOGIN:
        try:
            return await build_majorlogin_payload_old(open_id, access_token)
        except Exception as e:
            log("ERROR", f"Old MajorLogin payload error : {e}")
            return None
    return await build_majorlogin_payload_new(open_id, access_token, platform, client_version)


# ═══════════════════════════════════════════════════════════════
#              ★ MajorLogin রিকোয়েস্ট ★
# ═══════════════════════════════════════════════════════════════

async def send_majorlogin(client_http, data, release_version, server_url):
    """MajorLogin API তে রিকোয়েস্ট পাঠাবে"""
    try:
        url = f"{server_url}MajorLogin" if server_url.endswith('/') else f"{server_url}/MajorLogin"
        req_headers = DEFAULT_HEADERS.copy()
        req_headers["ReleaseVersion"] = str(release_version)

        response = await client_http.post(url, headers=req_headers, data=data)
        if response.status_code != 200 or len(response.content) < 40:
            # --- DEBUG: keno reject hocche ta dekhar jonno ---
            log("WARN", f"DEBUG | URL={url}")
            log("WARN", f"DEBUG | HTTP status={response.status_code} | response bytes={len(response.content)}")
            log("WARN", f"DEBUG | ReleaseVersion={release_version} | USE_OLD_MAJORLOGIN={USE_OLD_MAJORLOGIN}")
            try:
                log("WARN", f"DEBUG | body={response.content[:200]!r}")
            except Exception:
                pass
            return None

        res_proto = MajoRLoGinrEs_pb2.MajorLoginRes()
        try:
            res_proto.ParseFromString(response.content)
        except Exception:
            pass

        if not (res_proto.account_uid and res_proto.token):
            for offset in range(min(128, len(response.content))):
                try:
                    c = MajoRLoGinrEs_pb2.MajorLoginRes()
                    c.ParseFromString(response.content[offset:])
                    if c.account_uid and c.token:
                        res_proto = c
                        break
                except Exception:
                    pass

        parsed = Parser().parse(response.content.hex())
        dict_res = await parse_results(parsed)

        key_val = get_proto_field(dict_res, 22) or res_proto.key or AES_KEY
        iv_val  = get_proto_field(dict_res, 23) or res_proto.iv  or AES_IV

        if isinstance(key_val, str):
            try: key_val = bytes.fromhex(key_val)
            except Exception: pass
        if isinstance(iv_val, str):
            try: iv_val = bytes.fromhex(iv_val)
            except Exception: pass

        res_proto.key = key_val
        res_proto.iv  = iv_val
        if not res_proto.url:
            res_proto.url = server_url
        return res_proto
    except Exception as e:
        log("ERROR", f"MajorLogin সমস্যা : {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#              ★ GetLoginData রিকোয়েস্ট ★
# ═══════════════════════════════════════════════════════════════

async def send_getlogin(client_http, data, base_url, token, release_version):
    """GetLoginData API তে রিকোয়েস্ট পাঠাবে"""
    try:
        url = f"{base_url.rstrip('/')}/GetLoginData"
        req_headers = DEFAULT_HEADERS.copy()
        req_headers["ReleaseVersion"] = str(release_version)
        req_headers['Authorization'] = f"Bearer {token}"

        response = await client_http.post(url, headers=req_headers, data=data)
        if response.status_code != 200:
            return None

        res_proto = PorTs_pb2.GetLoginData()
        try:
            res_proto.ParseFromString(response.content)
        except Exception:
            pass

        parsed = Parser().parse(response.content.hex())
        dict_res = await parse_results(parsed)
        return res_proto, dict_res
    except Exception as e:
        log("ERROR", f"GetLoginData সমস্যা : {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#              ★ মূল লগইন ফাংশন (—͞ᏚAMI求 YT) ★
# ═══════════════════════════════════════════════════════════════

async def do_login(uid, password, region_pref="IND"):
    """সম্পূর্ণ লগইন প্রক্রিয়া — সব তথ্য ডিকশনারি আকারে রিটার্ন করবে"""
    async with httpx.AsyncClient(verify=False, timeout=15.0) as client_http:

        # ─── ১. ভার্সন কনফিগ আনা ───
        log("NET", "ভার্সন কনফিগারেশন আনা হচ্ছে ...")
        vc = await version_config(client_http, region_pref)
        if not vc:
            log("ERROR", "ভার্সন কনফিগ ব্যর্থ হয়েছে।")
            return None
        release_version, client_version, server_url = vc
        log("OK", f"ভার্সন : {client_version} │ রিলিজ : {release_version}")

        # ─── ২. অ্যাক্সেস টোকেন আনা ───
        log("NET", "অ্যাক্সেস টোকেন আনা হচ্ছে ...")
        tg = await get_access_token(client_http, uid, password)
        if not tg:
            log("ERROR", "UID বা পাসওয়ার্ড ভুল — অ্যাক্সেস টোকেন পাওয়া যায়নি।")
            return None
        open_id, access_token, platform = tg
        log("OK", "অ্যাক্সেস টোকেন সফলভাবে পাওয়া গেছে।")

        # ─── ৩. MajorLogin পেলোড তৈরি ───
        log("INFO", "MajorLogin পেলোড তৈরি হচ্ছে ...")
        payload = await build_majorlogin_payload(open_id, access_token, platform, client_version)
        if not payload:
            log("ERROR", "পেলোড তৈরি ব্যর্থ হয়েছে।")
            return None

        # ─── ৪. MajorLogin রিকোয়েস্ট ───
        log("NET", "MajorLogin রিকোয়েস্ট পাঠানো হচ্ছে ...")
        major_res = await send_majorlogin(client_http, payload, release_version, server_url)
        if not major_res or not major_res.account_uid:
            log("ERROR", "MajorLogin সার্ভার দ্বারা প্রত্যাখ্যাত হয়েছে।")
            return None
        log("OK", f"অ্যাকাউন্ট UID গৃহীত : {major_res.account_uid}")

        # ─── ৫. GetLoginData রিকোয়েস্ট ───
        log("NET", "GetLoginData রিকোয়েস্ট পাঠানো হচ্ছে ...")
        gl = await send_getlogin(client_http, payload, major_res.url, major_res.token, release_version)
        if not gl:
            log("ERROR", "GetLoginData ব্যর্থ হয়েছে।")
            return None
        res_proto, dict_res = gl
        log("OK", "লগইন তথ্য সফলভাবে গৃহীত হয়েছে।")

        # ─── ৬. অনলাইন ও চ্যাট সার্ভার এড্রেস পার্স ───
        online_addr = res_proto.Online_IP_Port or get_proto_field(dict_res, 14, "0.0.0.0:0")
        if ':' in online_addr:
            online_ip, online_port = online_addr.split(":")
        else:
            online_ip, online_port = "0.0.0.0", "0"

        chat_addr = res_proto.AccountIP_Port or get_proto_field(dict_res, 32, online_addr)
        if ':' in chat_addr:
            chat_ip, chat_port = chat_addr.split(":")
        else:
            chat_ip, chat_port = online_ip, online_port

        # ─── ৭. প্রিমিয়াম সাকসেস রেজাল্ট বক্স ───
        print_box("—͞ᏚAMI求 YT — LOGIN SUCCESS", [
            ("Bot UID",     major_res.account_uid),
            ("Account Name", res_proto.AccountName or "Unknown"),
            ("Region",      major_res.region or region_pref),
            ("Clan ID",     res_proto.Clan_ID or 0),
            ("Online",      f"{online_ip}:{online_port}"),
            ("Chat",        f"{chat_ip}:{chat_port}"),
            ("Server",      major_res.url),
        ])

        return {
            "bot_uid":      str(major_res.account_uid),
            "token":        major_res.token,
            "region":       major_res.region or region_pref,
            "key":          major_res.key or AES_KEY,
            "iv":           major_res.iv or AES_IV,
            "timestamp":    major_res.timestamp or int(time.time()),
            "online_ip":    online_ip,
            "online_port":  online_port,
            "chat_ip":      chat_ip,
            "chat_port":    chat_port,
            "account_name": res_proto.AccountName or "Unknown",
            "clan_id":      res_proto.Clan_ID or 0,
            "clan_data":    res_proto.Clan_Compiled_Data or "",
            "server_url":   major_res.url,
        }
