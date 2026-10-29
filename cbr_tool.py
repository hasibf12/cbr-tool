#!/usr/bin/env python3
import os
import sys
import hashlib
import time
import subprocess
import shutil
import uuid
import platform
import threading
import tarfile
import zipfile
import glob
import json
import re

# 💻 DUAL-CORE ARCHITECTURE DETECTOR 📱
IS_WINDOWS = (platform.system().lower() == "windows")

if IS_WINDOWS:
    os.system('chcp 65001 > nul')
    os.system('color')

CYAN = "\033[36m"
ORANGE = "\033[38;5;208m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
PURPLE = "\033[35m"
HACKER_GREEN = "\033[38;5;46m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

SECURE_PASSWORD_HASH = "ed30e4a879af03333d3ba7a782b941bb92ce5fba9d6c60be387c1688e2b5ea40"
ADVANCE_PASSWORD_HASH = hashlib.sha256(bytes.fromhex("6362723031393736363334303435")).hexdigest()

FIREBASE_SECRET = "W2u5TaOnnVWpdOwkCSsLDPuUzrXnSiC0o7ngf7zJ"
SETTINGS_URL = f"https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Settings.json?auth={FIREBASE_SECRET}"
SESSION_FILE = os.path.expanduser("~/.cbr_session.json")

ACTIVE_USB_DEV = None
GRANTED_USB_DEVS = set()

def get_cloud_setting(key, default_val):
    try:
        import requests
        res = requests.get(SETTINGS_URL, timeout=8).json()
        if isinstance(res, dict) and key in res:
            return res[key]
    except:
        pass
    return default_val

def send_activity_log(action_msg):
    try:
        import requests
        raw_id = platform.node() + str(uuid.getnode())
        hwid = hashlib.md5(raw_id.encode()).hexdigest()[:15].upper()
        db_url = f"https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users/{hwid}/activity_logs.json?auth={FIREBASE_SECRET}"
        timestamp = time.strftime("%Y-%m-%d %I:%M:%S %p")
        log_data = {str(int(time.time())): f"[{timestamp}] {action_msg}"}
        requests.patch(db_url, json=log_data)
    except:
        pass

def premium_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{CYAN}{BOLD}")
    print(r"  ██████╗██████╗ ██████╗ ")
    print(r" ██╔════╝██╔══██╗██╔══██╗")
    print(r" ██║     ██████╔╝██████╔╝")
    print(r" ██║     ██╔══██╗██╔══██╗")
    print(r" ╚██████╗██████╔╝██║  ██║")
    print(r"  ╚═════╝╚═════╝ ╚═╝  ╚═╝")
    print(f"      ⚡ CBR TOOL ⚡     {RESET}")
    if IS_WINDOWS:
        print(f" {HACKER_GREEN}{BOLD}[ACTIVE MODE: WINDOWS SUPER-PC]{RESET}")
    else:
        print(f" {HACKER_GREEN}{BOLD}[ACTIVE MODE: TERMUX MOBILE]{RESET}")
    print(f"{ORANGE}{BOLD} © Copyright: Abdullah Al Hasib {RESET}")
    print(f"{DIM}{'━' * 35}{RESET}\n")

def check_dependencies():
    if not IS_WINDOWS:
        bin_dir = "/data/data/com.termux/files/usr/bin"
        shortcut_path = os.path.join(bin_dir, "cbrtool")
        script_path = os.path.abspath(__file__)
        if os.path.exists(bin_dir) and not os.path.exists(shortcut_path):
            try:
                with open(shortcut_path, "w") as f:
                    f.write(f"#!/bin/bash\npython3 '{script_path}' \"$@\"\n")
                os.chmod(shortcut_path, 0o755)
            except: pass
            
        try:
            import ssl
        except ImportError:
            print(f"{ORANGE}[*] Repairing Termux SSL...{RESET}")
            os.system("pkg update -y && pkg install openssl ca-certificates python -y")
    
    try:
        import colorama, Cryptodome, miunlock, requests 
    except ImportError:
        print(f"{ORANGE}[*] Installing basic libraries...{RESET}")
        subprocess.call([sys.executable, "-m", "pip", "install", "colorama", "pycryptodomex", "miunlock", "requests"])

    # Termux Pyside6 Crash Fix
    if not IS_WINDOWS:
        try:
            import mtkclient
        except ImportError:
            print(f"{ORANGE}[*] Installing BROM Engine (mtkclient)...{RESET}")
            # Ignore graphics libraries to prevent Termux crash
            res = subprocess.call([sys.executable, "-m", "pip", "install", "mtkclient", "--no-deps"])
            if res != 0:
                print(f"{ORANGE}[*] Force downloading from GitHub...{RESET}")
                subprocess.call([sys.executable, "-m", "pip", "install", "https://github.com/bkerler/mtkclient/archive/main.zip", "--no-deps"])
                subprocess.call([sys.executable, "-m", "pip", "install", "pycryptodome", "usb", "colorama"])
    else:
        mtk_bin = shutil.which("mtk")
        if not mtk_bin:
            scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
            if not os.path.exists(os.path.join(scripts_dir, "mtk.exe")):
                print(f"{ORANGE}[*] Installing BROM Engine (mtkclient)...{RESET}")
                subprocess.call([sys.executable, "-m", "pip", "install", "mtkclient"])

def setup_otg_drivers():
    if not IS_WINDOWS:
        try:
            if shutil.which("lsusb") is None: os.system("pkg install usbutils -y > /dev/null 2>&1")
            if not os.path.exists("/data/data/com.termux/files/usr/bin/termux-usb"):
                os.system("pkg install termux-api libusb -y > /dev/null 2>&1")
            if not os.path.exists("/data/data/com.termux/files/usr/bin/termux-fastboot"):
                os.system("curl -fsS https://raw.githubusercontent.com/nohajc/termux-adb/master/install.sh | bash > /dev/null 2>&1")
        except: pass

def get_fastboot_bin():
    if not IS_WINDOWS and shutil.which("termux-fastboot") is not None:
        return "termux-fastboot"
    return "fastboot"

