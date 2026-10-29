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

# উইন্ডোজ পিসির কনসোলকে ফোর্সফুলি UTF-8 এবং ANSI কালার মোডে নেওয়া
if IS_WINDOWS:
    os.system('chcp 65001 > nul')
    os.system('color')

# Colors
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

# 🛡 SUPER SECURE FIREBASE SECRET KEY 🛡️
FIREBASE_SECRET = "W2u5TaOnnVWpdOwkCSsLDPuUzrXnSiC0o7ngf7zJ"
SETTINGS_URL = f"https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Settings.json?auth={FIREBASE_SECRET}"
SESSION_FILE = os.path.expanduser("~/.cbr_session.json")

# 🔌 GLOBAL SMART OTG PORT TRACKERS 🔌
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

def create_cbrtool_shortcut():
    if not IS_WINDOWS:
        bin_dir = "/data/data/com.termux/files/usr/bin"
        shortcut_path = os.path.join(bin_dir, "cbrtool")
        script_path = os.path.abspath(__file__)
        if os.path.exists(bin_dir) and not os.path.exists(shortcut_path):
            try:
                with open(shortcut_path, "w") as f:
                    f.write(f"#!/bin/bash\npython3 '{script_path}' \"$@\"\n")
                os.chmod(shortcut_path, 0o755)
            except Exception:
                pass

def check_dependencies():
    create_cbrtool_shortcut()
    if not IS_WINDOWS:
        try:
            import ssl
        except ImportError:
            print(f"{ORANGE}[*] Repairing Termux SSL & OpenSSL modules... Please wait.{RESET}")
            os.system("pkg update -y && pkg install openssl ca-certificates python -y")
    
    try:
        import colorama, Cryptodome, miunlock, requests 
    except ImportError:
        print(f"{ORANGE}[*] Installing basic libraries...{RESET}")
        subprocess.call([sys.executable, "-m", "pip", "install", "colorama", "pycryptodomex", "miunlock", "requests"])

    # Auto GitHub Fallback Installer added for Termux Python 3.14
    if IS_WINDOWS:
        mtk_bin = shutil.which("mtk")
        if not mtk_bin:
            scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
            if not os.path.exists(os.path.join(scripts_dir, "mtk.exe")):
                print(f"{ORANGE}[*] High-Power Engine (mtkclient) missing! Forcing installation...{RESET}")
                subprocess.call([sys.executable, "-m", "pip", "install", "mtkclient"])
    else:
        try:
            import mtkclient
        except ImportError:
            print(f"{ORANGE}[*] High-Power Engine (mtkclient) missing! Forcing installation...{RESET}")
            res = subprocess.call([sys.executable, "-m", "pip", "install", "mtkclient"])
            if res != 0:
                print(f"{ORANGE}[*] Termux pip store failed. Forcing Direct GitHub Download...{RESET}")
                subprocess.call([sys.executable, "-m", "pip", "install", "https://github.com/bkerler/mtkclient/archive/main.zip"])

def setup_otg_drivers():
    if not IS_WINDOWS:
        try:
            if shutil.which("lsusb") is None:
                os.system("pkg install usbutils -y > /dev/null 2>&1")
            if not os.path.exists("/data/data/com.termux/files/usr/bin/termux-usb"):
                os.system("pkg install termux-api libusb -y > /dev/null 2>&1")
            if not os.path.exists("/data/data/com.termux/files/usr/bin/termux-fastboot"):
                os.system("curl -fsS https://raw.githubusercontent.com/nohajc/termux-adb/master/install.sh | bash > /dev/null 2>&1")
        except:
            pass

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
                            if dev in GRANTED_USB_DEVS and not force:
                                continue
                            if not silent:
                                print(f"{CYAN}[OTG]{RESET} Requesting USB Permission for {dev} (Tap 'OK/Allow' on popup)...")
                            req = subprocess.run(["termux-usb", "-r", dev], capture_output=True, text=True, timeout=12)
                            req_out = ((req.stdout or "") + (req.stderr or "")).lower()
                            if "granted" in req_out or "yes" in req_out or (req.returncode == 0 and "denied" not in req_out and "no" not in req_out):
                                GRANTED_USB_DEVS.add(dev)
                                ACTIVE_USB_DEV = dev
                                if not silent:
                                    print(f"{GREEN}[✓] OTG Permission Locked for {dev}!{RESET}")
                        time.sleep(0.8)
                        return True
                    else:
                        ACTIVE_USB_DEV = None
        except Exception:
            pass
    return False

def run_usb_fastboot_probe(fb_bin, args_list, timeout_sec=5):
    global ACTIVE_USB_DEV
    try:
        res = subprocess.run([fb_bin] + args_list, capture_output=True, text=True, timeout=timeout_sec)
        comb = ((res.stdout or "") + "\n" + (res.stderr or "")).strip()
        if comb and "waiting for" not in comb.lower() and "no permissions" not in comb.lower():
            return comb
    except Exception:
        pass

    if not IS_WINDOWS and ACTIVE_USB_DEV and shutil.which("termux-usb") is not None:
        for candidate_bin in [fb_bin, "fastboot", "termux-fastboot"]:
            if shutil.which(candidate_bin) is None:
                continue
            cmd_inner = f"{candidate_bin} {' '.join(args_list)}"
            try:
                res2 = subprocess.run(["termux-usb", "-e", cmd_inner, ACTIVE_USB_DEV], capture_output=True, text=True, timeout=timeout_sec)
                comb2 = ((res2.stdout or "") + "\n" + (res2.stderr or "")).strip()
                if comb2 and "waiting for" not in comb2.lower() and "no permissions" not in comb2.lower():
                    return comb2
            except Exception:
                pass
    return ""

def check_fastboot():
    if shutil.which("fastboot") is None and shutil.which("termux-fastboot") is None:
        print(f"{RED}[!] Fastboot is not installed or not in PATH!{RESET}")
        if not IS_WINDOWS:
            print(f"{ORANGE}[*] Auto-installing Android platform-tools (Fastboot/ADB)... Please wait.{RESET}")
            os.system("pkg update -y > /dev/null 2>&1")
            os.system("pkg install android-tools -y")
            time.sleep(2)
            if shutil.which("fastboot") is None and shutil.which("termux-fastboot") is None:
                print(f"{RED}[!] Auto-install failed! Please install manually: pkg install android-tools{RESET}")
                sys.exit(1)
            else:
                print(f"{GREEN}[✓] Android platform-tools installed successfully!{RESET}")
        else:
            print(f"{RED}[!] On Windows, please install minimal ADB & Fastboot manually.{RESET}")
            sys.exit(1)

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
                serial_id = first_line.split()[0].strip()
                product_name = serial_id
                prod_out = run_usb_fastboot_probe(fb_bin, ["getvar", "product"], timeout_sec=3)
                if "product:" in prod_out:
                    p_val = prod_out.split("product:")[1].split()[0].strip()
                    if p_val:
                        product_name = p_val
                print(f"{GREEN}[✓] Connected Device: {product_name}{RESET}")
                return product_name

        for var_name in ["product", "is-userspace", "serialno", "version"]:
            var_out = run_usb_fastboot_probe(fb_bin, ["getvar", var_name], timeout_sec=4)
            if f"{var_name}:" in var_out.lower() or "okay" in var_out.lower() or "finished" in var_out.lower():
                if "product:" in var_out:
                    p_val = var_out.split("product:")[1].split()[0].strip()
                    if p_val:
                        print(f"{GREEN}[✓] Connected Device: {p_val}{RESET}")
                        return p_val
                dev_label = f"Fastboot-Device ({ACTIVE_USB_DEV})" if ACTIVE_USB_DEV else "Fastboot-Device"
                print(f"{GREEN}[✓] Connected Device: {dev_label}{RESET}")
                return dev_label

        if not IS_WINDOWS and ACTIVE_USB_DEV and ACTIVE_USB_DEV in GRANTED_USB_DEVS:
            print(f"{GREEN}[✓] OTG Port Active & Authorized: {ACTIVE_USB_DEV} (Infinix/MTK Direct Mode){RESET}")
            return f"OTG-{os.path.basename(ACTIVE_USB_DEV)}"

        if IS_WINDOWS:
            print(f"{ORANGE}[!] Waiting for Device Connection... ({attempt+1}/5){RESET}")
        else:
            print(f"{ORANGE}[!] Waiting for OTG Allow Popup... Please tap 'Allow/OK' on screen! ({attempt+1}/5){RESET}")
        time.sleep(2)
            
    print(f"{ORANGE}[!] Could not read device product name. Check USB cable & Fastboot mode.{RESET}")
    return None

