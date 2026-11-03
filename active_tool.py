# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║  AUTH GUARD v2.3 — Reusable License Authentication Module        ║
╠══════════════════════════════════════════════════════════════════╣
║  HOW TO ADD TO ANY TOOL (3 steps only):                          ║
║                                                                  ║
║  1) Copy auth_guard.py next to your tool file                    ║
║                                                                  ║
║  2) Top of your tool:                                            ║
║       from auth_guard import require_authentication              ║
║                                                                  ║
║  3) Inside: if __name__ == "__main__":                           ║
║       require_authentication(tool_name="My Tool")                ║
║                                                                  ║
║  Done! Auth will run before your tool starts.                    ║
╚══════════════════════════════════════════════════════════════════╝
"""

import hashlib
import json
import os
import platform
import subprocess
import sys
import time

try:
    import requests
except ImportError:
    print("\033[91m❌ 'requests' module missing. Install: pip install requests\033[0m")
    sys.exit(1)

# ═══════════════════ CONFIGURATION ═══════════════════
SERVER_URL   = "https://admin-panel-af2x.onrender.com"
AUTH_TOKEN   = "SEN_VERIFIED_2025"
TIMEOUT      = 35
# ═════════════════════════════════════════════════════

# ─────────────────────── COLORS ───────────────────────
C_CYAN   = "\033[96m"
C_YELLOW = "\033[93m"
C_GREEN  = "\033[92m"
C_RED    = "\033[91m"
C_BLUE   = "\033[94m"
C_MAG    = "\033[95m"
C_WHITE  = "\033[97m"
C_RESET  = "\033[0m"


# ─────────────────────── HELPERS ──────────────────────
def _clear():
    os.system("cls" if os.name == "nt" else "clear")


def _slide_print(text: str, color: str = C_GREEN, delay: float = 0.018,
                 newline: bool = True) -> None:
    """Print text with a left-to-right sliding animation."""
    sys.stdout.write(color)
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(C_RESET)
    if newline:
        sys.stdout.write("\n")
    sys.stdout.flush()


def _get_hwid():
    try:
        if os.name == "nt":
            cmd = "wmic csproduct get uuid"
            raw = subprocess.check_output(cmd, shell=True).decode().split()
            unique_str = raw[1] if len(raw) > 1 else platform.node()
        else:
            paths = [
                "/etc/machine-id",
                "/var/lib/dbus/machine-id",
                "/sys/class/android_usb/android0/iSerial",
            ]
            unique_str = ""
            for p in paths:
                if os.path.exists(p):
                    try:
                        with open(p, "r") as f:
                            unique_str = f.read().strip()
                            if unique_str:
                                break
                    except Exception:
                        pass
            if not unique_str:
                unique_str = (
                    platform.node() + platform.machine() + platform.processor()
                )
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16].upper()
    except Exception:
        return "UNKNOWN_HWID_01"


def _get_device_model():
    try:
        if os.name == "nt":
            return f"Windows PC ({platform.machine()})"
        try:
            model = subprocess.check_output(
                "getprop ro.product.model",
                shell=True,
                stderr=subprocess.DEVNULL,
            ).decode().strip()
            brand = subprocess.check_output(
                "getprop ro.product.brand",
                shell=True,
                stderr=subprocess.DEVNULL,
            ).decode().strip()
            if model:
                return f"{brand.capitalize()} {model}".strip()
        except Exception:
            pass
        return platform.system() + " " + platform.release()
    except Exception:
        return "Android Device"


# ─────────────────────── ANIMATED BANNER ──────────────
def _print_banner(tool_name="", animate: bool = True) -> None:
    """
    Print banner.
    animate=True  → slide-in animation (used only on first load)
    animate=False → instant print (used when redrawing after menu selection)
    """
    _clear()

    lines = [
        (C_GREEN,  "╔══════════════════════════════════════════════════════════════╗"),
        (C_YELLOW, "║                                                              ║"),
        (C_GREEN,  "║       ███████╗ █████╗ ███████╗██████╗  █████╗ ███╗   ██╗     ║"),
        (C_GREEN,  "║       ╚══███╔╝██╔══██╗██╔════╝██╔══██╗██╔══██╗████╗  ██║     ║"),
        (C_GREEN,  "║         ███╔╝ ███████║█████╗  ██████╔╝███████║██╔██╗ ██║     ║"),
        (C_GREEN,  "║        ███╔╝  ██╔══██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║     ║"),
        (C_GREEN,  "║       ███████╗██║  ██║██║     ██║  ██║██║  ██║██║ ╚████║     ║"),
        (C_GREEN,  "║       ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝     ║"),
        (C_YELLOW, "║                                                              ║"),
        (C_GREEN,  "╠══════════════════════════════════════════════════════════════╣"),
        (C_WHITE,  "║         Z A F R A N - K E Y - S Y S T E M   2.1              ║"),
        (C_GREEN,  "╠══════════════════════════════════════════════════════════════╣"),
    ]

    if animate:
        for color, line in lines:
            _slide_print(line, color=color, delay=0.003)
        if tool_name:
            line = "║" + f"  Tool: {tool_name}"[:62].ljust(62) + "║"
            _slide_print(line, color=C_YELLOW, delay=0.005)
        hwid = _get_hwid()
        device = _get_device_model()[:42]
        _slide_print("║ [+] HWID   : " + hwid.ljust(46) + "  ║", color=C_GREEN, delay=0.005)
        _slide_print("║ [+] Device : " + device.ljust(46) + "  ║", color=C_GREEN, delay=0.005)
        _slide_print("╚══════════════════════════════════════════════════════════════╝",
                     color=C_GREEN, delay=0.005)
    else:
        # Instant redraw — no animation
        for color, line in lines:
            print(color + line + C_RESET)
        if tool_name:
            line = "║" + f"  Tool: {tool_name}"[:62].ljust(62) + "║"
            print(C_YELLOW + line + C_RESET)
        hwid = _get_hwid()
        device = _get_device_model()[:42]
        print(C_GREEN + "║ [+] HWID   : " + hwid.ljust(46) + "║" + C_RESET)
        print(C_GREEN + "║ [+] Device : " + device.ljust(46) + "║" + C_RESET)
        print(C_GREEN + "╚══════════════════════════════════════════════════════════════╝" + C_RESET)

    print()


# ─────────────────── SERVER VERIFICATION ──────────────
def _verify_with_server(license_key: str) -> bool:
    headers = {"Content-Type": "application/json"}
    payload = {
        "key":   license_key,
        "hwid":  _get_hwid(),
        "model": _get_device_model(),
    }

    _slide_print("[*] Validating license with server...", color=C_YELLOW, delay=0.012)
    try:
        res = requests.post(
            f"{SERVER_URL}/api/verify",
            data=json.dumps(payload),
            headers=headers,
            timeout=TIMEOUT,
        )
        data = res.json()

        if data.get("status"):
            _slide_print("[✓] LICENSE VALIDATED SUCCESSFULLY!", color=C_GREEN, delay=0.014)
            _slide_print(f"[+] Expiry: {data.get('expiry', 'N/A')}", color=C_WHITE, delay=0.012)
            time.sleep(1.2)
            return True
        _slide_print(f"[-] Access Denied: {data.get('message', 'Invalid key')}",
                     color=C_RED, delay=0.012)
        return False
    except Exception as e:
        _slide_print(f"[-] Server connection error: {e}", color=C_RED, delay=0.012)
        return False


# ─────────────────────── LOGIN FLOW ───────────────────
def _login_flow(tool_name: str) -> bool:
    _print_banner(tool_name, animate=False)   # static redraw, only new lines slide
    _slide_print("[*] LICENSE KEY LOGIN", color=C_GREEN, delay=0.018)
    print()
    key = input(f"{C_BLUE}[?] Enter License Key:{C_RESET} ").strip()
    if not key:
        _slide_print("[-] Key blank nahi ho sakti!", color=C_RED, delay=0.012)
        time.sleep(1.5)
        return False
    return _verify_with_server(key)


# ──────────────────── REGISTRATION FLOW ───────────────
def _register_flow(tool_name: str) -> bool:
    headers = {"Content-Type": "application/json"}
    hwid = _get_hwid()
    model = _get_device_model()

    _print_banner(tool_name, animate=False)
    _slide_print("[*] REGISTER NEW DEVICE (GMAIL OTP)", color=C_GREEN, delay=0.018)
    print()

    while True:
        email = input(f"{C_BLUE}[?] Apna Gmail address:{C_RESET} ").strip().lower()
        if email and "@" in email:
            break
        _slide_print("[-] Invalid Gmail!", color=C_RED, delay=0.012)
        print()

    _slide_print("[*] Sending OTP...", color=C_YELLOW, delay=0.014)
    try:
        res = requests.post(
            f"{SERVER_URL}/api/send_otp",
            data=json.dumps({"email": email}),
            headers=headers,
            timeout=TIMEOUT,
        )
        data = res.json()
        if not data.get("status"):
            _slide_print(f"[-] Error: {data.get('message')}", color=C_RED, delay=0.012)
            input("\nPress Enter to return...")
            return False
        _slide_print("[+] OTP bhej diya! Gmail check karein.", color=C_GREEN, delay=0.014)
        print()
    except Exception as e:
        _slide_print(f"[-] Server error: {e}", color=C_RED, delay=0.012)
        input("\nPress Enter to return...")
        return False

    while True:
        otp = input(f"{C_BLUE}[?] 6-digit OTP:{C_RESET} ").strip()
        if len(otp) == 6:
            break
        _slide_print("[-] 6-digit OTP enter karein!", color=C_RED, delay=0.012)

    _slide_print("[*] Verifying OTP...", color=C_YELLOW, delay=0.014)
    try:
        payload = {"email": email, "otp": otp, "hwid": hwid, "model": model}
        res = requests.post(
            f"{SERVER_URL}/api/verify_otp",
            data=json.dumps(payload),
            headers=headers,
            timeout=TIMEOUT,
        )
        d = res.json()
        if not d.get("status"):
            _slide_print(f"[-] Failed: {d.get('message')}", color=C_RED, delay=0.012)
            input("\nPress Enter to return...")
            return False
        _slide_print("[✓] Device registered!", color=C_GREEN, delay=0.014)
    except Exception as e:
        _slide_print(f"[-] Server Error: {e}", color=C_RED, delay=0.012)
        input("\nPress Enter to return...")
        return False

    print()
    _slide_print("─" * 61, color=C_MAG, delay=0.001)
    _slide_print("[!] Admin aapka License Key approve kar raha hai.", color=C_YELLOW, delay=0.014)
    _slide_print("─" * 61, color=C_MAG, delay=0.001)
    print()

    while True:
        key = input(f"{C_BLUE}[?] Enter License Key:{C_RESET} ").strip()
        if not key:
            _slide_print("[-] Key blank nahi ho sakti!", color=C_RED, delay=0.012)
            continue
        if _verify_with_server(key):
            return True
        if input("\nDobara try? (y/n): ").strip().lower() != "y":
            return False


# ═══════════════════════ PUBLIC API ═══════════════════════
def require_authentication(tool_name: str = None) -> bool:
    if os.environ.get("SEN_AUTH_TOKEN") == AUTH_TOKEN:
        return True

    if tool_name is None:
        tool_name = os.path.basename(sys.argv[0]) if sys.argv else "tool"

    first_load = True

    while True:
        # Animate only on first load, static redraw afterwards
        _print_banner(tool_name, animate=first_load)
        first_load = False

        _slide_print("  1. Login with License Key", color=C_GREEN, delay=0.015)
        _slide_print("  2. Register New Device (Gmail OTP)", color=C_GREEN, delay=0.015)
        _slide_print("  3. Exit", color=C_YELLOW, delay=0.015)
        print()
        choice = input(f"{C_BLUE}[?] Select (1-3):{C_RESET} ").strip()

        if choice == "1":
            if _login_flow(tool_name):
                os.environ["SEN_AUTH_TOKEN"] = AUTH_TOKEN
                _slide_print("[✓] Access Granted! Starting tool...", color=C_GREEN, delay=0.018)
                time.sleep(1.0)
                return True
            input("\nPress Enter to return...")

        elif choice == "2":
            if _register_flow(tool_name):
                os.environ["SEN_AUTH_TOKEN"] = AUTH_TOKEN
                _slide_print("[✓] Access Granted! Starting tool...", color=C_GREEN, delay=0.018)
                time.sleep(1.0)
                return True
            input("\nPress Enter to return...")

        elif choice == "3":
            _clear()
            sys.exit(0)


# ─────────────────── Standalone Test ──────────────────
if __name__ == "__main__":
    require_authentication(tool_name="SYSTEM MANUFACTURING (@SEN_HACKER)")
    print("✅ Auth OK. This module is meant to be imported by other tools.")
# -*- coding: utf-8 -*-
# ---------------- START ----------------
#!/usr/bin/env python3
import os
import sys
import struct
import json
import shutil
from datetime import datetime
import time

OUTPUT_PATH = "/storage/emulated/0/Download/ActiveSav_Script/ZAFRAN"
OUTPUT_FILE = os.path.join(OUTPUT_PATH, "Float&Int.txt")
ACTIVE_SAV_PATH = os.path.join(OUTPUT_PATH, "Active.sav")
BACKUP_PATH = os.path.join(OUTPUT_PATH, "Backups")
TEMPLATE_PATH = os.path.join(OUTPUT_PATH, "Templates")

# ANSI Color Codes for Terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BLACK = '\033[30m'
    WHITE = '\033[97m'
    MAGENTA = '\033[35m'
    DARK_GRAY = '\033[90m'
    LIGHT_GRAY = '\033[37m'

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    banner = f"""
{Colors.BOLD}{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║  ███████╗ █████╗ ███████╗██████╗  █████╗ ███╗   ██╗                      ║
║  ╚══███╔╝██╔══██╗██╔════╝██╔══██╗██╔══██╗████╗  ██║                      ║
║    ███╔╝ ███████║█████╗  ██████╔╝███████║██╔██╗ ██║                      ║
║   ███╔╝  ██╔══██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║                      ║
║  ███████╗██║  ██║██║     ██║  ██║██║  ██║██║ ╚████║                      ║
║  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝                      ║
║                                                                          ║
║  {Colors.YELLOW}⚡ ULTIMATE UE4 Active.sav TOOL ⚡{Colors.GREEN}                                      ║
║  {Colors.DARK_GRAY}Created by: {Colors.GREEN}ZAFRAN{Colors.WHITE} | Version: 4.6/4.7/4.8 | Data.Base Edition{Colors.GREEN}               ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(banner)

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}╔{'═'*60}╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.END}{Colors.BOLD}{Colors.YELLOW}{title:^60}{Colors.END}{Colors.BOLD}{Colors.BLUE}║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚{'═'*60}╝{Colors.END}\n")