def trigger_otg_popup(silent=False, force=False):
    global ACTIVE_USB_DEV, GRANTED_USB_DEVS
    if IS_WINDOWS: return False
    if shutil.which("termux-usb") is not None:
        try:
            res = subprocess.run(["termux-usb", "-l"], capture_output=True, text=True, timeout=4)
            if res.stdout and res.stdout.strip():
                usb_devs = json.loads(res.stdout.strip())
                if isinstance(usb_devs, list):
                    GRANTED_USB_DEVS.intersection_update(set(usb_devs))
                    if len(usb_devs) > 0:
                        ACTIVE_USB_DEV = usb_devs[-1]
                        for dev in usb_devs:
                            if dev in GRANTED_USB_DEVS and not force: continue
                            if not silent: print(f"{CYAN}[OTG]{RESET} Requesting USB Permission for {dev}...")
                            req = subprocess.run(["termux-usb", "-r", dev], capture_output=True, text=True, timeout=12)
                            req_out = ((req.stdout or "") + (req.stderr or "")).lower()
                            if "granted" in req_out or "yes" in req_out or (req.returncode == 0 and "denied" not in req_out):
                                GRANTED_USB_DEVS.add(dev)
                                ACTIVE_USB_DEV = dev
                                if not silent: print(f"{GREEN}[✓] OTG Permission Locked!{RESET}")
                        time.sleep(0.8)
                        return True
                    else: ACTIVE_USB_DEV = None
        except: pass
    return False

def run_usb_fastboot_probe(fb_bin, args_list, timeout_sec=5):
    global ACTIVE_USB_DEV
    try:
        res = subprocess.run([fb_bin] + args_list, capture_output=True, text=True, timeout=timeout_sec)
        comb = ((res.stdout or "") + "\n" + (res.stderr or "")).strip()
        if comb and "waiting for" not in comb.lower() and "no permissions" not in comb.lower():
            return comb
    except: pass

    if not IS_WINDOWS and ACTIVE_USB_DEV and shutil.which("termux-usb") is not None:
        for candidate_bin in [fb_bin, "fastboot", "termux-fastboot"]:
            if shutil.which(candidate_bin) is None: continue
            cmd_inner = f"{candidate_bin} {' '.join(args_list)}"
            try:
                res2 = subprocess.run(["termux-usb", "-e", cmd_inner, ACTIVE_USB_DEV], capture_output=True, text=True, timeout=timeout_sec)
                comb2 = ((res2.stdout or "") + "\n" + (res2.stderr or "")).strip()
                if comb2 and "waiting for" not in comb2.lower() and "no permissions" not in comb2.lower():
                    return comb2
            except: pass
    return ""

def check_fastboot():
    if shutil.which("fastboot") is None and shutil.which("termux-fastboot") is None:
        print(f"{RED}[!] Fastboot is not installed!{RESET}")
        if not IS_WINDOWS:
            print(f"{ORANGE}[*] Auto-installing...{RESET}")
            os.system("pkg update -y > /dev/null 2>&1 && pkg install android-tools -y")
        else: sys.exit(1)

def get_device_info():
    global ACTIVE_USB_DEV, GRANTED_USB_DEVS
    print(f"{CYAN}[INFO]{RESET} Fetching device details...")
    for attempt in range(5):
        fb_bin = get_fastboot_bin()
        trigger_otg_popup(force=(attempt > 0 and not GRANTED_USB_DEVS))
        dev_out = run_usb_fastboot_probe(fb_bin, ["devices"], timeout_sec=5)
        if dev_out and ("fastboot" in dev_out.lower() or len(dev_out.split()) >= 1):
            first_line = dev_out.splitlines()[0].strip()
            if first_line and "permission" not in first_line.lower():
                prod_out = run_usb_fastboot_probe(fb_bin, ["getvar", "product"], timeout_sec=3)
                p_name = prod_out.split("product:")[1].split()[0].strip() if "product:" in prod_out else first_line.split()[0].strip()
                print(f"{GREEN}[✓] Connected Device: {p_name}{RESET}")
                return p_name

        for var_name in ["product", "is-userspace", "serialno"]:
            var_out = run_usb_fastboot_probe(fb_bin, ["getvar", var_name], timeout_sec=4)
            if f"{var_name}:" in var_out.lower() or "okay" in var_out.lower():
                dev_label = f"Fastboot-Device ({ACTIVE_USB_DEV})" if ACTIVE_USB_DEV else "Fastboot-Device"
                print(f"{GREEN}[✓] Connected Device: {dev_label}{RESET}")
                return dev_label

        if not IS_WINDOWS and ACTIVE_USB_DEV and ACTIVE_USB_DEV in GRANTED_USB_DEVS:
            print(f"{GREEN}[✓] OTG Port Active!{RESET}")
            return f"OTG-{os.path.basename(ACTIVE_USB_DEV)}"

        print(f"{ORANGE}[!] Waiting for Device Connection... ({attempt+1}/5){RESET}")
        time.sleep(2)
    print(f"{ORANGE}[!] Could not read device product name.{RESET}")
    return None