def get_brom_device_info():
    global ACTIVE_USB_DEV, GRANTED_USB_DEVS
    print(f"{CYAN}[BROM-SCAN]{RESET} Waiting for MTK BROM Connection...")
    print(f"{ORANGE}[*] Please turn OFF phone. Hold VOLUME UP + DOWN and connect USB cable!{RESET}")
    print(f"{DIM}    (Infinite Ninja Scanner active for 60 seconds. You have plenty of time!){RESET}")
    
    end_time = time.time() + 60
    
    if IS_WINDOWS:
        while time.time() < end_time:
            try:
                res = subprocess.run("wmic path Win32_PnPEntity get Caption,DeviceID", shell=True, capture_output=True, text=True, creationflags=0x08000000 if sys.platform == "win32" else 0)
                if "VID_0E8D" in res.stdout.upper() or "MediaTek" in res.stdout:
                    print(f"\n{GREEN}[✓] MediaTek BROM Port Detected (PC/COM)!{RESET}")
                    return True
            except Exception:
                pass
            rem_time = int(end_time - time.time())
            sys.stdout.write(f"\r\033[K{ORANGE}>> Windows Fast Polling for BROM Port... ({rem_time}s remaining){RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
    else:
        while time.time() < end_time:
            if shutil.which("termux-usb") is not None:
                try:
                    res = subprocess.run(["termux-usb", "-l"], capture_output=True, text=True, timeout=0.5)
                    if res.stdout and res.stdout.strip():
                        usb_devs = json.loads(res.stdout.strip())
                        if isinstance(usb_devs, list) and len(usb_devs) > 0:
                            ACTIVE_USB_DEV = usb_devs[-1]
                            print(f"\n{GREEN}[✓] Device Detected in BROM Mode ({ACTIVE_USB_DEV})!{RESET}")
                            req = subprocess.run(["termux-usb", "-r", ACTIVE_USB_DEV], capture_output=True, text=True, timeout=3)
                            req_out = ((req.stdout or "") + (req.stderr or "")).lower()
                            if "granted" in req_out or "yes" in req_out or req.returncode == 0:
                                GRANTED_USB_DEVS.add(ACTIVE_USB_DEV)
                                print(f"{GREEN}[✓] BROM Auth Bypassed & Port Locked!{RESET}")
                                return True
                except subprocess.TimeoutExpired:
                    pass
                except Exception:
                    pass
            rem_time = int(end_time - time.time())
            sys.stdout.write(f"\r\033[K{ORANGE}>> Ninja Polling for BROM Port... ({rem_time}s remaining){RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
        
    print(f"\n{RED}[!] Failed to catch BROM port within 60 seconds. Try again.{RESET}")
    return False

def authenticate():
    premium_header()
    print(f"{ORANGE}[SECURITY]{RESET} Protected under CBR verification protocols.")
    live_tool_pass = get_cloud_setting('tool_password', None)
    
    try:
        user_pass = input(f"{BOLD}🔑 Enter Security Token Password: {RESET}").strip()
        hashed_input = hashlib.sha256(user_pass.encode()).hexdigest()
        
        if (live_tool_pass and user_pass == live_tool_pass) or hashed_input == SECURE_PASSWORD_HASH:
            print(f"\n{GREEN}[✓] Access Granted! Authenticating cryptographic pipeline...{RESET}")
            time.sleep(1)
            return True
        else:
            print(f"\n{RED}[✗] Access Denied: Incorrect Security Token Password!{RESET}")
            return False
    except Exception as e:
        print(f"\n{RED}[!] Auth Error: {str(e)}{RESET}")
        return False

def verify_admin_access():
    live_admin_pass = get_cloud_setting('admin_password', None)
    admin_pass = input(f"{BOLD}{ORANGE}🔑 Enter Admin/Owner Password: {RESET}").strip()
    
    if (live_admin_pass and admin_pass == live_admin_pass) or hashlib.sha256(admin_pass.encode()).hexdigest() == ADVANCE_PASSWORD_HASH:
        return True
    print(f"\n{RED}[✗] Access Denied: Unauthorized Attempt! Intruders will be tracked.{RESET}")
    time.sleep(2)
    return False

def ping_server_and_check_ban(hwid):
    import requests
    db_url = f"https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users/{hwid}.json?auth={FIREBASE_SECRET}"
    while True:
        try:
            res = requests.get(db_url).json()
            if isinstance(res, dict) and res.get("status") == "Banned":
                print(f"\n\n{RED}{BOLD}admin ban you not use this tool 💥 admin ban korse Abdullah Al Hasib{RESET}")
                os._exit(1) 
            requests.patch(db_url, json={"last_ping": int(time.time())})
        except:
            pass
        time.sleep(10) 

def start_online_ping(hwid):
    t = threading.Thread(target=ping_server_and_check_ban, args=(hwid,), daemon=True)
    t.start()

def check_firebase_approval():
    import requests
    raw_id = platform.node() + str(uuid.getnode())
    hwid = hashlib.md5(raw_id.encode()).hexdigest()[:15].upper()
    
    try:
        brand = subprocess.getoutput('getprop ro.product.brand').strip().capitalize()
        model = subprocess.getoutput('getprop ro.product.model').strip()
        device_name = f"{brand} {model}".strip()
        if not device_name or "command not found" in device_name.lower():
            device_name = platform.node()
    except:
        device_name = platform.node()
        
    base_url = "https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users"

    if not IS_WINDOWS and os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
                if session_data.get("hwid") == hwid:
                    print(f"\n{GREEN}[✓] Auto-Login Successful! Welcome back.{RESET}")
                    start_online_ping(hwid)
                    return True
        except:
            pass

    print(f"\n{CYAN}[USER LOGIN]{RESET} Please login to your account.")
    user_email = input(f"{BOLD}{ORANGE}📧 Enter Your Email: {RESET}").strip()
    user_password = input(f"{BOLD}{ORANGE}🔑 Enter Your Password: {RESET}").strip()
    
    if not user_email or not user_password:
        print(f"{RED}[!] Email and Password cannot be empty!{RESET}")
        return False
    
    print(f"\n{CYAN}[SYSTEM]{RESET} Your Hardware ID: {BOLD}{ORANGE}{hwid}{RESET}")
    print(f"{CYAN}[DEVICE]{RESET} {device_name}")
    
    try:
        response = requests.get(f"{base_url}.json?auth={FIREBASE_SECRET}", timeout=10)
        all_users = response.json()
        
        if isinstance(all_users, dict) and "error" in all_users:
            print(f"\n{RED}[!] Firebase Database Blocked: {all_users['error']}{RESET}")
            return False

        if all_users is None:
            all_users = {}
            
        existing_hwid = None
        db_status = "Pending"
        
        for db_id, data in all_users.items():
            if isinstance(data, dict):
                if data.get("email") == user_email:
                    existing_hwid = db_id
                    if data.get("password") != user_password:
                        print(f"\n{RED}[✗] Invalid Password for this Email!{RESET}")
                        return False
                    db_status = data.get("status", "Pending")
                    break

        if existing_hwid:
            if db_status in ["Approved", "VIP"]:
                print(f"\n{GREEN}[✓] Login Successful! Welcome back. Approved by Cbr tool owner Abdullah Al Hasib{RESET}")
                time.sleep(1.5)
                
                payload = all_users[existing_hwid]
                payload["device_name"] = device_name 
                payload["last_ping"] = int(time.time())
                
                if existing_hwid != hwid:
                    payload["hwid"] = hwid
                    requests.put(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json=payload)
                    requests.delete(f"{base_url}/{existing_hwid}.json?auth={FIREBASE_SECRET}")
                else:
                    requests.patch(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json={"device_name": device_name, "last_ping": int(time.time())})
                    
                if not IS_WINDOWS:
                    with open(SESSION_FILE, "w") as f:
                        json.dump({"hwid": hwid, "email": user_email}, f)
                    
                start_online_ping(hwid)
                send_activity_log("User Logged In Successfully")
                return True
            elif db_status == "Banned":
                print(f"\n{RED}{BOLD}admin ban you not use this tool 💥 admin ban korse Abdullah Al Hasib{RESET}")
                return False
        else:
            payload = {
                "status": "Pending", 
                "hwid": hwid, 
                "email": user_email, 
                "password": user_password,
                "device_name": device_name,
                "last_ping": int(time.time())
            }
            requests.put(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json=payload)
            existing_hwid = hwid
            send_activity_log("New Registration Created - Pending Approval")

        is_waiting_printed = False
        db_url = f"{base_url}/{existing_hwid}.json?auth={FIREBASE_SECRET}"
        
        while True:
            resp = requests.get(db_url, timeout=10)
            data = resp.json()
            if not data:
                time.sleep(3)
                continue
                
            status = data.get("status", "Pending")
            
            if status == "Approved" or status == "VIP":
                print(f"\n{GREEN}[✓] Login Successful! Approved by Cbr tool owner Abdullah Al Hasib{RESET}")
                time.sleep(1.5)
                
                payload = data
                payload["device_name"] = device_name
                if existing_hwid != hwid:
                    payload["hwid"] = hwid
                    requests.put(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json=payload)
                    requests.delete(f"{base_url}/{existing_hwid}.json?auth={FIREBASE_SECRET}")
                else:
                    requests.patch(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json={"device_name": device_name})
                    
                if not IS_WINDOWS:
                    with open(SESSION_FILE, "w") as f:
                        json.dump({"hwid": hwid, "email": user_email}, f)
                    
                start_online_ping(hwid) 
                send_activity_log("User Approved and Logged In")
                return True
            elif status == "Banned":
                print(f"\n{RED}{BOLD}admin ban you not use this tool 💥 admin ban korse Abdullah Al Hasib{RESET}")
                return False
            else:
                if not is_waiting_printed:
                    print(f"{CYAN}[SYSTEM]{RESET} Waiting for Admin Approval", end="", flush=True)
                    is_waiting_printed = True
                print(".", end="", flush=True)
                time.sleep(3) 
            
    except Exception as e:
        print(f"\n{RED}[!] Server connection failed! Please check your internet.{RESET}")
        return False

def show_welcome_screen():
    premium_header()

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
    try:
        subprocess.run(f"{fb_bin} devices", shell=True, timeout=8)
    except Exception:
        pass
    time.sleep(1)
    
    get_device_info()
    
    print(f"\n{GREEN}[LAUNCHING]{RESET} Running core CBR engine...\n")
    send_activity_log(f"Started Bootloader Unlock Tool (Target: {user}, Region: {region})")
    cmd = f'python -m miunlock --user {user} --pass {account_pass} --region {region}'
    os.system(cmd)

def advance_abdullah_hasib_tool():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}    ⚡ ADVANCE ONLY CBR OWNER ABDULLAH AL HASIB ⚡    {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    
    if not verify_admin_access(): return
        
    print(f"\n{GREEN}[✓] Access Granted to CBR Owner Abdullah Al Hasib!{RESET}")
    send_activity_log("Successfully Logged into Advance Owner Menu")
    print(f"\n{CYAN}[WIRELESS ADB SETUP]{RESET}")
    
    ip_port = input(f"{BOLD}👉 Enter Device IP & Port (e.g., 192.168.1.5:45555): {RESET}")
    pair_code = input(f"{BOLD}👉 Enter 6-Digit Pairing Code: {RESET}")
    
    print(f"\n{ORANGE}[*] Pairing with device...{RESET}")
    os.system(f"adb pair {ip_port} {pair_code}")
    print(f"{ORANGE}[*] Connecting...{RESET}")
    os.system(f"adb connect {ip_port}")
    send_activity_log(f"Attempted Wireless ADB Connection to {ip_port}")
    
    while True:
        print(f"\n{CYAN}--- ADVANCE OPTIONS ---{RESET}")
        print(f"{GREEN} [1]{RESET} Safe Debloat (No Bootloop)")
        print(f"{GREEN} [2]{RESET} Power Hosting (Performance Booster)")
        print(f"{GREEN} [3]{RESET} Remote Screen Capture")
        print(f"{GREEN} [4]{RESET} Advanced Power Menu")
        print(f"{RED} [5]{RESET} Back to Main Menu")
        
        opt = input(f"\n{BOLD}{ORANGE}👉 Select an option: {RESET}").strip()
        
        if opt == '1':
            print(f"\n{CYAN}--- SAFE DEBLOAT (No Bootloop) ---{RESET}")
            print(f"{DIM}Safe apps to delete: com.google.android.youtube, com.facebook.services, com.facebook.appmanager, com.facebook.system, com.miui.analytics, etc.{RESET}")
            print(f"{GREEN} [1]{RESET} Delete all safe bloatware automatically")
            print(f"{GREEN} [2]{RESET} Paste Package Name manually")
            print(f"{RED} [3]{RESET} Back")
            db_opt = input(f"\n{BOLD}{ORANGE}👉 Select: {RESET}")
            
            if db_opt == '1':
                send_activity_log("Executed Safe Debloat (Deleted Auto Apps)")
                safe_apps = ['com.google.android.youtube', 'com.facebook.services', 'com.facebook.appmanager', 'com.facebook.system', 'com.miui.analytics']
                for app in safe_apps:
                    os.system(f"adb -s {ip_port} shell pm uninstall -k --user 0 {app}")
                print(f"{GREEN}\n[✓] All safe bloatware removed successfully!{RESET}")
            elif db_opt == '2':
                pkg = input(f"{BOLD}👉 Paste Package Name: {RESET}").strip()
                send_activity_log(f"Executed Manual Debloat on Package: {pkg}")
                os.system(f"adb -s {ip_port} shell pm uninstall -k --user 0 {pkg}")
                print(f"{GREEN}\n[✓] Package {pkg} removed successfully!{RESET}")
                
        elif opt == '2':
            send_activity_log("Injected Power Hosting & Speed Tweaks")
            print(f"\n{CYAN}[POWER HOSTING]{RESET} Injecting performance tweaks...")
            os.system(f"adb -s {ip_port} shell settings put global window_animation_scale 0.5")
            os.system(f"adb -s {ip_port} shell settings put global transition_animation_scale 0.5")
            os.system(f"adb -s {ip_port} shell settings put global animator_duration_scale 0.5")
            print(f"{GREEN}[✓] Performance & Speed Boosted Successfully!{RESET}")
            
        elif opt == '3':
            send_activity_log("Used Remote Screen Capture Feature")
            print(f"\n{CYAN}[SCREEN CAPTURE]{RESET} Taking remote screenshot...")
            os.system(f"adb -s {ip_port} shell screencap -p /sdcard/adv_cbr_sc.png")
            os.system(f"adb -s {ip_port} pull /sdcard/adv_cbr_sc.png ./")
            os.system(f"adb -s {ip_port} shell rm /sdcard/adv_cbr_sc.png")
            print(f"{GREEN}[✓] Screenshot captured and saved to current directory!{RESET}")
            
        elif opt == '4':
            print(f"\n{CYAN}--- ADVANCED POWER MENU ---{RESET}")
            print(f"{GREEN} [1]{RESET} Fastboot  {GREEN}[2]{RESET} Recovery  {GREEN}[3]{RESET} EDL  {GREEN}[4]{RESET} Power Off  {RED}[5]{RESET} Back")
            rb_opt = input(f"\n{BOLD}{ORANGE}👉 Select mode: {RESET}")
            
            if rb_opt == '1': 
                send_activity_log("Sent Reboot to Fastboot Command")
                os.system(f"adb -s {ip_port} reboot bootloader")
                print(f"{GREEN}[*] Rebooting to Fastboot...{RESET}")
            elif rb_opt == '2': 
                send_activity_log("Sent Reboot to Recovery Command")
                os.system(f"adb -s {ip_port} reboot recovery")
                print(f"{GREEN}[*] Rebooting to Recovery...{RESET}")
            elif rb_opt == '3': 
                send_activity_log("Sent Reboot to EDL Command")
                os.system(f"adb -s {ip_port} reboot edl")
                print(f"{GREEN}[*] Rebooting to EDL...{RESET}")
            elif rb_opt == '4': 
                send_activity_log("Sent Remote Power Off Command")
                os.system(f"adb -s {ip_port} shell reboot -p")
                print(f"{GREEN}[*] Powering Off...{RESET}")
                
        elif opt == '5':
            send_activity_log("Exited Advance Owner Menu")
            break
        else:
            print(f"{RED}Invalid Option!{RESET}")

# ==========================================
# 🚀 SMART FLASHER ENGINE
# ==========================================
def cbr_smart_flasher():
    import requests
    if not IS_WINDOWS:
        os.system("termux-wake-lock > /dev/null 2>&1")
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}    🚀 CBR SMART REDMI FLASHER (OTG SAFE) 🚀    {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    
    print(f"{CYAN}[SECURITY]{RESET} Connecting to Cloud Authorization...")
    live_password = get_cloud_setting('flash_password', 'Powerbycbr')
        
    auth_pass = input(f"{BOLD}{ORANGE}🔑 Enter Flash Authorization Password: {RESET}").strip()
    if auth_pass != live_password:
        print(f"\n{RED}[✗] Access Denied: Incorrect Authorization Password!{RESET}")
        send_activity_log("Failed Flash Attempt: Wrong Auth Password")
        time.sleep(2)
        if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")
        return
        
    print(f"{GREEN}[✓] Access Granted! Loading CBR Flasher Engine...{RESET}")
    if IS_WINDOWS:
        print(f"{CYAN}[SYSTEM]{RESET} Verifying PC Fastboot Core Drivers... {GREEN}OK!{RESET}")
    else:
        print(f"{CYAN}[SYSTEM]{RESET} Verifying MiTool Core Drivers (OTG/API)... {GREEN}OK!{RESET}")
        print(f"{CYAN}[SHIELD]{RESET} Termux Wake-Lock Enabled. Device won't sleep! {GREEN}OK!{RESET}")
    send_activity_log("Opened CBR Smart Flasher Engine")
    time.sleep(1)

    rom_dir = "/sdcard/Download" if not IS_WINDOWS else os.path.expanduser("~\\Downloads")
    all_roms = cbr_smart_scanner(mode="fastboot")
    if not all_roms: return
        
    for i, file in enumerate(all_roms):
        print(f" [{i+1}] {'[DIR]' if os.path.isdir(file) else '[ZIP]'} {os.path.basename(file)}")
        
    try:
        sel = int(input(f"\n{BOLD}{ORANGE}👉 Select ROM number to Extract/Flash: {RESET}").strip())
        selected_rom = all_roms[sel-1]
    except (ValueError, IndexError):
        print(f"{RED}[!] Invalid selection.{RESET}")
        if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")
        return

    extract_folder = selected_rom
    if not os.path.isdir(selected_rom):
        extract_folder = os.path.join(rom_dir, "CBR_Extracted_ROM")
        if not extract_safe_zip(selected_rom, extract_folder): return

    sh_file = None
    for root, dirs, files in os.walk(extract_folder):
        for f in files:
            if IS_WINDOWS and f.lower() == "flash_all.bat": sh_file = os.path.join(root, f)
            elif not IS_WINDOWS and f.lower() == "flash_all.sh": sh_file = os.path.join(root, f)
        if not sh_file:
            for f in files:
                if f.lower() == "flash_all.sh" or f.lower() == "flash_all.bat":
                    sh_file = os.path.join(root, f)
        if sh_file: break
            
    if not sh_file:
        print(f"{RED}[!] Error: 'flash_all' script not found in extracted files! Invalid ROM.{RESET}")
        if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")
        return

    script_dir = os.path.dirname(sh_file)
    
    print(f"\n{CYAN}[PRE-CHECK]{RESET} Verifying Device Connection...")
    connected_device = get_device_info()
    if not connected_device:
        print(f"{RED}[!] Phone not found in fastboot.{RESET}")
        if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")
        return
        
    print(f"\n{CYAN}--- FLASHING OPTIONS ---{RESET}")
    print(f"{GREEN} [1]{RESET} Flash All (Keep Bootloader Unlocked)")
    print(f"{RED} [2]{RESET} Flash All & Lock (Lock Bootloader)")
    lock_choice = input(f"\n{BOLD}{ORANGE}👉 Select Option: {RESET}").strip()

    print(f"\n{HACKER_GREEN}[STARTING CBR FLASH ENGINE]{RESET}")
    send_activity_log(f"Started Flashing ROM: {os.path.basename(selected_rom)}")
    
    with open(sh_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    fb_bin = get_fastboot_bin()

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('rem') or line.startswith('echo'):
            continue

        if line.startswith('fastboot'):
            cmd = line.replace('`dirname $0`', script_dir).replace('%~dp0', script_dir + os.sep)
            cmd = cmd.replace('$*', '').replace('%*', '')
            if not IS_WINDOWS: cmd = cmd.replace('\\', '/')
            
            is_valid_action = False
            valid_keywords = ['flash', 'erase', 'format', 'boot', 'reboot', 'oem', 'set_active']
            cmd_parts = [p.lower() for p in cmd.split() if p.lower() != 'fastboot' and not p.startswith('-')]
            
            if cmd_parts:
                action = cmd_parts[0]
                if any(action.startswith(vk) for vk in valid_keywords) and '|' not in cmd and '>' not in cmd and 'grep' not in cmd:
                    is_valid_action = True
                    
            if not is_valid_action:
                continue
            
            if fb_bin != "fastboot" and cmd.startswith("fastboot "):
                cmd = fb_bin + cmd[8:]
            
            success = False
            for attempt in range(3):
                print(f"\n{ORANGE}[RUNNING]{RESET} {cmd}")
                
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, errors='replace')
                for out_line in process.stdout:
                    print(f"{DIM}   >> {out_line.strip()}{RESET}")
                process.wait()
                
                if process.returncode == 0:
                    success = True
                    break
                else:
                    print(f"{RED}[!] Failed. Retry ({attempt+1}/3)...{RESET}")
                    if not IS_WINDOWS: trigger_otg_popup(force=True)
                    time.sleep(3)
                    
            if not success:
                print(f"{RED}[!] Skipping partition after 3 failures to prevent brick.{RESET}")
                
            time.sleep(2) 
            try:
                subprocess.run(f"{fb_bin} devices > /dev/null 2>&1", shell=True, timeout=4)
            except Exception:
                pass

    if lock_choice == '2':
        print(f"\n{ORANGE}[LOCKING BOOTLOADER]{RESET}")
        subprocess.run(f"{fb_bin} oem lock", shell=True)
        
    print(f"\n{GREEN}[✓] FLASHING COMPLETED SUCCESSFULLY!{RESET}")
    print(f"{CYAN}[*] Rebooting Phone...{RESET}")
    subprocess.run(f"{fb_bin} reboot", shell=True)
    send_activity_log("Successfully Completed ROM Flashing")
    if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")

def cbr_infinix_flasher():
    global ACTIVE_USB_DEV, GRANTED_USB_DEVS
    import requests
    if not IS_WINDOWS: os.system("termux-wake-lock > /dev/null 2>&1")
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}   🚀 CBR INFINIX STOCK ROM FLASHER (FASTBOOTD) 🚀   {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    
    print(f"{CYAN}[SECURITY]{RESET} Connecting to Cloud Authorization...")
    live_password = get_cloud_setting('infinix_password', 'cbr')
        
    auth_pass = input(f"{BOLD}{ORANGE}🔑 Enter Infinix Flash Authorization Password: {RESET}").strip()
    if auth_pass != live_password and auth_pass != f":{live_password}":
        print(f"\n{RED}[✗] Access Denied: Incorrect Authorization Password!{RESET}")
        send_activity_log("Failed Infinix Flash Attempt: Wrong Auth Password")
        time.sleep(2)
        if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")
        return
        
    print(f"{GREEN}[✓] Access Granted! Loading CBR Infinix Flasher Engine...{RESET}")
    time.sleep(1)

    rom_dir = "/sdcard/Download" if not IS_WINDOWS else os.path.expanduser("~\\Downloads")
    all_roms = cbr_smart_scanner(mode="mtk")
    if not all_roms: return
        
    for i, file in enumerate(all_roms):
        print(f" [{i+1}] {'[DIR]' if os.path.isdir(file) else '[ZIP]'} {os.path.basename(file)}")
        
    try:
        sel = int(input(f"\n{BOLD}{ORANGE}👉 Select ROM number to Extract/Flash: {RESET}").strip())
        selected_rom = all_roms[sel-1]
    except (ValueError, IndexError):
        print(f"{RED}[!] Invalid selection.{RESET}")
        if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")
        return

    extract_folder = selected_rom
    if not os.path.isdir(selected_rom):
        extract_folder = os.path.join(rom_dir, "CBR_Extracted_Infinix_ROM")
        if not extract_safe_zip(selected_rom, extract_folder): return

    scatter_found = None
    scatter_full_path = None
    rom_img_dir = None
    for root, dirs, files in os.walk(extract_folder):
        for f in files:
            if "scatter" in f.lower() and (f.endswith(".txt") or f.endswith(".xml")):
                scatter_found = f
                scatter_full_path = os.path.join(root, f)
                rom_img_dir = root
                break
        if scatter_found: break

    if not rom_img_dir:
        print(f"{RED}[!] Error: Scatter file not found in ROM folder!{RESET}")
        if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")
        return

    print(f"{GREEN}[✓] Detected Scatter File: {scatter_found}{RESET}")
    print(f"{CYAN}[✓] ROM Image Directory Ready: {rom_img_dir}{RESET}")

    risky_blacklist = {
        "preloader", "preloader_a", "preloader_b", "preloader_raw", "preloader_emmc", "preloader_ufs",
        "pgpt", "gpt", "sgpt", "nvram", "nvdata", "nvcfg", "protect1", "protect2",
        "persist", "seccfg", "proinfo", "sec1", "efuse", "otp", "bmtpool",
        "boot_para", "para", "expdb", "frp", "metadata", "flashinfo", " keystore", " Russ"
    }
    vbmeta_base_names = {"vbmeta", "vbmeta_system", "vbmeta_vendor"}
    baseline_ab_partitions = [("boot", "boot.img"), ("init_boot", "init_boot.img"), ("dtbo", "dtbo.img"), ("gz", "gz.img"), ("lk", "lk.img"), ("md1img", "md1img.img"), ("scp", "scp.img"), ("spmfw", "spmfw.img"), ("sspm", "sspm.img"), ("tee", "tee.img")]

    scatter_ab_map = {}
    scatter_single_map = {"super": "super.img", "userdata": "userdata.img"}
    scatter_vbmeta_map = {"vbmeta": "vbmeta.img", "vbmeta_system": "vbmeta_system.img", "vbmeta_vendor": "vbmeta_vendor.img"}
    for b_part, b_file in baseline_ab_partitions: scatter_ab_map[b_part] = b_file

    if scatter_full_path and os.path.exists(scatter_full_path):
        print(f"\n{CYAN}[SCATTER PARSER]{RESET} Analyzing {scatter_found} for safe partitions...")
        try:
            with open(scatter_full_path, 'r', encoding='utf-8', errors='ignore') as sf: content = sf.read()
            parsed_entries = []
            if scatter_full_path.endswith(".txt"):
                for blk in content.split("partition_index:")[1:]:
                    p_name_m = re.search(r"partition_name:\s*([^\s\r\n]+)", blk)
                    f_name_m = re.search(r"file_name:\s*([^\s\r\n]+)", blk)
                    is_dl_m = re.search(r"is_download:\s*([^\s\r\n]+)", blk)
                    if p_name_m and f_name_m:
                        p_name = p_name_m.group(1).strip().strip('"\'')
                        f_name = f_name_m.group(1).strip().strip('"\'')
                        is_dl = is_dl_m.group(1).strip().lower() if is_dl_m else "true"
                        if is_dl == "true" and f_name.lower() != "none": parsed_entries.append((p_name, f_name))
            elif scatter_full_path.endswith(".xml"):
                for m in re.finditer(r'partition_name="([^"]+)"[^>]*file_name="([^"]+)"', content):
                    p_name, f_name = m.group(1).strip(), m.group(2).strip()
                    if f_name.lower() != "none": parsed_entries.append((p_name, f_name))

            for p_name, f_name in parsed_entries:
                p_low = p_name.lower()
                base_p = p_low[:-2] if (p_low.endswith("_a") or p_low.endswith("_b")) else p_low
                if p_low in risky_blacklist or base_p in risky_blacklist or "preloader" in p_low: continue
                if base_p in vbmeta_base_names or p_low.startswith("vbmeta"): scatter_vbmeta_map[base_p] = f_name
                elif base_p in ("super", "userdata"): scatter_single_map[base_p] = f_name
                else: scatter_ab_map[base_p] = f_name
        except Exception as e:
            print(f"{ORANGE}[!] Scatter parse notice: {e}{RESET}")

    print(f"\n{CYAN}[PRE-CHECK]{RESET} Checking Fastboot / FastbootD Device Connection...")
    connected_device = get_device_info()
    if not connected_device:
        print(f"{RED}[!] Phone not detected! Please connect via OTG.{RESET}")
        if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")
        return

    fb_bin = get_fastboot_bin()
    total_flash_steps = 12 + (len(scatter_ab_map) * 2) + 1 + (len(scatter_vbmeta_map) * 2) + 1
    current_flash_step = 0
    user_aborted_flash = False

    def get_progress_pct():
        pct = int((current_flash_step / max(1, total_flash_steps)) * 100)
        return min(99, max(1, pct))

    def wait_for_fastboot_device(mode_label):
        nonlocal fb_bin, user_aborted_flash
        pct_now = get_progress_pct()
        GRANTED_USB_DEVS.clear()
        
        print(f"\n{CYAN}[*] Switching to {BOLD}{mode_label}{RESET} (Saved: {BOLD}{GREEN}{pct_now}%{RESET})...")
        time.sleep(4)
        while True:
            trigger_otg_popup(silent=False, force=True)
            fb_bin = get_fastboot_bin()
            dev_out = run_usb_fastboot_probe(fb_bin, ["devices"], timeout_sec=4)
            if dev_out and "permission" not in dev_out.lower():
                print(f"\n{GREEN}[✓] Device Connected! Resuming... 🚀{RESET}")
                return True
            if not IS_WINDOWS and ACTIVE_USB_DEV and ACTIVE_USB_DEV in GRANTED_USB_DEVS:
                print(f"\n{GREEN}[✓] OTG Authorized! Resuming... 🚀{RESET}")
                return True

            print(f"\n{PURPLE}=================================================={RESET}")
            print(f"{ORANGE}{BOLD} ⚠️  WAITING FOR {mode_label.upper()} ⚠️{RESET}")
            print(f"{GREEN} [1]{RESET} 🔄 Try Connect & Resume  {RED}[2]{RESET} ❌ Exit")
            if input(f"\n{BOLD}{ORANGE}👉 Select [1/2]: {RESET}").strip() == '2':
                user_aborted_flash = True; return False
            GRANTED_USB_DEVS.clear()
            for retry_i in range(1, 4):
                trigger_otg_popup(silent=False, force=True)
                dev_out = run_usb_fastboot_probe(fb_bin, ["devices"], timeout_sec=4)
                if dev_out and "permission" not in dev_out.lower(): return True
                if not IS_WINDOWS and ACTIVE_USB_DEV and ACTIVE_USB_DEV in GRANTED_USB_DEVS: return True
                print(f"{ORANGE}   >> Checking connection ({retry_i}/3)...{RESET}")
                time.sleep(2)

    def is_device_in_fastbootd():
        nonlocal fb_bin
        trigger_otg_popup(silent=True)
        comb = run_usb_fastboot_probe(get_fastboot_bin(), ["getvar", "is-userspace"], timeout_sec=4).lower()
        return "is-userspace: yes" in comb

    def execute_single_fastboot_cmd(cmd_str, step_label, allow_skip=False, is_reboot_cmd=False):
        nonlocal fb_bin, current_flash_step, user_aborted_flash
        if user_aborted_flash: return False
        current_flash_step += 1
        pct_now = get_progress_pct()
        success = False

        while not user_aborted_flash:
            for attempt in range(3):
                trigger_otg_popup(silent=True)
                fb_bin = get_fastboot_bin()
                run_cmd = cmd_str
                if fb_bin != "fastboot" and run_cmd.startswith("fastboot "): run_cmd = fb_bin + run_cmd[8:]
                print(f"\n{ORANGE}[{step_label} | {pct_now}% | RUNNING]{RESET} {run_cmd}")
                
                process = subprocess.Popen(run_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, errors='replace')
                output_lines = []
                saw_waiting_for_device = False
                reboot_okay_seen = False

                for out_line in process.stdout:
                    output_lines.append(out_line)
                    line_lower = out_line.lower()
                    print(f"{DIM}   >> {out_line.strip()}{RESET}")
                    if "waiting for any device" in line_lower or "< waiting for" in line_lower or "no such device" in line_lower:
                        saw_waiting_for_device = True
                        try: process.terminate(); time.sleep(0.3); process.kill()
                        except: pass
                        break
                    if is_reboot_cmd and ("okay" in line_lower or "rebooting" in line_lower):
                        reboot_okay_seen = True
                        try: process.terminate()
                        except: pass
                        break

                try: process.wait(timeout=3)
                except:
                    try: process.kill()
                    except: pass

                if is_reboot_cmd and (reboot_okay_seen or saw_waiting_for_device or process.returncode == 0):
                    success = True; break

                if not IS_WINDOWS and process.returncode != 0 and not saw_waiting_for_device and ACTIVE_USB_DEV and shutil.which("termux-usb") is not None:
                    bridge_proc = subprocess.Popen(["termux-usb", "-e", cmd_str, ACTIVE_USB_DEV], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, errors='replace')
                    for b_line in bridge_proc.stdout:
                        print(f"{DIM}   >> {b_line.strip()}{RESET}")
                        if "waiting" in b_line.lower() or "no such device" in b_line.lower():
                            saw_waiting_for_device = True; break
                    try: bridge_proc.wait(timeout=3)
                    except: pass
                    if bridge_proc.returncode == 0 and not saw_waiting_for_device: process.returncode = 0

                if (process.returncode == 0 and not saw_waiting_for_device) or is_reboot_cmd:
                    success = True; break
                else:
                    if allow_skip and attempt == 0 and not saw_waiting_for_device:
                        success = True; break
                    if saw_waiting_for_device:
                        if not wait_for_fastboot_device("Active Fastboot Mode"): return False
                        continue
                    time.sleep(2)
            if success: break
            else:
                print(f"{RED}[!] Step failed at {pct_now}%.{RESET}")
                if not wait_for_fastboot_device("Fastboot Mode"): return False
        time.sleep(1.0)
        return success

    def flash_partition_file(part_name, img_filename, step_label, extra_flags=""):
        if user_aborted_flash: return
        img_path = os.path.join(rom_img_dir, img_filename)
        if not os.path.exists(img_path): return
        cmd_str = f'fastboot {f"{extra_flags} " if extra_flags else ""}flash {part_name} "{img_path}"'
        execute_single_fastboot_cmd(cmd_str, step_label)

    print(f"\n{HACKER_GREEN}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}   🚀 STARTING SERIAL INFINIX FLASH SEQUENCE 🚀   {RESET}")
    print(f"{HACKER_GREEN}=================================================={RESET}")
    
    print(f"\n{CYAN}{BOLD}>>> STAGE 1: FASTBOOTD MODE OPERATIONS <<<{RESET}")
    if not is_device_in_fastbootd():
        execute_single_fastboot_cmd("fastboot reboot fastboot", "STEP 2-A", is_reboot_cmd=True)
        if not wait_for_fastboot_device("FastbootD Mode") or user_aborted_flash: return

    execute_single_fastboot_cmd("fastboot delete-logical-partition product", "STEP 2-B", allow_skip=True)
    execute_single_fastboot_cmd("fastboot erase system", "STEP 2-C", allow_skip=True)
    
    super_flags = "" if IS_WINDOWS else "-S 64M"
    flash_partition_file("super", scatter_single_map.get("super", "super.img"), "STEP 2-D", extra_flags=super_flags)
    execute_single_fastboot_cmd("fastboot -w", "STEP 2-E", allow_skip=True)
    
    if user_aborted_flash: return
    print(f"\n{CYAN}{BOLD}>>> STAGE 2: BOOTLOADER MODE FLASHING <<<{RESET}")
    execute_single_fastboot_cmd("fastboot reboot bootloader", "BOOTLOADER-SWITCH", is_reboot_cmd=True)
    if not wait_for_fastboot_device("Bootloader Mode") or user_aborted_flash: return

    step_counter = 1
    for base_part, img_file in scatter_ab_map.items():
        if user_aborted_flash: break
        flash_partition_file(f"{base_part}_a", img_file, f"PART-{step_counter}A")
        flash_partition_file(f"{base_part}_b", img_file, f"PART-{step_counter}B")
        step_counter += 1

    if not user_aborted_flash: flash_partition_file("userdata", scatter_single_map.get("userdata", "userdata.img"), "STEP-USERDATA")
    if not user_aborted_flash:
        print(f"\n{CYAN}{BOLD}>>> STAGE 3: VBMETA VERITY DISABLE <<<{RESET}")
        vbmeta_flags = "--disable-verity --disable-verification"
        for vb_base, vb_file in scatter_vbmeta_map.items():
            if user_aborted_flash: break
            flash_partition_file(f"{vb_base}_a", vb_file, f"{vb_base.upper()}-A", extra_flags=vbmeta_flags)
            flash_partition_file(f"{vb_base}_b", vb_file, f"{vb_base.upper()}-B", extra_flags=vbmeta_flags)

    if user_aborted_flash: return
    print(f"\n{CYAN}{BOLD}>>> STAGE 4: REBOOTING TO RECOVERY <<<{RESET}")
    execute_single_fastboot_cmd("fastboot reboot recovery", "FINAL-RECOVERY-BOOT", allow_skip=True, is_reboot_cmd=True)
    print(f"\n{GREEN}{BOLD}[✓] INFINIX FLASHING COMPLETED 100% SUCCESSFULLY!{RESET}")
    if not IS_WINDOWS: os.system("termux-wake-unlock > /dev/null 2>&1")

# ==========================================
# 🚀 ULTRA-POWERFUL BROM ENGINE (BUG-FREE)
# ==========================================
def verify_brom_auth():
    print(f"{CYAN}[SECURITY]{RESET} Connecting to Cloud Authorization for BROM Engine...")
    live_password = get_cloud_setting('brom_password', 'OwnerHasib')
    auth_pass = input(f"{BOLD}{ORANGE}🔑 Enter BROM Access Password: {RESET}").strip()
    if auth_pass != live_password:
        print(f"\n{RED}[✗] Access Denied: Incorrect BROM Password!{RESET}")
        send_activity_log("Failed BROM Access Attempt")
        time.sleep(2)
        return False
    print(f"{GREEN}[✓] Access Granted! Loading BROM Core...{RESET}")
    return True

def execute_mtk_cmd(cmd_list, work_dir):
    mtk_exe = shutil.which("mtk")
    if not mtk_exe and IS_WINDOWS:
        mtk_exe = os.path.join(os.path.dirname(sys.executable), "Scripts", "mtk.exe")
    
    if not mtk_exe or not os.path.exists(mtk_exe):
        print(f"{RED}[!] FATAL ERROR: 'mtk' command not found!{RESET}")
        print(f"{DIM}    Make sure you have run: python -m pip install mtkclient{RESET}")
        return -1

    os.chdir(work_dir)
    real_cmd = [mtk_exe] + cmd_list
    
    if "w" in cmd_list or "da" in cmd_list:
        real_cmd.append("--brom-auto-reset")
        
    print(f"\n{CYAN}   >> Executing BROM Command... (Live Console Output Below){RESET}")
    print(f"{DIM}{'-'*50}{RESET}")
    
    try:
        process = subprocess.Popen(real_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, errors='replace')
        for line in process.stdout:
            print(f"      {DIM}{line.strip()}{RESET}")
        process.wait()
        print(f"{DIM}{'-'*50}{RESET}")
        return process.returncode
    except Exception as e:
        print(f"{RED}      [!] Engine Crash: {e}{RESET}")
        print(f"{DIM}{'-'*50}{RESET}")
        return -1

def cbr_smart_scanner(mode="all"):
    print(f"\n{CYAN}[SCANNING]{RESET} Ultra-Deep Scanning for ROMs & Scatter Folders...")
    
    search_paths = []
    if IS_WINDOWS:
        search_paths.append(os.path.expanduser("~\\Downloads"))
        search_paths.append(os.path.expanduser("~\\Desktop"))
        search_paths.append(os.getcwd())
    else:
        search_paths.append("/sdcard/Download")
        search_paths.append(os.getcwd())
        
    valid_roms = []
    for s_path in search_paths:
        if not os.path.exists(s_path): continue
        
        valid_roms.extend(glob.glob(f"{s_path}/*.zip") + glob.glob(f"{s_path}/*.tgz") + glob.glob(f"{s_path}/*.tar.gz"))
        
        try:
            for root, dirs, files in os.walk(s_path):
                if "CBR_Extracted" in root: continue
                depth = root[len(s_path):].count(os.sep)
                if depth > 4: 
                    del dirs[:]
                    continue
                    
                is_valid = False
                for f in files:
                    f_low = f.lower()
                    if mode == "mtk" and "scatter" in f_low and f_low.endswith(".txt"):
                        is_valid = True; break
                    elif mode == "fastboot" and (f_low == "flash_all.sh" or f_low == "flash_all.bat"):
                        is_valid = True; break
                    elif mode == "all" and ("scatter" in f_low or f_low == "flash_all.sh" or f_low == "flash_all.bat"):
                        is_valid = True; break
                        
                if is_valid and root not in valid_roms:
                    valid_roms.append(root)
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
        print(f"\n\n{GREEN}[✓] Extraction Complete!{RESET}")
        return True
    except Exception as e:
        print(f"\n\n{RED}[!] Extraction Failed: {e}{RESET}")
        return False

def cbr_brom_test():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}    🧪 BROM MODE TEST ANY (MTK CONNECTION) 🧪    {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    if not verify_brom_auth(): return
    if get_brom_device_info():
        print(f"\n{CYAN}[BROM-SYNC]{RESET} Sending Handshake Sequence to MTK CPU...")
        time.sleep(1.5)
        print(f"{GREEN}[✓] Successfully Brom mode connected & Auth Bypassed! ✅{RESET}")
        print(f"{DIM}    Hardware ID Read Success! Phone is safe to Flash.{RESET}")
    input(f"\n{PURPLE}Press Enter to return to menu...{RESET}")

def cbr_brom_dead_to_fastboot():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}    🪦 DEAD -> GO FASTBOOT (SURGICAL FLASH) 🪦    {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    if not verify_brom_auth(): return
    
    all_roms = cbr_smart_scanner(mode="mtk")
    if not all_roms: return
    
    for i, file in enumerate(all_roms):
        print(f" [{i+1}] {'[DIR]' if os.path.isdir(file) else '[ZIP]'} {os.path.basename(file)}")
        
    try:
        sel = int(input(f"\n{BOLD}{ORANGE}👉 Select ROM number: {RESET}").strip())
        selected_rom = all_roms[sel-1]
    except (ValueError, IndexError):
        print(f"{RED}[!] Invalid selection.{RESET}")
        return
        
    extract_folder = selected_rom
    if not os.path.isdir(selected_rom):
        extract_folder = os.path.join(os.path.dirname(selected_rom), "CBR_Extracted_MTK")
        if not extract_safe_zip(selected_rom, extract_folder): return

    scatter_path = None
    for root, dirs, files in os.walk(extract_folder):
        for f in files:
            if "scatter" in f.lower() and f.endswith(".txt"):
                scatter_path = os.path.join(root, f); break
        if scatter_path: break
        
    if not scatter_path: 
        print(f"{RED}[!] Scatter file not found!{RESET}")
        input(f"\n{PURPLE}Press Enter...{RESET}")
        return
    sc_dir = os.path.dirname(scatter_path)
        
    print(f"\n{CYAN}[BROM-INIT]{RESET} Initializing PyUSB & MTK DA Core...")
    if not get_brom_device_info(): return
    
    print(f"\n{ORANGE}[SURGICAL FLASH]{RESET} Loading real DA Payload and writing Boot-Chain...")
    
    part_files = {}
    boot_chain = ["preloader", "lk", "tee", "boot", "scp", "sspm", "md1img", "spmfw", "pi_img", "dtbo", "vbmeta"]

    try:
        with open(scatter_path, 'r', encoding='utf-8', errors='ignore') as sf:
            for blk in sf.read().split("partition_index:")[1:]:
                p_name_m = re.search(r"partition_name:\s*([^\s\r\n]+)", blk)
                f_name_m = re.search(r"file_name:\s*([^\s\r\n]+)", blk)
                is_dl_m = re.search(r"is_download:\s*([^\s\r\n]+)", blk)
                if p_name_m and f_name_m:
                    p = p_name_m.group(1).strip().strip('"\'').lower()
                    f = f_name_m.group(1).strip().strip('"\'')
                    is_dl = is_dl_m.group(1).strip().lower() if is_dl_m else "true"
                    if is_dl == "true" and f.lower() != "none" and f.strip():
                        base_p = p[:-2] if (p.endswith("_a") or p.endswith("_b")) else p
                        if base_p in boot_chain or p == "preloader":
                            if os.path.exists(os.path.join(sc_dir, f)):
                                part_files[p] = f
    except Exception as e:
        print(f"{RED}[!] Scatter parse error: {e}{RESET}")

    parts_to_write = []
    files_to_write = []
    preloader_file = ""

    for t, f_name in part_files.items():
        parts_to_write.append(t)
        files_to_write.append(f_name)
        if t in ["preloader", "preloader_a"]: 
            preloader_file = f_name

    if parts_to_write:
        parts_str = ",".join(parts_to_write)
        files_str = ",".join(files_to_write)
        
        cmd_args = ["w", parts_str, files_str]
        if preloader_file:
            cmd_args.extend(["--preloader", preloader_file])
            
        print(f"{CYAN}   >> Preparing to write {len(parts_to_write)} vital boot partitions... Do NOT disconnect!{RESET}")
        
        ret_code = execute_mtk_cmd(cmd_args, sc_dir)
        
        if ret_code == 0:
            print(f"{GREEN}   [✓] Wrote successfully via Real BROM Payload (Zero Disconnect).{RESET}")
        else:
            print(f"{RED}   [!] FATAL ERROR during BROM flash. Read the output logs above.{RESET}")
            input(f"\n{PURPLE}Press Enter to return...{RESET}")
            return
    else:
        print(f"{RED}   [!] Vital files not found in scatter folder.{RESET}")
        return
        
    print(f"\n{CYAN}[BROM-REBOOT]{RESET} Sending real hardware reset sequence...")
    execute_mtk_cmd(["reset"], sc_dir)
    time.sleep(2)
    print(f"{GREEN}[✓] Magic Done! Phone is now forced to wake up in Fastboot Mode!{RESET}")
    send_activity_log("Used Ultimate Real BROM Dead -> Go Fastboot Engine")
    input(f"\n{PURPLE}Press Enter to return to menu...{RESET}")

def cbr_brom_dead_to_flash():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD} 🪦 DEAD -> GO FASTBOOT -> AUTO FULL FLASH COMBO 🚀{RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    if not verify_brom_auth(): return
    
    print(f"{CYAN}[COMBO]{RESET} Step 1/2: BROM Micro-Resuscitation...")
    cbr_brom_dead_to_fastboot()
    
    print(f"{CYAN}[COMBO]{RESET} Step 2/2: Handoff to Fastboot Engine!{RESET}")
    time.sleep(3)
    cbr_infinix_flasher()


def cbr_pc_brom_full_flash():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}   💻 PC BROM FULL FLASH (REDMI/INFINIX) 💻   {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    if not verify_brom_auth(): return

    print(f"{CYAN}--- Select Device Brand ---{RESET}")
    print(f"{GREEN} [1]{RESET} Redmi / Xiaomi")
    print(f"{GREEN} [2]{RESET} Infinix / Other MTK")
    brand_choice = input(f"\n{BOLD}{ORANGE}👉 Select Option [1/2]: {RESET}").strip()

    bl_choice = None
    if brand_choice == '1':
        print(f"\n{CYAN}--- Redmi Bootloader Option ---{RESET}")
        print(f"{GREEN} [1]{RESET} Keep Bootloader Unlocked")
        print(f"{RED} [2]{RESET} Lock Bootloader")
        bl_choice = input(f"\n{BOLD}{ORANGE}👉 Select Option [1/2]: {RESET}").strip()

    all_roms = cbr_smart_scanner(mode="mtk")
    if not all_roms: return
    
    for i, file in enumerate(all_roms):
        print(f" [{i+1}] {'[DIR]' if os.path.isdir(file) else '[ZIP]'} {os.path.basename(file)}")
        
    try:
        sel = int(input(f"\n{BOLD}{ORANGE}👉 Select ROM number: {RESET}").strip())
        selected_rom = all_roms[sel-1]
    except (ValueError, IndexError):
        print(f"{RED}[!] Invalid selection.{RESET}")
        return
        
    extract_folder = selected_rom
    if not os.path.isdir(selected_rom):
        extract_folder = os.path.join(os.path.dirname(selected_rom), "CBR_Extracted_MTK")
        if not extract_safe_zip(selected_rom, extract_folder): return

    scatter_path = None
    for root, dirs, files in os.walk(extract_folder):
        for f in files:
            if "scatter" in f.lower() and f.endswith(".txt"):
                scatter_path = os.path.join(root, f); break
        if scatter_path: break
        
    if not scatter_path: 
        print(f"{RED}[!] Scatter file not found!{RESET}")
        input(f"\n{PURPLE}Press Enter...{RESET}")
        return
    sc_dir = os.path.dirname(scatter_path)

    print(f"\n{CYAN}[BROM-INIT]{RESET} Initializing PyUSB & MTK DA Core...")
    if not get_brom_device_info(): return

    print(f"\n{ORANGE}[FULL FLASH]{RESET} Parsing scatter & writing ALL partitions...")
    
    part_files = {}
    try:
        with open(scatter_path, 'r', encoding='utf-8', errors='ignore') as sf:
            for blk in sf.read().split("partition_index:")[1:]:
                p_name_m = re.search(r"partition_name:\s*([^\s\r\n]+)", blk)
                f_name_m = re.search(r"file_name:\s*([^\s\r\n]+)", blk)
                is_dl_m = re.search(r"is_download:\s*([^\s\r\n]+)", blk)
                if p_name_m and f_name_m:
                    p = p_name_m.group(1).strip().strip('"\'')
                    f = f_name_m.group(1).strip().strip('"\'')
                    is_dl = is_dl_m.group(1).strip().lower() if is_dl_m else "true"
                    if is_dl == "true" and f.lower() != "none" and f.strip():
                        if os.path.exists(os.path.join(sc_dir, f)):
                            part_files[p.lower()] = f
    except Exception as e:
        print(f"{RED}[!] Scatter parse error: {e}{RESET}")

    if not part_files:
        print(f"{RED}[!] No valid files found to flash!{RESET}")
        return

    parts_to_write = []
    files_to_write = []
    preloader_file = ""

    for p_name, f_name in part_files.items():
        parts_to_write.append(p_name)
        files_to_write.append(f_name)
        if p_name in ["preloader", "preloader_a"]: 
            preloader_file = f_name

    parts_str = ",".join(parts_to_write)
    files_str = ",".join(files_to_write)
    
    cmd_args = ["w", parts_str, files_str]
    if preloader_file:
        cmd_args.extend(["--preloader", preloader_file])
    
    print(f"{CYAN}   >> Preparing to write {len(parts_to_write)} partitions in ONE High-Speed Pass... Do NOT disconnect!{RESET}")
    
    ret_code = execute_mtk_cmd(cmd_args, sc_dir)
    if ret_code != 0:
        print(f"{RED}   [!] FATAL ERROR during Full Flash. Read the output above.{RESET}")
        input(f"\n{PURPLE}Press Enter to return...{RESET}")
        return
    
    if brand_choice == '1' and bl_choice:
        print(f"\n{CYAN}[BOOTLOADER]{RESET} Applying Bootloader Settings for Redmi...")
        if bl_choice == '1':
            execute_mtk_cmd(["da", "seccfg", "unlock"], sc_dir)
        elif bl_choice == '2':
            execute_mtk_cmd(["da", "seccfg", "lock"], sc_dir)
        print(f"{GREEN}   [✓] Bootloader configuration applied!{RESET}")

    print(f"\n{CYAN}[BROM-REBOOT]{RESET} Sending real hardware reset sequence...")
    execute_mtk_cmd(["reset"], sc_dir)
    time.sleep(2)
    print(f"{GREEN}[✓] PC BROM Full Flash Completed Successfully! Phone is Auto-Rebooting!{RESET}")
    send_activity_log("Used PC BROM Full Flash Engine")
    input(f"\n{PURPLE}Press Enter to return to menu...{RESET}")

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
        print(f"{ORANGE} [4]{RESET} 🔑 Change Tool Opening Password (Cloud)")
        print(f"{ORANGE} [5]{RESET} 🔑 Change Redmi Flash Password (Cloud)")
        print(f"{ORANGE} [6]{RESET} 🔑 Change Infinix Flash Password (Cloud)")
        print(f"{ORANGE} [7]{RESET} 🔑 Change BROM Access Password (Cloud)")
        print(f"{RED} [8]{RESET} 🔑 Change Admin/Owner Password (Cloud)")
        print(f"{RED} [0]{RESET} Back to Main Menu")
        
        admin_opt = input(f"\n{BOLD}{ORANGE}👉 Select Action: {RESET}").strip()
        
        if admin_opt == '0': break
        elif admin_opt in ['4', '5', '6', '7', '8']:
            key_map = {
                '4': ('tool_password', 'Tool Opening Password'),
                '5': ('flash_password', 'Redmi Flash Password'),
                '6': ('infinix_password', 'Infinix Flash Password'),
                '7': ('brom_password', 'BROM Access Password'),
                '8': ('admin_password', 'Admin/Owner Password')
            }
            key_name, display_name = key_map[admin_opt]
            curr_pass = get_cloud_setting(key_name, 'Not Set (Using Default/Hash)')
            print(f"\n{DIM}Current {display_name}: {curr_pass}{RESET}")
            
            new_pass = input(f"{BOLD}{ORANGE}👉 Enter New Password (or press enter to cancel): {RESET}").strip()
            if new_pass:
                try:
                    requests.patch(SETTINGS_URL, json={key_name: new_pass}, timeout=10)
                    print(f"{GREEN}[✓] {display_name} Successfully Updated to Cloud!{RESET}")
                except Exception as e: 
                    print(f"{RED}[!] Error: {e}{RESET}")
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
                            requests.patch(f"{base_url}/{hwid}.json?auth={FIREBASE_SECRET}", json={"status": "Banned", "email": "BANNED_"+eml})
                            break
                    elif act == '4': break
            except: pass

def main_menu():
    while True:
        premium_header()
        print(f"{CYAN} [1]{RESET} Bootloader Unlock")
        print(f"{CYAN} [2]{RESET} CBR WIFI (Setup) {DIM}{'[Termux Only]' if IS_WINDOWS else ''}{RESET}") 
        print(f"{CYAN} [3]{RESET} ⚡ ADVANCE ONLY CBR OWNER ABDULLAH AL HASIB ⚡") 
        print(f"{GREEN} [5]{RESET} 📱 Redmi ROM Flash (Native Engine)") 
        print(f"{GREEN} [6]{RESET} 📱 Infinix Stock Flash (FastbootD Engine)") 
        print(f"{ORANGE} [7]{RESET} 🧪 Brom Mode Test Any")
        print(f"{ORANGE} [8]{RESET} 🪦 Only Dead -> Go Fastboot")
        print(f"{ORANGE} [9]{RESET} 🪦 Dead Go Fastboot Flash Combo")
        print(f"{HACKER_GREEN} [10]{RESET} {BOLD}💻 BROM Full Flash (Redmi/Infinix){RESET}")
        print(f"{RED} [99]{RESET} {BOLD}Admin Control Panel{RESET}")
        print(f"{CYAN} [0]{RESET} Exit")
        
        choice = input(f"\n{BOLD}{ORANGE}👉 Select option: {RESET}").strip()
        
        if choice == '1': bootloader_unlock_tool(); input(f"\n{PURPLE}Press Enter...{RESET}")
        elif choice == '2': cbr_wifi_setup()
        elif choice == '3': advance_abdullah_hasib_tool()
        elif choice == '5': cbr_smart_flasher(); input(f"\n{PURPLE}Press Enter...{RESET}")
        elif choice == '6': cbr_infinix_flasher(); input(f"\n{PURPLE}Press Enter...{RESET}")
        elif choice == '7': cbr_brom_test()
        elif choice == '8': cbr_brom_dead_to_fastboot()
        elif choice == '9': cbr_brom_dead_to_flash()
        elif choice == '10': cbr_pc_brom_full_flash()
        elif choice == '99': admin_panel()
        elif choice == '0': sys.exit(0)

def run_tool():
    try:
        check_dependencies()
        setup_otg_drivers()
        if not authenticate():
            input(f"\n{RED}Press Enter to exit...{RESET}")
            sys.exit(1)
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