def print_progress_bar(current, total, prefix='Progress:', suffix='Complete', length=50):
    if total == 0:
        total = 1
    percent = (current / total) * 100
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    print(f'\r{Colors.CYAN}{prefix} |{Colors.GREEN}{bar}{Colors.CYAN}| {Colors.YELLOW}{percent:.1f}%{Colors.END} {Colors.WHITE}{suffix}{Colors.END}', end='', flush=True)
    if current == total:
        print()

def show_loading_animation(seconds=0.5):
    animation = "⣾⣽⣻⢿⡿⣟⣯⣷"
    iterations = max(1, int(seconds * 10))
    for i in range(iterations):
        sys.stdout.write(f"\r{Colors.GREEN}Processing {animation[i % len(animation)]}{Colors.END}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 20 + "\r")

def ensure_paths():
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    os.makedirs(BACKUP_PATH, exist_ok=True)
    os.makedirs(TEMPLATE_PATH, exist_ok=True)

# ---------------- UTILS ----------------
def le_int(val):
    return struct.pack("<i", val)

def le_uint(val):
    return struct.pack("<I", val)

def le_float(val):
    return struct.pack("<f", val)

def le_double(val):
    return struct.pack("<d", val)

def le_bool(val):
    return struct.pack("<?", val)

def hexify(b):
    return " ".join(f"{x:02X}" for x in b)

def name_block(name):
    raw = name.encode("ascii") + b"\x00"
    size = le_int(len(raw))
    return hexify(size), hexify(raw)

def backup_sav():
    if os.path.exists(ACTIVE_SAV_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_PATH, f"Active_{timestamp}.sav")
        shutil.copy2(ACTIVE_SAV_PATH, backup_file)
        return backup_file
    return None

def restore_backup():
    backups = [f for f in os.listdir(BACKUP_PATH) if f.endswith('.sav')]
    if not backups:
        return None
    latest = max(backups, key=lambda x: os.path.getctime(os.path.join(BACKUP_PATH, x)))
    shutil.copy2(os.path.join(BACKUP_PATH, latest), ACTIVE_SAV_PATH)
    return latest

def write_hex(name, data, prop_type):
    ensure_paths()
    with open(OUTPUT_FILE, "a") as f:
        f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{prop_type}] {name}\n")
        f.write(data + "\n")
        f.write("="*80 + "\n")
    
    print(f"\n{Colors.GREEN}✅ HEX Generated and Saved!{Colors.END}")
    print(f"{Colors.CYAN}📁 Saved to: {OUTPUT_FILE}{Colors.END}")