def get_brom_device_info():
    global ACTIVE_USB_DEV, GRANTED_USB_DEVS
    print(f"{CYAN}[BROM-SCAN]{RESET} Waiting for MTK BROM Connection...")
    print(f"{ORANGE}[*] Please turn OFF phone. Hold VOLUME UP + DOWN and connect USB cable!{RESET}")
    
    end_time = time.time() + 60
    if IS_WINDOWS:
        while time.time() < end_time:
            try:
                res = subprocess.run("wmic path Win32_PnPEntity get Caption,DeviceID", shell=True, capture_output=True, text=True, creationflags=0x08000000)
                if "VID_0E8D" in res.stdout.upper() or "MediaTek" in res.stdout:
                    print(f"\n{GREEN}[✓] MediaTek BROM Port Detected!{RESET}")
                    return True
            except: pass
            sys.stdout.write(f"\r\033[K{ORANGE}>> Windows Fast Polling for BROM Port... ({int(end_time - time.time())}s){RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
    else:
        while time.time() < end_time:
            if shutil.which("termux-usb") is not None:
                try:
                    res = subprocess.run(["termux-usb", "-l"], capture_output=True, text=True, timeout=0.5)
                    if res.stdout and res.stdout.strip():
                        usb_devs = json.loads(res.stdout.strip())
                        if usb_devs:
                            ACTIVE_USB_DEV = usb_devs[-1]
                            print(f"\n{GREEN}[✓] Device Detected in BROM Mode!{RESET}")
                            req = subprocess.run(["termux-usb", "-r", ACTIVE_USB_DEV], capture_output=True, text=True, timeout=3)
                            if "granted" in req.stdout.lower() or req.returncode == 0:
                                GRANTED_USB_DEVS.add(ACTIVE_USB_DEV)
                                return True
                except: pass
            sys.stdout.write(f"\r\033[K{ORANGE}>> Ninja Polling for BROM Port... ({int(end_time - time.time())}s){RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
    print(f"\n{RED}[!] Failed to catch BROM port within 60 seconds.{RESET}")
    return False

def authenticate():
    premium_header()
    live_tool_pass = get_cloud_setting('tool_password', None)
    try:
        user_pass = input(f"{BOLD}🔑 Enter Security Token Password: {RESET}").strip()
        if (live_tool_pass and user_pass == live_tool_pass) or hashlib.sha256(user_pass.encode()).hexdigest() == SECURE_PASSWORD_HASH:
            print(f"\n{GREEN}[✓] Access Granted!{RESET}"); time.sleep(1)
            return True
        print(f"\n{RED}[✗] Access Denied!{RESET}")
        return False
    except: return False

def verify_admin_access():
    live_admin_pass = get_cloud_setting('admin_password', None)
    admin_pass = input(f"{BOLD}{ORANGE}🔑 Enter Admin Password: {RESET}").strip()
    if (live_admin_pass and admin_pass == live_admin_pass) or hashlib.sha256(admin_pass.encode()).hexdigest() == ADVANCE_PASSWORD_HASH: return True
    print(f"\n{RED}[✗] Access Denied!{RESET}"); time.sleep(2); return False


# ====== STRONG AUTO LOGIN & PING ENGINE ======
def ping_server_and_check_ban(hwid, original_pass):
    import requests
    db_url = f"https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users/{hwid}.json?auth={FIREBASE_SECRET}"
    while True:
        try:
            res = requests.get(db_url).json()
            # Strict verification: Check if banned OR password changed
            if isinstance(res, dict):
                if res.get("status") == "Banned":
                    print(f"\n\n{RED}{BOLD}admin ban you not use this tool 💥 admin ban korse Abdullah Al Hasib{RESET}")
                    if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
                    os._exit(1)
                elif res.get("password") != original_pass:
                    print(f"\n\n{RED}{BOLD}Password has been changed by Admin! Please login again.{RESET}")
                    if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
                    os._exit(1)
            requests.patch(db_url, json={"last_ping": int(time.time())})
        except: pass
        time.sleep(10) 

def start_online_ping(hwid, original_pass):
    t = threading.Thread(target=ping_server_and_check_ban, args=(hwid, original_pass), daemon=True)
    t.start()

def check_firebase_approval():
    import requests
    raw_id = platform.node() + str(uuid.getnode())
    hwid = hashlib.md5(raw_id.encode()).hexdigest()[:15].upper()
    
    try:
        brand = subprocess.getoutput('getprop ro.product.brand').strip().capitalize()
        model = subprocess.getoutput('getprop ro.product.model').strip()
        device_name = f"{brand} {model}".strip() if brand else platform.node()
    except: device_name = platform.node()
        
    base_url = "https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users"

    # Strong Session Check
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f: session_data = json.load(f)
            if session_data.get("hwid") == hwid:
                # Re-verify with server silently
                res = requests.get(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", timeout=5).json()
                if isinstance(res, dict) and res.get("status") in ["Approved", "VIP"] and res.get("password") == session_data.get("password"):
                    print(f"\n{GREEN}[✓] Auto-Login Successful! Welcome back.{RESET}")
                    start_online_ping(hwid, session_data.get("password"))
                    return True
                else:
                    os.remove(SESSION_FILE) # Invalid session, force re-login
        except: pass

    print(f"\n{CYAN}[USER LOGIN]{RESET} Please login to your account.")
    user_email = input(f"{BOLD}{ORANGE}📧 Enter Your Email: {RESET}").strip()
    user_password = input(f"{BOLD}{ORANGE}🔑 Enter Your Password: {RESET}").strip()
    
    if not user_email or not user_password:
        print(f"{RED}[!] Email and Password cannot be empty!{RESET}"); return False
    
    print(f"\n{CYAN}[SYSTEM]{RESET} Your Hardware ID: {BOLD}{ORANGE}{hwid}{RESET}")
    
    try:
        all_users = requests.get(f"{base_url}.json?auth={FIREBASE_SECRET}", timeout=10).json()
        if isinstance(all_users, dict) and "error" in all_users: return False
        if all_users is None: all_users = {}
            
        existing_hwid = None
        db_status = "Pending"
        
        for db_id, data in all_users.items():
            if isinstance(data, dict) and data.get("email") == user_email:
                existing_hwid = db_id
                if data.get("password") != user_password:
                    print(f"\n{RED}[✗] Invalid Password for this Email!{RESET}"); return False
                db_status = data.get("status", "Pending")
                break

        if existing_hwid:
            if db_status in ["Approved", "VIP"]:
                print(f"\n{GREEN}[✓] Login Successful! Welcome back. Approved by Cbr tool owner Abdullah Al Hasib{RESET}"); time.sleep(1.5)
                payload = all_users[existing_hwid]
                payload["device_name"] = device_name 
                payload["last_ping"] = int(time.time())
                
                if existing_hwid != hwid:
                    payload["hwid"] = hwid
                    requests.put(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json=payload)
                    requests.delete(f"{base_url}/{existing_hwid}.json?auth={FIREBASE_SECRET}")
                else:
                    requests.patch(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json={"device_name": device_name, "last_ping": int(time.time())})
                    
                with open(SESSION_FILE, "w") as f: json.dump({"hwid": hwid, "email": user_email, "password": user_password}, f)
                start_online_ping(hwid, user_password)
                send_activity_log("User Logged In Successfully")
                return True
            elif db_status == "Banned":
                print(f"\n{RED}{BOLD}admin ban you not use this tool 💥 admin ban korse Abdullah Al Hasib{RESET}"); return False
        else:
            payload = {"status": "Pending", "hwid": hwid, "email": user_email, "password": user_password, "device_name": device_name, "last_ping": int(time.time())}
            requests.put(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json=payload)
            existing_hwid = hwid
            send_activity_log("New Registration Created - Pending Approval")

        is_waiting = False
        db_url = f"{base_url}/{existing_hwid}.json?auth={FIREBASE_SECRET}"
        while True:
            data = requests.get(db_url, timeout=10).json()
            if not data: time.sleep(3); continue
            status = data.get("status", "Pending")
            
            if status in ["Approved", "VIP"]:
                print(f"\n{GREEN}[✓] Login Successful! Approved by Cbr tool owner Abdullah Al Hasib{RESET}"); time.sleep(1.5)
                payload = data; payload["device_name"] = device_name
                if existing_hwid != hwid:
                    payload["hwid"] = hwid
                    requests.put(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json=payload)
                    requests.delete(f"{base_url}/{existing_hwid}.json?auth={FIREBASE_SECRET}")
                else:
                    requests.patch(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json={"device_name": device_name})
                    
                with open(SESSION_FILE, "w") as f: json.dump({"hwid": hwid, "email": user_email, "password": user_password}, f)
                start_online_ping(hwid, user_password); send_activity_log("User Approved and Logged In")
                return True
            elif status == "Banned":
                print(f"\n{RED}{BOLD}admin ban you not use this tool 💥 admin ban korse Abdullah Al Hasib{RESET}"); return False
            else:
                if not is_waiting: print(f"{CYAN}[SYSTEM]{RESET} Waiting for Admin Approval", end="", flush=True); is_waiting = True
                print(".", end="", flush=True); time.sleep(3) 
    except: return False


# ====== CBR SMART FINDER ENGINE ======
def cbr_smart_scanner(mode="all"):
    print(f"\n{CYAN}[SCANNING]{RESET} Deep Scanning for ROMs in Folders...")
    search_paths = [os.path.expanduser("~\\Downloads"), os.path.expanduser("~\\Desktop"), os.getcwd()] if IS_WINDOWS else ["/sdcard/Download", os.getcwd()]
    valid_roms = []
    
    for s_path in search_paths:
        if not os.path.exists(s_path): continue
        valid_roms.extend(glob.glob(f"{s_path}/*.zip") + glob.glob(f"{s_path}/*.tgz") + glob.glob(f"{s_path}/*.tar.gz"))
        try:
            for root, dirs, files in os.walk(s_path):
                if "CBR_Extracted" in root: continue
                depth = root[len(s_path):].count(os.sep)
                if depth > 4: del dirs[:]; continue
                
                is_valid = False
                for f in files:
                    f_low = f.lower()
                    if mode == "mtk" and "scatter" in f_low and f_low.endswith(".txt"): is_valid = True; break
                    elif mode == "fastboot" and (f_low == "flash_all.sh" or f_low == "flash_all.bat"): is_valid = True; break
                    elif mode == "all" and ("scatter" in f_low or f_low == "flash_all.sh" or f_low == "flash_all.bat"): is_valid = True; break
                if is_valid and root not in valid_roms: valid_roms.append(root)
        except: pass
    return list(set(valid_roms))

def extract_safe_zip(zip_path, extract_folder):
    print(f"\n{CYAN}[EXTRACTING]{RESET} Unpacking {os.path.basename(zip_path)}...")
    if os.path.exists(extract_folder): shutil.rmtree(extract_folder)
    os.makedirs(extract_folder)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            total_size = sum(info.file_size for info in zf.infolist())
            extracted = 0
            for info in zf.infolist():
                target = os.path.join(extract_folder, info.filename)
                if info.is_dir() or info.filename.endswith('/'):
                    os.makedirs(target, exist_ok=True); continue
                os.makedirs(os.path.dirname(target), exist_ok=True)
                if os.path.isdir(target): continue
                try:
                    with zf.open(info) as src, open(target, 'wb') as tgt:
                        while True:
                            chunk = src.read(1024 * 1024)
                            if not chunk: break
                            tgt.write(chunk)
                            extracted += len(chunk)
                            pct = (extracted / total_size) * 100 if total_size > 0 else 100
                            sys.stdout.write(f"\r\033[K{ORANGE}>>{RESET} {CYAN}Unpacking: {BOLD}{GREEN}{pct:.1f}%{RESET}")
                            sys.stdout.flush()
                except zipfile.BadZipFile: pass
        print(f"\n\n{GREEN}[✓] Extraction Complete!{RESET}"); return True
    except: return False


# ====== TOOL FUNCTIONS ======
def bootloader_unlock_tool():
    user = input(f"{BOLD}{ORANGE}👉{RESET} Mi Account Phone/Email: ").strip()
    if not user:
        user = "cbr_admin@system.local"
        print(f"{DIM}   Using Default Admin Profile: {user}{RESET}")
        
    account_pass = input(f"{BOLD}{ORANGE}👉{RESET} Enter Mi Account Password: ").strip()
    if not account_pass:
        print(f"\n{RED}[!] Password cannot be blank!{RESET}")
        return
        
    region = input(f"{BOLD}{ORANGE}👉{RESET} Enter Region (global/india/china) [global]: ").strip().lower()
    if not region:
        region = "global"

    print(f"\n{CYAN}[FASTBOOT]{RESET} Scanning active device connection status...")
    trigger_otg_popup()
    fb_bin = get_fastboot_bin()
    try: subprocess.run(f"{fb_bin} devices", shell=True, timeout=8)
    except: pass
    time.sleep(1)
    
    get_device_info()
    print(f"\n{GREEN}[LAUNCHING]{RESET} Running core CBR engine...\n")
    send_activity_log(f"Started Bootloader Unlock Tool (Target: {user}, Region: {region})")
    os.system(f'python -m miunlock --user {user} --pass {account_pass} --region {region}')

def cbr_wifi_setup():
    if IS_WINDOWS:
        print(f"\n{RED}[!] বস, CBR WIFI (Setup) শুধুমাত্র Termux (Mobile) এর জন্য! પিসিতে এটা দরকার নেই।{RESET}")
        return

    print(f"\n{CYAN}[SYSTEM]{RESET} Installing Required Termux Packages & Running CBR WIFI...")
    send_activity_log("Executed CBR WIFI Setup Tool")
    commands = [
        "apt update -y", "apt upgrade -y", "pkg install tsu -y", "pkg install git -y",
        "pkg install -y root-repo", "pkg install sudo -y", "pkg install python -y",
        "curl -sSf https://raw.githubusercontent.com/dark-s4b7z/SHADOW-ONESHOT/main/installer.sh | bash"
    ]
    for cmd in commands:
        print(f"\n{ORANGE}[RUNNING]{RESET} {cmd}")
        os.system(cmd)

def advance_abdullah_hasib_tool():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}    ⚡ ADVANCE ONLY CBR OWNER ABDULLAH AL HASIB ⚡    {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    
    if not verify_admin_access(): return
    print(f"\n{GREEN}[✓] Access Granted to CBR Owner!{RESET}")
    send_activity_log("Successfully Logged into Advance Owner Menu")
    
    ip_port = input(f"{BOLD}👉 Enter Device IP & Port (e.g., 192.168.1.5:45555): {RESET}")
    pair_code = input(f"{BOLD}👉 Enter 6-Digit Pairing Code: {RESET}")
    
    print(f"\n{ORANGE}[*] Pairing with device...{RESET}")
    os.system(f"adb pair {ip_port} {pair_code}")
    print(f"{ORANGE}[*] Connecting...{RESET}")
    os.system(f"adb connect {ip_port}")
    
    while True:
        print(f"\n{CYAN}--- ADVANCE OPTIONS ---{RESET}")
        print(f"{GREEN} [1]{RESET} Safe Debloat (No Bootloop)  {GREEN}[2]{RESET} Power Hosting")
        print(f"{GREEN} [3]{RESET} Remote Screen Capture       {GREEN}[4]{RESET} Advanced Power Menu")
        print(f"{RED} [5]{RESET} Back")
        opt = input(f"\n{BOLD}{ORANGE}👉 Select option: {RESET}").strip()
        
        if opt == '1':
            print(f"{GREEN} [1]{RESET} Auto Delete  {GREEN}[2]{RESET} Manual Paste")
            db_opt = input(f"{BOLD}{ORANGE}👉 Select: {RESET}")
            if db_opt == '1':
                safe_apps = ['com.google.android.youtube', 'com.facebook.services', 'com.facebook.appmanager', 'com.facebook.system', 'com.miui.analytics']
                for app in safe_apps: os.system(f"adb -s {ip_port} shell pm uninstall -k --user 0 {app}")
                print(f"{GREEN}[✓] Safe bloatware removed!{RESET}")
            elif db_opt == '2':
                pkg = input(f"{BOLD}👉 Paste Package Name: {RESET}").strip()
                os.system(f"adb -s {ip_port} shell pm uninstall -k --user 0 {pkg}")
                print(f"{GREEN}[✓] Package {pkg} removed!{RESET}")
        elif opt == '2':
            os.system(f"adb -s {ip_port} shell settings put global window_animation_scale 0.5")
            os.system(f"adb -s {ip_port} shell settings put global transition_animation_scale 0.5")
            os.system(f"adb -s {ip_port} shell settings put global animator_duration_scale 0.5")
            print(f"{GREEN}[✓] Boosted Successfully!{RESET}")
        elif opt == '3':
            os.system(f"adb -s {ip_port} shell screencap -p /sdcard/adv_cbr_sc.png")
            os.system(f"adb -s {ip_port} pull /sdcard/adv_cbr_sc.png ./")
            os.system(f"adb -s {ip_port} shell rm /sdcard/adv_cbr_sc.png")
            print(f"{GREEN}[✓] Screenshot saved!{RESET}")
        elif opt == '4':
            print(f"{GREEN}[1]{RESET} Fastboot {GREEN}[2]{RESET} Recovery {GREEN}[3]{RESET} EDL {GREEN}[4]{RESET} Power Off")
            rb_opt = input(f"{BOLD}{ORANGE}👉 Select mode: {RESET}")
            if rb_opt == '1': os.system(f"adb -s {ip_port} reboot bootloader")
            elif rb_opt == '2': os.system(f"adb -s {ip_port} reboot recovery")
            elif rb_opt == '3': os.system(f"adb -s {ip_port} reboot edl")
            elif rb_opt == '4': os.system(f"adb -s {ip_port} shell reboot -p")
        elif opt == '5': break

def admin_panel():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{RED}{BOLD}        🔐 ADMIN CONTROL DASHBOARD 🔐        {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    if not verify_admin_access(): return
    import requests
    base_url = "https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users"
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{CYAN}--- ADMIN PANEL ---{RESET}")
        print(f"{GREEN} [1]{RESET} Manage Users (Logs/Ban/Clear)")
        print(f"{ORANGE} [4]{RESET} 🔑 Change Tool Opening Password")
        print(f"{ORANGE} [5]{RESET} 🔑 Change Redmi Flash Password")
        print(f"{ORANGE} [6]{RESET} 🔑 Change Infinix Flash Password")
        print(f"{ORANGE} [7]{RESET} 🔑 Change BROM Access Password")
        print(f"{RED} [8]{RESET} 🔑 Change Admin/Owner Password")
        print(f"{RED} [0]{RESET} Back")
        
        admin_opt = input(f"\n{BOLD}{ORANGE}👉 Select Action: {RESET}").strip()
        if admin_opt == '0': break
        elif admin_opt in ['4', '5', '6', '7', '8']:
            key_map = {'4': 'tool_password', '5': 'flash_password', '6': 'infinix_password', '7': 'brom_password', '8': 'admin_password'}
            key_name = key_map[admin_opt]
            curr_pass = get_cloud_setting(key_name, 'Not Set')
            print(f"\n{DIM}Current: {curr_pass}{RESET}")
            new_pass = input(f"{BOLD}{ORANGE}👉 Enter New Password: {RESET}").strip()
            if new_pass:
                try: requests.patch(SETTINGS_URL, json={key_name: new_pass}, timeout=10); print(f"{GREEN}[✓] Updated!{RESET}")
                except Exception as e: print(f"{RED}[!] Error: {e}{RESET}")
            input(f"\n{PURPLE}Press Enter...{RESET}")
        elif admin_opt == '1':
            try:
                users_data = requests.get(f"{base_url}.json?auth={FIREBASE_SECRET}", timeout=10).json()
                if not users_data or "error" in users_data: continue
                email_list = []
                print(f"\n{CYAN}--- REGISTERED USERS ---{RESET}")
                for hwid, data in users_data.items():
                    if isinstance(data, dict):
                        email, device, status = data.get('email', '?'), data.get('device_name', '?'), data.get('status', 'Pending')
                        s_txt = f"{GREEN}{status}{RESET}" if status == 'Approved' else (f"{RED}{status}{RESET}" if status == 'Banned' else f"{ORANGE}{status}{RESET}")
                        print(f"{CYAN}[{len(email_list)+1}]{RESET} {email} | {DIM}{device}{RESET} | [{s_txt}]")
                        email_list.append((hwid, email))
                
                choice = int(input(f"\n{BOLD}{ORANGE}👉 Select User Number (0 to Back): {RESET}").strip())
                if choice == 0: continue
                hwid, eml = email_list[choice - 1]
                
                while True:
                    print(f"\n{CYAN}--- MANAGING: {eml} ---{RESET}")
                    print(f"{GREEN} [1]{RESET} Activity Logs  {GREEN}[2]{RESET} Clear Logs  {RED}[3]{RESET} Ban User  {ORANGE}[4]{RESET} Back")
                    act = input(f"\n{BOLD}{ORANGE}👉 Select: {RESET}").strip()
                    if act == '1':
                        logs = requests.get(f"{base_url}/{hwid}/activity_logs.json?auth={FIREBASE_SECRET}").json()
                        if logs: 
                            for t, m in sorted(logs.items()): print(f"{DIM}{m}{RESET}")
                        input(f"\n{PURPLE}Press Enter...{RESET}")
                    elif act == '2':
                        requests.delete(f"{base_url}/{hwid}/activity_logs.json?auth={FIREBASE_SECRET}")
                        print(f"{GREEN}[✓] Cleared!{RESET}"); time.sleep(1)
                    elif act == '3':
                        if input(f"{RED}BAN {eml}? (y/n): {RESET}").lower() == 'y':
                            requests.patch(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json={"status": "Banned", "password": "BANNED"})
                            break
                    elif act == '4': break
            except: pass

def admin_host_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{PURPLE}=================================================={RESET}")
        print(f"{HACKER_GREEN}{BOLD}       🛡️ ADMIN HOST MENU 🛡️       {RESET}")
        print(f"{PURPLE}=================================================={RESET}\n")
        print(f"{CYAN} [1]{RESET} ⚡ ADVANCE ONLY CBR OWNER ABDULLAH AL HASIB")
        print(f"{RED} [2]{RESET} 🔐 Admin Control Panel")
        print(f"{ORANGE} [0]{RESET} Back to Main Menu")
        
        opt = input(f"\n{BOLD}{ORANGE}👉 Select option: {RESET}").strip()
        if opt == '1': advance_abdullah_hasib_tool()
        elif opt == '2': admin_panel()
        elif opt == '0': break


# ====== FLASH ENGINE (FASTBOOT) ======
def cbr_smart_flasher(brand="redmi"):
    import requests
    if not IS_WINDOWS: os.system("termux-wake-lock > /dev/null 2>&1")
    os.system('cls' if os.name == 'nt' else 'clear')
    
    brand_name = "REDMI NATIVE" if brand == "redmi" else "INFINIX FASTBOOTD"
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}    🚀 CBR SMART {brand_name} FLASHER 🚀    {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    
    pass_key = 'flash_password' if brand == "redmi" else 'infinix_password'
    live_password = get_cloud_setting(pass_key, 'Powerbycbr' if brand=="redmi" else 'cbr')
    auth_pass = input(f"{BOLD}{ORANGE}🔑 Enter Authorization Password: {RESET}").strip()
    
    if auth_pass != live_password and auth_pass != f":{live_password}":
        print(f"\n{RED}[✗] Access Denied!{RESET}"); time.sleep(2); return
        
    print(f"{GREEN}[✓] Access Granted! Loading Engine...{RESET}"); time.sleep(1)

    all_roms = cbr_smart_scanner(mode="fastboot" if brand == "redmi" else "mtk")
    if not all_roms: return
        
    for i, file in enumerate(all_roms):
        print(f" [{i+1}] {'[DIR]' if os.path.isdir(file) else '[ZIP]'} {os.path.basename(file)}")
        
    try:
        sel = int(input(f"\n{BOLD}{ORANGE}👉 Select ROM number: {RESET}").strip())
        selected_rom = all_roms[sel-1]
    except: return

    extract_folder = selected_rom
    if not os.path.isdir(selected_rom):
        extract_folder = os.path.join(os.path.dirname(selected_rom), "CBR_Extracted_ROM")
        if not extract_safe_zip(selected_rom, extract_folder): return

    if brand == "redmi":
        sh_file = None
        for root, dirs, files in os.walk(extract_folder):
            for f in files:
                if (IS_WINDOWS and f.lower() == "flash_all.bat") or (not IS_WINDOWS and f.lower() == "flash_all.sh"):
                    sh_file = os.path.join(root, f); break
            if sh_file: break
        if not sh_file: print(f"{RED}[!] 'flash_all' script not found!{RESET}"); return
        
        print(f"\n{CYAN}[PRE-CHECK]{RESET} Verifying Connection...")
        if not get_device_info(): return
        
        print(f"\n{CYAN}--- FLASHING OPTIONS ---{RESET}")
        print(f"{GREEN} [1]{RESET} Flash All (Keep Unlocked)  {RED}[2]{RESET} Flash All & Lock")
        lock_choice = input(f"{BOLD}{ORANGE}👉 Select Option: {RESET}").strip()

        print(f"\n{HACKER_GREEN}[STARTING CBR FLASH ENGINE]{RESET}")
        fb_bin = get_fastboot_bin()
        with open(sh_file, 'r', encoding='utf-8', errors='ignore') as f: lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('rem') or line.startswith('echo'): continue
            if line.startswith('fastboot'):
                cmd = line.replace('`dirname $0`', os.path.dirname(sh_file)).replace('%~dp0', os.path.dirname(sh_file) + os.sep).replace('$*', '').replace('%*', '')
                if not IS_WINDOWS: cmd = cmd.replace('\\', '/')
                if fb_bin != "fastboot" and cmd.startswith("fastboot "): cmd = fb_bin + cmd[8:]
                
                print(f"\n{ORANGE}[RUNNING]{RESET} {cmd}")
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, errors='replace')
                for out_line in process.stdout: print(f"{DIM}   >> {out_line.strip()}{RESET}")
                process.wait()
                time.sleep(1)

        if lock_choice == '2': subprocess.run(f"{fb_bin} oem lock", shell=True)
        print(f"\n{GREEN}[✓] COMPLETED! Rebooting...{RESET}")
        subprocess.run(f"{fb_bin} reboot", shell=True)

    else:
        # INFINIX FASTBOOTD LOGIC
        scatter_found, scatter_full_path, rom_img_dir = None, None, None
        for root, dirs, files in os.walk(extract_folder):
            for f in files:
                if "scatter" in f.lower() and (f.endswith(".txt") or f.endswith(".xml")):
                    scatter_found, scatter_full_path, rom_img_dir = f, os.path.join(root, f), root
                    break
            if scatter_found: break
        if not rom_img_dir: print(f"{RED}[!] Scatter not found!{RESET}"); return

        scatter_ab_map, scatter_single_map, scatter_vbmeta_map = {}, {"super": "super.img", "userdata": "userdata.img"}, {}
        if scatter_full_path and os.path.exists(scatter_full_path):
            try:
                with open(scatter_full_path, 'r', encoding='utf-8', errors='ignore') as sf: content = sf.read()
                for blk in content.split("partition_index:")[1:]:
                    p_name_m = re.search(r"partition_name:\s*([^\s\r\n]+)", blk)
                    f_name_m = re.search(r"file_name:\s*([^\s\r\n]+)", blk)
                    if p_name_m and f_name_m:
                        p_name = p_name_m.group(1).strip().strip('"\'').lower()
                        f_name = f_name_m.group(1).strip().strip('"\'')
                        if f_name.lower() != "none":
                            base_p = p_name[:-2] if (p_name.endswith("_a") or p_name.endswith("_b")) else p_name
                            if base_p in ["super", "userdata"]: scatter_single_map[base_p] = f_name
                            elif base_p in ["vbmeta", "vbmeta_system", "vbmeta_vendor"]: scatter_vbmeta_map[base_p] = f_name
                            elif base_p not in ["preloader", "pgpt", "nvram", "nvdata"]: scatter_ab_map[base_p] = f_name
            except: pass

        if not get_device_info(): return
        
        def execute_cmd(cmd_str):
            fb_bin = get_fastboot_bin()
            if fb_bin != "fastboot" and cmd_str.startswith("fastboot "): cmd_str = fb_bin + cmd_str[8:]
            print(f"\n{ORANGE}[RUNNING]{RESET} {cmd_str}")
            p = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in p.stdout: print(f"{DIM}   >> {line.strip()}{RESET}")
            p.wait()

        print(f"\n{CYAN}>>> FASTBOOTD OPERATIONS <<<{RESET}")
        execute_cmd("fastboot reboot fastboot"); time.sleep(5)
        for part in ["product", "system", "system_ext", "product_a", "product_b"]: execute_cmd(f"fastboot delete-logical-partition {part}")
        execute_cmd(f'fastboot {"-S 64M " if not IS_WINDOWS else ""}flash super "{os.path.join(rom_img_dir, scatter_single_map.get("super", "super.img"))}"')
        execute_cmd("fastboot -w")
        
        print(f"\n{CYAN}>>> BOOTLOADER FLASHING <<<{RESET}")
        execute_cmd("fastboot reboot bootloader"); time.sleep(4)
        for b_part, f_name in scatter_ab_map.items():
            execute_cmd(f'fastboot flash {b_part}_a "{os.path.join(rom_img_dir, f_name)}"')
            execute_cmd(f'fastboot flash {b_part}_b "{os.path.join(rom_img_dir, f_name)}"')
        execute_cmd(f'fastboot flash userdata "{os.path.join(rom_img_dir, scatter_single_map.get("userdata", "userdata.img"))}"')
        
        print(f"\n{CYAN}>>> VBMETA DISABLE <<<{RESET}")
        for v_part, f_name in scatter_vbmeta_map.items():
            execute_cmd(f'fastboot --disable-verity --disable-verification flash {v_part}_a "{os.path.join(rom_img_dir, f_name)}"')
            execute_cmd(f'fastboot --disable-verity --disable-verification flash {v_part}_b "{os.path.join(rom_img_dir, f_name)}"')
            
        execute_cmd("fastboot reboot recovery")
        print(f"\n{GREEN}[✓] INFINIX FLASHING COMPLETED!{RESET}")

def fastboot_stock_rom_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{PURPLE}=================================================={RESET}")
        print(f"{HACKER_GREEN}{BOLD}    📱 FASTBOOT STOCK ROM FLASH (Mobile/PC) 📱    {RESET}")
        print(f"{PURPLE}=================================================={RESET}\n")
        print(f"{GREEN} [1]{RESET} Redmi ROM Flash (Native Engine)")
        print(f"{GREEN} [2]{RESET} Infinix Stock Flash (FastbootD Engine)")
        print(f"{ORANGE} [0]{RESET} Back to Main Menu")
        
        opt = input(f"\n{BOLD}{ORANGE}👉 Select option: {RESET}").strip()
        if opt == '1': cbr_smart_flasher(brand="redmi"); input(f"\n{PURPLE}Press Enter...{RESET}")
        elif opt == '2': cbr_smart_flasher(brand="infinix"); input(f"\n{PURPLE}Press Enter...{RESET}")
        elif opt == '0': break


# ====== BROM ENGINE (PC) ======
def verify_brom_auth():
    print(f"{CYAN}[SECURITY]{RESET} Connecting to Cloud Authorization...")
    live_password = get_cloud_setting('brom_password', 'OwnerHasib')
    auth_pass = input(f"{BOLD}{ORANGE}🔑 Enter BROM Access Password: {RESET}").strip()
    if auth_pass != live_password:
        print(f"\n{RED}[✗] Access Denied!{RESET}"); time.sleep(2); return False
    return True

def execute_mtk_cmd(cmd_list, work_dir):
    mtk_exe = shutil.which("mtk")
    if not mtk_exe and IS_WINDOWS: mtk_exe = os.path.join(os.path.dirname(sys.executable), "Scripts", "mtk.exe")
    if not mtk_exe or not os.path.exists(mtk_exe):
        print(f"{RED}[!] 'mtk' command not found!{RESET}"); return -1
    os.chdir(work_dir)
    real_cmd = [mtk_exe] + cmd_list
    if "w" in cmd_list or "da" in cmd_list: real_cmd.append("--brom-auto-reset")
    
    print(f"\n{CYAN}   >> Executing BROM Command...{RESET}\n{DIM}{'-'*50}{RESET}")
    try:
        process = subprocess.Popen(real_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, errors='replace')
        for line in process.stdout: print(f"      {DIM}{line.strip()}{RESET}")
        process.wait(); print(f"{DIM}{'-'*50}{RESET}")
        return process.returncode
    except Exception as e: print(f"{RED}      [!] Crash: {e}{RESET}\n{DIM}{'-'*50}{RESET}"); return -1

def cbr_brom_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{PURPLE}=================================================={RESET}")
        print(f"{HACKER_GREEN}{BOLD}         💻 PC BROM MODE FLASH (MTK) 💻         {RESET}")
        print(f"{PURPLE}=================================================={RESET}\n")
        print(f"{ORANGE} [1]{RESET} 🧪 Brom Mode Test Any")
        print(f"{ORANGE} [2]{RESET} 🪦 Only Dead -> Go Fastboot")
        print(f"{ORANGE} [3]{RESET} 🪦 Dead Go Fastboot Flash Combo")
        print(f"{HACKER_GREEN} [4]{RESET} {BOLD}BROM Full Flash (Redmi/Infinix){RESET}")
        print(f"{ORANGE} [0]{RESET} Back to Main Menu")
        
        opt = input(f"\n{BOLD}{ORANGE}👉 Select option: {RESET}").strip()
        if opt == '0': break
        elif opt in ['1', '2', '3', '4']:
            if not verify_brom_auth(): continue
            if opt == '1':
                if get_brom_device_info(): print(f"{GREEN}[✓] Successfully Brom mode connected & Auth Bypassed!{RESET}")
                input(f"\n{PURPLE}Press Enter...{RESET}")
            else:
                all_roms = cbr_smart_scanner(mode="mtk")
                if not all_roms: continue
                for i, file in enumerate(all_roms): print(f" [{i+1}] {'[DIR]' if os.path.isdir(file) else '[ZIP]'} {os.path.basename(file)}")
                try: selected_rom = all_roms[int(input(f"\n{BOLD}{ORANGE}👉 Select ROM number: {RESET}").strip())-1]
                except: continue

                extract_folder = selected_rom
                if not os.path.isdir(selected_rom):
                    extract_folder = os.path.join(os.path.dirname(selected_rom), "CBR_Extracted_MTK")
                    if not extract_safe_zip(selected_rom, extract_folder): continue

                scatter_path = None
                for root, dirs, files in os.walk(extract_folder):
                    for f in files:
                        if "scatter" in f.lower() and f.endswith(".txt"): scatter_path = os.path.join(root, f); break
                    if scatter_path: break
                if not scatter_path: print(f"{RED}[!] Scatter file not found!{RESET}"); input(); continue
                sc_dir = os.path.dirname(scatter_path)

                if not get_brom_device_info(): continue
                
                part_files, boot_chain = {}, ["preloader", "lk", "tee", "boot", "scp", "sspm", "md1img", "spmfw", "pi_img", "dtbo", "vbmeta"]
                try:
                    with open(scatter_path, 'r', encoding='utf-8', errors='ignore') as sf:
                        for blk in sf.read().split("partition_index:")[1:]:
                            p_name_m = re.search(r"partition_name:\s*([^\s\r\n]+)", blk)
                            f_name_m = re.search(r"file_name:\s*([^\s\r\n]+)", blk)
                            if p_name_m and f_name_m:
                                p = p_name_m.group(1).strip().strip('"\'').lower()
                                f = f_name_m.group(1).strip().strip('"\'')
                                if f.lower() != "none" and f.strip() and os.path.exists(os.path.join(sc_dir, f)):
                                    base_p = p[:-2] if (p.endswith("_a") or p.endswith("_b")) else p
                                    if opt == '4' or base_p in boot_chain or p == "preloader": part_files[p] = f
                except: pass
                
                if not part_files: print(f"{RED}[!] Valid files not found!{RESET}"); continue
                
                parts_to_write, files_to_write, preloader_file = [], [], ""
                for t, f_name in part_files.items():
                    parts_to_write.append(t); files_to_write.append(f_name)
                    if t in ["preloader", "preloader_a"]: preloader_file = f_name
                    
                cmd_args = ["w", ",".join(parts_to_write), ",".join(files_to_write)]
                if preloader_file: cmd_args.extend(["--preloader", preloader_file])
                
                if execute_mtk_cmd(cmd_args, sc_dir) == 0:
                    if opt == '3': 
                        print(f"{CYAN}[COMBO]{RESET} Handoff to Fastboot Engine!"); time.sleep(3)
                        cbr_smart_flasher(brand="infinix")
                    else:
                        execute_mtk_cmd(["reset"], sc_dir)
                        print(f"{GREEN}[✓] Magic Done! Phone Auto-Rebooting!{RESET}")
                else: print(f"{RED}   [!] FATAL ERROR during BROM flash.{RESET}")
                input(f"\n{PURPLE}Press Enter...{RESET}")


# ====== MAIN MENU ======
def main_menu():
    while True:
        premium_header()
        print(f"{CYAN} [1]{RESET} Bootloader Unlock")
        print(f"{CYAN} [2]{RESET} CBR WIFI (Setup) {DIM}{'[Termux Only]' if IS_WINDOWS else ''}{RESET}") 
        print(f"{RED} [3]{RESET} Admin Host {DIM}(Advance Owner & Panel){RESET}") 
        print(f"{GREEN} [4]{RESET} Fastboot Stock Rom Flash {DIM}(Mobile/PC Both){RESET}") 
        print(f"{HACKER_GREEN} [5]{RESET} {BOLD}PC BROM Mode Flash{RESET}")
        print(f"{CYAN} [0]{RESET} Exit")
        
        choice = input(f"\n{BOLD}{ORANGE}👉 Select option: {RESET}").strip()
        
        if choice == '1': bootloader_unlock_tool(); input(f"\n{PURPLE}Press Enter...{RESET}")
        elif choice == '2': cbr_wifi_setup()
        elif choice == '3': admin_host_menu()
        elif choice == '4': fastboot_stock_rom_menu()
        elif choice == '5': cbr_brom_menu()
        elif choice == '0': sys.exit(0)

def run_tool():
    try:
        check_dependencies()
        setup_otg_drivers()
        if not check_firebase_approval():
            input(f"\n{RED}Press Enter to exit...{RESET}")
            sys.exit(1)
        check_fastboot()
        main_menu()
    except Exception as fatal_err:
        print(f"\n{RED}[CRITICAL ERROR]: {str(fatal_err)}{RESET}")
        if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    run_tool()