def append_to_sav(hex_data, finalize=False):
    ensure_paths()
    if not os.path.exists(ACTIVE_SAV_PATH):
        print(f"{Colors.RED}❌ Active.sav not found at: {ACTIVE_SAV_PATH}{Colors.END}")
        return

    backup_sav()
    with open(ACTIVE_SAV_PATH, "rb") as f:
        content = f.read()

    new_bytes = bytes.fromhex(hex_data)
    
    # Standard terminal sequences
    eof_marker = b"\x05\x00\x00\x00None\x00\x00"
    std_marker = b"\x05\x00\x00\x00None\x00"
    
    pos = content.rfind(eof_marker)
    if pos != -1:
        base = content[:pos]
    else:
        pos2 = content.rfind(std_marker)
        if pos2 != -1:
            base = content[:pos2]
        else:
            base = content

    if finalize:
        # File complete close with legal EOF
        updated = base + new_bytes + eof_marker
        print(f"\n{Colors.GREEN}🔒 Active.sav closed legally with final None EOF.{Colors.END}")
    else:
        # File open for continuous injection (keep struct terminator ready)
        updated = base + new_bytes + eof_marker

    with open(ACTIVE_SAV_PATH, "wb") as f:
        f.write(updated)
        
    print(f"{Colors.GREEN}✅ HEX Added to Active.sav!{Colors.END}")
    print(f"{Colors.CYAN}📁 Updated: {ACTIVE_SAV_PATH}{Colors.END}")

def close_active_sav_manually():
    ensure_paths()
    if not os.path.exists(ACTIVE_SAV_PATH):
        print(f"{Colors.RED}❌ Active.sav not found!{Colors.END}")
        return

    backup_sav()
    with open(ACTIVE_SAV_PATH, "rb") as f:
        content = f.read()

    eof_marker = b"\x05\x00\x00\x00None\x00\x00"
    if content.endswith(eof_marker):
        print(f"{Colors.YELLOW}ℹ️ Active.sav already properly closed with legal EOF.{Colors.END}")
        return

    std_marker = b"\x05\x00\x00\x00None\x00"
    pos = content.rfind(std_marker)
    if pos != -1:
        updated = content[:pos] + eof_marker
    else:
        updated = content + eof_marker

    with open(ACTIVE_SAV_PATH, "wb") as f:
        f.write(updated)
    print(f"{Colors.GREEN}✅ Active.sav successfully locked with None EOF!{Colors.END}")

# ---------------- MAP PROPERTY MAKER ----------------
def make_map_int_int():
    print_header("MAP PROPERTY (INT -> INT) CREATOR")
    name = input(f"{Colors.YELLOW}📝 Map Property Name: {Colors.END}").strip()
    
    while True:
        try:
            num_pairs = int(input(f"{Colors.YELLOW}🔢 Number of Key-Value pairs: {Colors.END}"))
            if num_pairs > 0:
                break
            print(f"{Colors.RED}❌ Number must be positive!{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input! Enter a number.{Colors.END}")
    
    pairs = []
    print(f"\n{Colors.CYAN}Enter {num_pairs} key-value pairs (Key = Int, Value = Int):{Colors.END}")
    for i in range(num_pairs):
        print(f"\n{Colors.YELLOW}Pair [{i+1}]:{Colors.END}")
        while True:
            try:
                key = int(input(f"  {Colors.GREEN}Key{Colors.END}: "))
                value = int(input(f"  {Colors.GREEN}Value{Colors.END}: "))
                pairs.append((key, value))
                break
            except ValueError:
                print(f"{Colors.RED}❌ Invalid! Enter integers.{Colors.END}")
    
    show_loading_animation(0.5)
    
    # Name block
    n_size, n_hex = name_block(name)
    
    # MapProperty header
    p_size, p_hex = name_block("MapProperty")
    
    # Key type: IntProperty
    k_size, k_hex = name_block("IntProperty")
    
    # Value type: IntProperty
    v_size, v_hex = name_block("IntProperty")
    
    # Payload = 4 bytes (NumKeysToRemove) + 4 bytes (num_pairs) + (pairs * 8 bytes)
    payload_size = 8 + (num_pairs * 8)
    
    pairs_data = b"".join(le_int(k) + le_int(v) for k, v in pairs)
    
    full = (f"{n_size} {n_hex} {p_size} {p_hex} "
            f"{hexify(le_int(payload_size))} 00 00 00 00 "
            f"{k_size} {k_hex} {v_size} {v_hex} 00 "
            f"00 00 00 00 "
            f"{hexify(le_int(num_pairs))} {hexify(pairs_data)}")
    
    write_hex(name, full, "MapProperty[Int->Int]")
    return full

# ---------------- ARRAY PROPERTY MAKERS ----------------
def make_array_float():
    print_header("ARRAY PROPERTY (FLOAT) CREATOR")
    name = input(f"{Colors.YELLOW}📝 Array Property Name: {Colors.END}").strip()
    
    while True:
        try:
            num_elements = int(input(f"{Colors.YELLOW}🔢 Number of Float values in array: {Colors.END}"))
            if num_elements > 0:
                break
            print(f"{Colors.RED}❌ Number must be positive!{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input! Enter a number.{Colors.END}")
    
    values = []
    print(f"\n{Colors.CYAN}Enter {num_elements} float values:{Colors.END}")
    for i in range(num_elements):
        while True:
            try:
                val = float(input(f"  Value [{i+1}]: {Colors.END}"))
                values.append(val)
                break
            except ValueError:
                print(f"{Colors.RED}❌ Invalid! Enter a float number.{Colors.END}")
    
    show_loading_animation(0.5)
    
    n_size, n_hex = name_block(name)
    p_size, p_hex = name_block("ArrayProperty")
    inner_size, inner_hex = name_block("FloatProperty")
    
    # Payload = 4 bytes (count) + (elements * 4 bytes)
    payload_size = 4 + (num_elements * 4)
    data_bytes = b"".join(le_float(v) for v in values)
    
    full = (f"{n_size} {n_hex} {p_size} {p_hex} "
            f"{hexify(le_int(payload_size))} 00 00 00 00 "
            f"{inner_size} {inner_hex} 00 "
            f"{hexify(le_int(num_elements))} {hexify(data_bytes)}")
    
    write_hex(name, full, "ArrayProperty[Float]")
    return full

def make_array_int():
    print_header("ARRAY PROPERTY (INTEGER) CREATOR")
    name = input(f"{Colors.YELLOW}📝 Array Property Name: {Colors.END}").strip()
    
    while True:
        try:
            num_elements = int(input(f"{Colors.YELLOW}🔢 Number of Integer values in array: {Colors.END}"))
            if num_elements > 0:
                break
            print(f"{Colors.RED}❌ Number must be positive!{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input! Enter a number.{Colors.END}")
    
    values = []
    print(f"\n{Colors.CYAN}Enter {num_elements} integer values:{Colors.END}")
    for i in range(num_elements):
        while True:
            try:
                val = int(input(f"  Value [{i+1}]: {Colors.END}"))
                values.append(val)
                break
            except ValueError:
                print(f"{Colors.RED}❌ Invalid! Enter an integer.{Colors.END}")
    
    show_loading_animation(0.5)
    
    n_size, n_hex = name_block(name)
    p_size, p_hex = name_block("ArrayProperty")
    inner_size, inner_hex = name_block("IntProperty")
    
    # Payload = 4 bytes (count) + (elements * 4 bytes)
    payload_size = 4 + (num_elements * 4)
    data_bytes = b"".join(le_int(v) for v in values)
    
    full = (f"{n_size} {n_hex} {p_size} {p_hex} "
            f"{hexify(le_int(payload_size))} 00 00 00 00 "
            f"{inner_size} {inner_hex} 00 "
            f"{hexify(le_int(num_elements))} {hexify(data_bytes)}")
    
    write_hex(name, full, "ArrayProperty[Int]")
    return full

# ---------------- PROPERTY MAKERS ----------------
def make_float():
    print_header("FLOAT PROPERTY CREATOR")
    name = input(f"{Colors.YELLOW}📝 Property Name: {Colors.END}").strip()
    
    while True:
        try:
            value = float(input(f"{Colors.YELLOW}🔢 Float Value: {Colors.END}"))
            break
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input!{Colors.END}")
    
    show_loading_animation(0.5)
    
    n_size, n_hex = name_block(name)
    p_size, p_hex = name_block("FloatProperty")
    value_hex = hexify(le_float(value))
    
    full = (f"{n_size} {n_hex} {p_size} {p_hex} "
            f"04 00 00 00 00 00 00 00 00 {value_hex}")
    
    write_hex(name, full, "FloatProperty")
    return full

def make_int():
    print_header("INTEGER PROPERTY CREATOR")
    name = input(f"{Colors.YELLOW}📝 Property Name: {Colors.END}").strip()
    
    while True:
        try:
            value = int(input(f"{Colors.YELLOW}🔢 Integer Value: {Colors.END}"))
            break
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input!{Colors.END}")
    
    show_loading_animation(0.5)
    
    n_size, n_hex = name_block(name)
    p_size, p_hex = name_block("IntProperty")
    val_hex = hexify(le_int(value))
    
    full = (f"{n_size} {n_hex} {p_size} {p_hex} "
            f"04 00 00 00 00 00 00 00 00 {val_hex}")
    
    write_hex(name, full, "IntProperty")
    return full

def make_bool():
    print_header("BOOLEAN PROPERTY CREATOR")
    name = input(f"{Colors.YELLOW}📝 Property Name: {Colors.END}").strip()
    
    while True:
        value_input = input(f"{Colors.YELLOW}🔘 Boolean Value (True/False/1/0): {Colors.END}").strip().lower()
        if value_input in ['true', 'false', '1', '0', 'yes', 'no']:
            value = value_input in ['true', '1', 'yes']
            break
        print(f"{Colors.RED}❌ Invalid!{Colors.END}")
    
    show_loading_animation(0.5)
    
    n_size, n_hex = name_block(name)
    p_size, p_hex = name_block("BoolProperty")
    val_byte = "01" if value else "00"
    
    full = (f"{n_size} {n_hex} {p_size} {p_hex} "
            f"00 00 00 00 00 00 00 00 {val_byte} 00")
    
    write_hex(name, full, "BoolProperty")
    return full

def make_string():
    print_header("STRING PROPERTY CREATOR")
    name = input(f"{Colors.YELLOW}📝 Property Name: {Colors.END}").strip()
    value = input(f"{Colors.YELLOW}📄 String Value: {Colors.END}").strip()
    
    show_loading_animation(0.5)
    
    n_size, n_hex = name_block(name)
    p_size, p_hex = name_block("StrProperty")
    str_bytes = value.encode("utf-8") + b"\x00"
    str_len = len(str_bytes)
    payload_size = le_int(4 + str_len)
    str_hex = hexify(le_int(str_len)) + " " + hexify(str_bytes)
    
    full = (f"{n_size} {n_hex} {p_size} {p_hex} "
            f"{hexify(payload_size)} 00 00 00 00 00 {str_hex}")
    
    write_hex(name, full, "StringProperty")
    return full

def make_double():
    print_header("DOUBLE PROPERTY CREATOR")
    name = input(f"{Colors.YELLOW}📝 Property Name: {Colors.END}").strip()
    
    while True:
        try:
            value = float(input(f"{Colors.YELLOW}🔢 Double Value: {Colors.END}"))
            break
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input!{Colors.END}")
    
    show_loading_animation(0.5)
    
    n_size, n_hex = name_block(name)
    p_size, p_hex = name_block("DoubleProperty")
    val_hex = hexify(le_double(value))
    
    full = (f"{n_size} {n_hex} {p_size} {p_hex} "
            f"08 00 00 00 00 00 00 00 00 {val_hex}")
    
    write_hex(name, full, "DoubleProperty")
    return full

def make_vector():
    print_header("VECTOR PROPERTY CREATOR (3D Position)")
    name = input(f"{Colors.YELLOW}📝 Property Name: {Colors.END}").strip()
    
    while True:
        try:
            print(f"{Colors.CYAN}Enter Vector coordinates:{Colors.END}")
            x = float(input(f"  {Colors.YELLOW}X: {Colors.END}"))
            y = float(input(f"  {Colors.YELLOW}Y: {Colors.END}"))
            z = float(input(f"  {Colors.YELLOW}Z: {Colors.END}"))
            break
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input!{Colors.END}")
    
    show_loading_animation(0.5)
    
    n_size, n_hex = name_block(name)
    p_size, p_hex = name_block("StructProperty")
    struct_type_size, struct_type_hex = name_block("Vector")
    vector_hex = f"{hexify(le_float(x))} {hexify(le_float(y))} {hexify(le_float(z))}"
    
    full = (f"{n_size} {n_hex} {p_size} {p_hex} "
            f"0C 00 00 00 00 00 00 00 "
            f"{struct_type_size} {struct_type_hex} "
            f"00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
            f"{vector_hex}")
    
    write_hex(name, full, "VectorProperty")
    return full

def property_off_and_continue_flow():
    clear_screen()
    print_header("ACTIVE.SAV PROPERTY OFF & CONTINUE")
    print(f"{Colors.CYAN}Yeh feature Active.sav ke aakhir mein EOF marker ko check ya finalize karta hai.{Colors.END}\n")
    print(f"  {Colors.GREEN}[1]{Colors.END} Continue Mode (Property agay likhne ke liye tayar karein)")
    print(f"  {Colors.RED}[2]{Colors.END} Property Off Mode (None EOF laga kar file band karein)")
    print(f"  {Colors.YELLOW}[0]{Colors.END} Back to Main Menu")

    mode = input(f"\n{Colors.YELLOW}➜ Select Action (1/2/0): {Colors.END}").strip()
    if mode == "1":
        print(f"\n{Colors.GREEN}✅ Continue ready! Aap bina extra 00 ke property add kar sakte hain.{Colors.END}")
    elif mode == "2":
        close_active_sav_manually()
    elif mode == "0":
        return
    else:
        print(f"{Colors.RED}❌ Invalid choice!{Colors.END}")
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

def add_property_to_sav():
    while True:
        clear_screen()
        print_banner()
        show_digital_clock()
        
        print(f"{Colors.BOLD}{Colors.CYAN}╔{'═'*55}╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.BOLD}{Colors.YELLOW}ADD PROPERTY TO ACTIVE.SAV{Colors.END}                  {Colors.BOLD}{Colors.CYAN}         ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}╠{'═'*55}╣{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}1.{Colors.END} 🎯 FloatProperty                    {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}2.{Colors.END} 🔢 IntProperty                      {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}3.{Colors.END} ✅ BoolProperty                     {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}4.{Colors.END} 📝 StringProperty                   {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}5.{Colors.END} 🔬 DoubleProperty                   {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}6.{Colors.END} 📐 VectorProperty                   {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}7.{Colors.END} 📚 ArrayProperty (Float)            {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}8.{Colors.END} 📊 ArrayProperty (Int)              {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}9.{Colors.END} 🗺️  MapProperty (Int->Int)           {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.MAGENTA}10.{Colors.END}⚡ Property Off & Continue Mode      {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.RED}0.{Colors.END} 🔙 Back to Main Menu                 {Colors.BOLD}{Colors.CYAN}             ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚{'═'*55}╝{Colors.END}")
        
        choice = input(f"\n{Colors.BOLD}{Colors.YELLOW}➜ Select property type: {Colors.END}").strip()
        
        hex_data = None
        current_property = ""
        
        if choice == "1":
            hex_data = make_float()
            current_property = "Float"
        elif choice == "2":
            hex_data = make_int()
            current_property = "Integer"
        elif choice == "3":
            hex_data = make_bool()
            current_property = "Boolean"
        elif choice == "4":
            hex_data = make_string()
            current_property = "String"
        elif choice == "5":
            hex_data = make_double()
            current_property = "Double"
        elif choice == "6":
            hex_data = make_vector()
            current_property = "Vector"
        elif choice == "7":
            hex_data = make_array_float()
            current_property = "Array[Float]"
        elif choice == "8":
            hex_data = make_array_int()
            current_property = "Array[Int]"
        elif choice == "9":
            hex_data = make_map_int_int()
            current_property = "Map[Int->Int]"
        elif choice == "10":
            property_off_and_continue_flow()
            continue
        elif choice == "0":
            break
        else:
            print(f"{Colors.RED}❌ Invalid Option!{Colors.END}")
            time.sleep(1)
            continue
        
        if hex_data:
            print()
            for i in range(101):
                print_progress_bar(i, 100, prefix='Adding to Active.sav:', suffix='Complete')
                time.sleep(0.005)

            print(f"\n{Colors.BOLD}{Colors.YELLOW}══════════════ ACTIONS (Agay Kya Karna Hai?) ══════════════{Colors.END}")
            print(f"  {Colors.GREEN}[1]{Colors.END} Continue (Aur property add karni hai - No trailing junk)")
            print(f"  {Colors.RED}[2]{Colors.END} Bandh (None EOF lagana hai aur file close karni hai)")
            
            end_choice = input(f"\n{Colors.YELLOW}➜ Option select karein (1=Continue / 2=Bandh): {Colors.END}").strip()
            
            if end_choice == "2":
                append_to_sav(hex_data, finalize=True)
                input(f"\n{Colors.CYAN}File closed successfully! Press Enter to continue...{Colors.END}")
                break
            else:
                append_to_sav(hex_data, finalize=False)
                another = input(f"\n{Colors.YELLOW}Add another property now? (y/n): {Colors.END}").strip().lower()
                if another != 'y':
                    break

def view_active_sav():
    print_header("ACTIVE.SAV VIEWER")
    
    if not os.path.exists(ACTIVE_SAV_PATH):
        print(f"{Colors.RED}❌ No Active.sav file found!{Colors.END}")
        return
    
    file_size = os.path.getsize(ACTIVE_SAV_PATH)
    print(f"{Colors.CYAN}📁 File: {ACTIVE_SAV_PATH}{Colors.END}")
    print(f"{Colors.CYAN}📏 Size: {file_size} bytes{Colors.END}")
    print(f"{Colors.CYAN}🕐 Last Modified: {datetime.fromtimestamp(os.path.getmtime(ACTIVE_SAV_PATH)).strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}╔{'═'*60}╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}║{Colors.END}{Colors.BOLD} HEX DUMP (First 256 bytes){Colors.END}{Colors.BOLD}{Colors.YELLOW}║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}╚{'═'*60}╝{Colors.END}\n")
    
    with open(ACTIVE_SAV_PATH, "rb") as f:
        data = f.read(256)
    
    hex_lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        hex_lines.append(f"{Colors.DARK_GRAY}{i:04X}{Colors.END}  {Colors.GREEN}{hex_part:<48}{Colors.END}  {Colors.CYAN}{ascii_part}{Colors.END}")
    
    print("\n".join(hex_lines))
    
    if file_size > 256:
        print(f"\n{Colors.DARK_GRAY}... and {file_size - 256} more bytes{Colors.END}")

def file_management():
    print_header("FILE MANAGEMENT")
    
    print(f"{Colors.CYAN}Options:{Colors.END}")
    print(f"  {Colors.GREEN}1.{Colors.END} Backup Active.sav")
    print(f"  {Colors.GREEN}2.{Colors.END} Restore from Backup")
    print(f"  {Colors.GREEN}3.{Colors.END} Export to JSON")
    print(f"  {Colors.GREEN}4.{Colors.END} Delete Active.sav")
    print(f"  {Colors.RED}5.{Colors.END} Back to Main Menu")
    
    choice = input(f"\n{Colors.YELLOW}Select Option: {Colors.END}").strip()
    
    if choice == "1":
        backup = backup_sav()
        if backup:
            print(f"{Colors.GREEN}✅ Backup created: {backup}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ No Active.sav found!{Colors.END}")
    elif choice == "2":
        restored = restore_backup()
        if restored:
            print(f"{Colors.GREEN}✅ Restored from: {restored}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ No backup found!{Colors.END}")
    elif choice == "3":
        export_json()
    elif choice == "4":
        confirm = input(f"{Colors.RED}⚠️ Delete Active.sav? (yes/no): {Colors.END}")
        if confirm.lower() == 'yes':
            if os.path.exists(ACTIVE_SAV_PATH):
                os.remove(ACTIVE_SAV_PATH)
                print(f"{Colors.GREEN}✅ Active.sav deleted!{Colors.END}")
            else:
                print(f"{Colors.RED}❌ File not found!{Colors.END}")
    elif choice == "5":
        return
    else:
        print(f"{Colors.RED}❌ Invalid Option!{Colors.END}")
        time.sleep(1)

def export_json():
    if not os.path.exists(ACTIVE_SAV_PATH):
        print(f"{Colors.RED}❌ No Active.sav found!{Colors.END}")
        return
    
    data = {
        "file": ACTIVE_SAV_PATH,
        "size": os.path.getsize(ACTIVE_SAV_PATH),
        "export_time": datetime.now().isoformat(),
        "backup_count": len([f for f in os.listdir(BACKUP_PATH) if f.endswith('.sav')])
    }
    
    json_file = os.path.join(OUTPUT_PATH, f"Active_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(json_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"{Colors.GREEN}✅ Exported to: {json_file}{Colors.END}")

def template_manager():
    print_header("TEMPLATE MANAGER")
    
    print(f"{Colors.CYAN}Options:{Colors.END}")
    print(f"  {Colors.GREEN}1.{Colors.END} Save Template")
    print(f"  {Colors.GREEN}2.{Colors.END} Load Template")
    print(f"  {Colors.GREEN}3.{Colors.END} List Templates")
    print(f"  {Colors.RED}4.{Colors.END} Back to Main Menu")
    
    choice = input(f"\n{Colors.YELLOW}Select Option: {Colors.END}").strip()
    
    if choice == "1":
        name = input(f"{Colors.YELLOW}Template Name: {Colors.END}").strip()
        prop_type = input(f"{Colors.YELLOW}Property Type (float/int/bool/string/double/vector/arrayfloat/arrayint/mapintint): {Colors.END}").strip()
        prop_name = input(f"{Colors.YELLOW}Property Name: {Colors.END}").strip()
        prop_value = input(f"{Colors.YELLOW}Property Value: {Colors.END}").strip()
        
        template = {
            "name": name,
            "type": prop_type,
            "property_name": prop_name,
            "value": prop_value,
            "created": datetime.now().isoformat()
        }
        
        template_file = os.path.join(TEMPLATE_PATH, f"{name}.json")
        with open(template_file, "w") as f:
            json.dump(template, f, indent=2)
        
        print(f"{Colors.GREEN}✅ Template saved: {template_file}{Colors.END}")
    
    elif choice == "2":
        templates = [f.replace('.json', '') for f in os.listdir(TEMPLATE_PATH) if f.endswith('.json')]
        if not templates:
            print(f"{Colors.RED}❌ No templates found!{Colors.END}")
            return
        
        print(f"\n{Colors.CYAN}Available Templates:{Colors.END}")
        for i, t in enumerate(templates, 1):
            print(f"  {Colors.GREEN}{i}.{Colors.END} {t}")
        
        try:
            idx = int(input(f"\n{Colors.YELLOW}Select template: {Colors.END}")) - 1
            if 0 <= idx < len(templates):
                template_file = os.path.join(TEMPLATE_PATH, f"{templates[idx]}.json")
                with open(template_file, "r") as f:
                    template = json.load(f)
                print(f"{Colors.GREEN}✅ Loaded: {template['name']}{Colors.END}")
                print(f"{Colors.CYAN}Type: {template['type']}, Name: {template['property_name']}, Value: {template['value']}{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Invalid selection!{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input!{Colors.END}")
    
    elif choice == "3":
        templates = [f.replace('.json', '') for f in os.listdir(TEMPLATE_PATH) if f.endswith('.json')]
        if templates:
            print(f"\n{Colors.CYAN}📁 Templates in {TEMPLATE_PATH}:{Colors.END}")
            for t in templates:
                print(f"  {Colors.GREEN}•{Colors.END} {t}")
        else:
            print(f"{Colors.RED}❌ No templates found!{Colors.END}")
    elif choice == "4":
        return
    else:
        print(f"{Colors.RED}❌ Invalid Option!{Colors.END}")
        time.sleep(1)

def show_digital_clock():
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    day_str = now.strftime("%A")
    
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}╔════{'═'*40}╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}║{Colors.END}  {Colors.CYAN}🕐 {time_str}  📅 {date_str}  📆 {day_str}{Colors.END}  {Colors.BOLD}{Colors.MAGENTA} ║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}╚════{'═'*40}╝{Colors.END}\n")

def main_menu():
    ensure_paths()
    
    while True:
        clear_screen()
        print_banner()
        show_digital_clock()
        
        print(f"{Colors.BOLD}{Colors.CYAN}╔{'═'*55}╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.BOLD}{Colors.YELLOW}MAIN MENU - SELECT AN OPTION{Colors.END}                      {Colors.BOLD}{Colors.CYAN}   ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}╠{'═'*55}╣{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}║{Colors.END}  {Colors.GREEN}1.{Colors.END} 🎯 FloatProperty                    {Colors.BOLD}{Colors.YELLOW}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}2.{Colors.END} 🔢 IntProperty                      {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}║{Colors.END}  {Colors.GREEN}3.{Colors.END} ✅ BoolProperty                     {Colors.BOLD}{Colors.RED}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}4.{Colors.END} 📝 StringProperty                   {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}5.{Colors.END} 🔬 DoubleProperty                   {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}║{Colors.END}  {Colors.GREEN}6.{Colors.END} 📐 VectorProperty                   {Colors.BOLD}{Colors.YELLOW}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.END}  {Colors.GREEN}7.{Colors.END} 📚 ArrayProperty (Float)            {Colors.BOLD}{Colors.BLUE}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}║{Colors.END}  {Colors.GREEN}8.{Colors.END} 📊 ArrayProperty (Int)              {Colors.BOLD}{Colors.WHITE}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}║{Colors.END}  {Colors.GREEN}9.{Colors.END} 🗺️  MapProperty (Int->Int)           {Colors.BOLD}{Colors.GREEN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLACK}║{Colors.END}  {Colors.GREEN}10.{Colors.END}💾 Add to Active.sav                {Colors.BOLD}{Colors.BLACK}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}║{Colors.END}  {Colors.GREEN}11.{Colors.END}📁 File Management                  {Colors.BOLD}{Colors.RED}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.END}  {Colors.GREEN}12.{Colors.END}📋 Template Manager                 {Colors.BOLD}{Colors.CYAN}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.END}  {Colors.GREEN}13.{Colors.END}👁️  View Active.sav                  {Colors.BOLD}{Colors.BLUE}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}║{Colors.END}  {Colors.YELLOW}14.{Colors.END}⚡ Active.sav Property Off & Continue{Colors.BOLD}{Colors.MAGENTA}             ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}║{Colors.END}  {Colors.RED}0.{Colors.END} 🚪 Exit                             {Colors.BOLD}{Colors.YELLOW}              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}╚{'═'*55}╝{Colors.END}")
        
        choice = input(f"\n{Colors.BOLD}{Colors.WHITE}➜ Enter your choice: {Colors.END}").strip()
        
        if choice == "1":
            make_float()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "2":
            make_int()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "3":
            make_bool()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "4":
            make_string()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "5":
            make_double()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "6":
            make_vector()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "7":
            make_array_float()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "8":
            make_array_int()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "9":
            make_map_int_int()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "10":
            add_property_to_sav()
        elif choice == "11":
            file_management()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "12":
            template_manager()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "13":
            view_active_sav()
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        elif choice == "14":
            property_off_and_continue_flow()
        elif choice == "0":
            print(f"\n{Colors.GREEN}👋 Goodbye! Thanks for using ZAFRAN Tool!{Colors.END}\n")
            break
        else:
            print(f"{Colors.RED}❌ Invalid option! Please try again.{Colors.END}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)
# ---------------- END ----------------
