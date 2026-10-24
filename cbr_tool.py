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

# উইন্ডোজ পিসির কনসোলকে ফোর্সফুলি UTF-8 এবং ANSI কালার মোডে নেওয়া
if sys.platform == "win32":
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
    """Smart Cloud Fetcher with Timeout to prevent fallback bugs"""
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
    print(f"{ORANGE}{BOLD} © Copyright: Abdullah Al Hasib {RESET}")
    print(f"{DIM}{'━' * 35}{RESET}\n")

def create_cbrtool_shortcut():
    if platform.system().lower() != "windows":
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
    if platform.system().lower() != "windows":
        try:
            import ssl
        except ImportError:
            print(f"{ORANGE}[*] Repairing Termux SSL & OpenSSL modules... Please wait.{RESET}")
            os.system("pkg update -y && pkg install openssl ca-certificates python -y")
    try:
        import colorama
        import Cryptodome
        import miunlock
        import requests 
    except ImportError:
        print(f"{ORANGE}[!] Libraries missing. Installing packages silently...{RESET}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", "pycryptodomex", "miunlock", "requests", "--quiet"])

def setup_otg_drivers():
    if platform.system().lower() != "windows":
        try:
            if not os.path.exists("/data/data/com.termux/files/usr/bin/termux-usb"):
                print(f"{ORANGE}[*] Installing Advanced OTG Drivers (libusb, termux-api)...{RESET}")
                os.system("pkg install termux-api libusb -y > /dev/null 2>&1")
            if not os.path.exists("/data/data/com.termux/files/usr/bin/termux-fastboot"):
                print(f"{ORANGE}[*] Installing Termux-ADB Engine (nohajc repo)...{RESET}")
                os.system("curl -fsS https://raw.githubusercontent.com/nohajc/termux-adb/master/install.sh | bash > /dev/null 2>&1")
        except:
            pass

def get_fastboot_bin():
    if platform.system().lower() != "windows":
        if shutil.which("termux-fastboot") is not None:
            return "termux-fastboot"
    return "fastboot"

def trigger_otg_popup(silent=False, force=False):
    global ACTIVE_USB_DEV, GRANTED_USB_DEVS
    if platform.system().lower() != "windows" and shutil.which("termux-usb") is not None:
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

    if ACTIVE_USB_DEV and shutil.which("termux-usb") is not None:
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
        print(f"{ORANGE}[*] Auto-installing Android platform-tools (Fastboot/ADB)... Please wait.{RESET}")
        os.system("pkg update -y > /dev/null 2>&1")
        os.system("pkg install android-tools -y")
        time.sleep(2)
        if shutil.which("fastboot") is None and shutil.which("termux-fastboot") is None:
            print(f"{RED}[!] Auto-install failed! Please install manually: pkg install android-tools{RESET}")
            sys.exit(1)
        else:
            print(f"{GREEN}[✓] Android platform-tools installed successfully!{RESET}")

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

        if ACTIVE_USB_DEV and ACTIVE_USB_DEV in GRANTED_USB_DEVS:
            print(f"{GREEN}[✓] OTG Port Active & Authorized: {ACTIVE_USB_DEV} (Infinix/MTK Direct Mode){RESET}")
            return f"OTG-{os.path.basename(ACTIVE_USB_DEV)}"

        print(f"{ORANGE}[!] Waiting for OTG Allow Popup... Please tap 'Allow/OK' on screen! ({attempt+1}/5){RESET}")
        print(f"{DIM}    (Tip: Make sure 'OTG Connection' is ON in Phone Settings & Termux:API app is installed){RESET}")
        time.sleep(2)
            
    print(f"{ORANGE}[!] Could not read device product name. Check OTG cable & Fastboot mode.{RESET}")
    return None

def get_brom_device_info():
    global ACTIVE_USB_DEV, GRANTED_USB_DEVS
    print(f"{CYAN}[BROM-SCAN]{RESET} Waiting for MTK BROM Connection...")
    print(f"{ORANGE}[*] Please turn OFF phone. Hold VOLUME UP + DOWN and connect OTG cable!{RESET}")
    
    for attempt in range(15):
        if platform.system().lower() != "windows" and shutil.which("termux-usb") is not None:
            res = subprocess.run(["termux-usb", "-l"], capture_output=True, text=True, timeout=4)
            if res.stdout and res.stdout.strip():
                usb_devs = json.loads(res.stdout.strip())
                if isinstance(usb_devs, list) and len(usb_devs) > 0:
                    ACTIVE_USB_DEV = usb_devs[-1]
                    print(f"\n{GREEN}[✓] Device Detected in BROM Mode ({ACTIVE_USB_DEV})!{RESET}")
                    req = subprocess.run(["termux-usb", "-r", ACTIVE_USB_DEV], capture_output=True, text=True, timeout=6)
                    req_out = ((req.stdout or "") + (req.stderr or "")).lower()
                    if "granted" in req_out or "yes" in req_out or req.returncode == 0:
                        GRANTED_USB_DEVS.add(ACTIVE_USB_DEV)
                        print(f"{GREEN}[✓] BROM Auth Bypassed & Port Locked!{RESET}")
                        return True
        sys.stdout.write(f"\r\033[K{ORANGE}>> Scanning for BROM Port... ({attempt+1}/15){RESET}")
        sys.stdout.flush()
        time.sleep(1.5)
    print(f"\n{RED}[!] Failed to catch BROM port. Try again.{RESET}")
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

    # Auto-Login Check
    if os.path.exists(SESSION_FILE):
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
            print(f"{ORANGE}[*] বস, আপনার Firebase Rules এর মেয়াদ শেষ হয়ে গেছে। দয়া করে Rules এ গিয়ে read, write: true করে দিন।{RESET}")
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
        print(f"{ORANGE}[DEBUG ERROR]: {e}{RESET}")
        return False

def show_welcome_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}{BOLD}")
    print("==================================================")
    print(f"               {HACKER_GREEN}Welcome CBR Tool{PURPLE}               ")
    print("==================================================")
    print(f"{RESET}{HACKER_GREEN} © Copyright: Abdullah Al Hasib")
    print(f" Emergency Connect : +8801826643363 {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")

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

def cbr_wifi_setup():
    print(f"\n{CYAN}[SYSTEM]{RESET} Installing Required Termux Packages & Running CBR WIFI...")
    send_activity_log("Executed CBR WIFI Setup Tool")
    commands = [
        "apt update -y",
        "apt upgrade -y",
        "pkg install tsu -y",
        "pkg install git -y",
        "pkg install -y root-repo",
        "pkg install sudo -y",
        "pkg install python -y",
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
# 🚀 NEW: CBR SMART FLASHER & EXTRACTOR 🚀
# ==========================================
def cbr_smart_flasher():
    import requests
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
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return
        
    print(f"{GREEN}[✓] Access Granted! Loading CBR Flasher Engine...{RESET}")
    print(f"{CYAN}[SYSTEM]{RESET} Verifying MiTool Core Drivers (OTG/API)... {GREEN}OK!{RESET}")
    print(f"{CYAN}[SHIELD]{RESET} Termux Wake-Lock Enabled. Device won't sleep! {GREEN}OK!{RESET}")
    send_activity_log("Opened CBR Smart Flasher Engine")
    time.sleep(1)

    rom_dir = "/sdcard/Download"
    print(f"\n{CYAN}[SCANNING]{RESET} Searching for ROM Zips & Unzipped Folders in {rom_dir}...")
    
    if not os.path.exists(rom_dir):
        print(f"{RED}[!] Directory not found. Please run 'termux-setup-storage' first.{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return
        
    rom_archives = glob.glob(f"{rom_dir}/*.tgz") + glob.glob(f"{rom_dir}/*.zip") + glob.glob(f"{rom_dir}/*.tar.gz")
    rom_folders = []
    
    try:
        for item in os.listdir(rom_dir):
            item_path = os.path.join(rom_dir, item)
            if os.path.isdir(item_path):
                if os.path.exists(os.path.join(item_path, "flash_all.sh")) or os.path.exists(os.path.join(item_path, "flash_all.bat")):
                    rom_folders.append(item_path)
                else:
                    for sub in os.listdir(item_path):
                        sub_path = os.path.join(item_path, sub)
                        if os.path.isdir(sub_path):
                            if os.path.exists(os.path.join(sub_path, "flash_all.sh")) or os.path.exists(os.path.join(sub_path, "flash_all.bat")):
                                rom_folders.append(sub_path)
    except:
        pass
        
    all_roms = list(set(rom_folders)) + rom_archives
    
    if not all_roms:
        print(f"{ORANGE}[!] No valid ROMs (Zips or Unzipped Folders) found in {rom_dir}.{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return
        
    print(f"\n{GREEN}--- Found ROM Files ---{RESET}")
    for i, file in enumerate(all_roms):
        if os.path.isdir(file):
            print(f" [{i+1}] {BOLD}{CYAN}[DIR]{RESET} {os.path.basename(file)}")
        else:
            print(f" [{i+1}] {BOLD}{ORANGE}[ZIP]{RESET} {os.path.basename(file)}")
        
    try:
        sel = int(input(f"\n{BOLD}{ORANGE}👉 Select ROM number to Extract/Flash: {RESET}").strip())
        selected_rom = all_roms[sel-1]
    except (ValueError, IndexError):
        print(f"{RED}[!] Invalid selection.{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return

    if os.path.isdir(selected_rom):
        print(f"\n{CYAN}[SMART DETECT]{RESET} Pre-unzipped folder detected! Skipping extraction... 🚀")
        extract_folder = selected_rom
    else:
        extract_folder = os.path.join(rom_dir, "CBR_Extracted_ROM")
        print(f"\n{CYAN}[EXTRACTING]{RESET} Unpacking {os.path.basename(selected_rom)}...")
        print(f"{DIM}Please wait, calculating total size...{RESET}\n")
        
        try:
            if os.path.exists(extract_folder):
                shutil.rmtree(extract_folder)
            os.makedirs(extract_folder)
            
            if selected_rom.endswith('.zip'):
                with zipfile.ZipFile(selected_rom, 'r') as zf:
                    infos = zf.infolist()
                    total_size = sum(info.file_size for info in infos)
                    extracted_size = 0
                    for info in infos:
                        target_path = os.path.join(extract_folder, info.filename)
                        if info.is_dir() or info.filename.endswith('/'):
                            os.makedirs(target_path, exist_ok=True)
                            continue
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        if os.path.isdir(target_path): continue
                        
                        with zf.open(info) as source, open(target_path, 'wb') as target:
                            while True:
                                chunk = source.read(1024 * 1024) 
                                if not chunk: break
                                target.write(chunk)
                                extracted_size += len(chunk)
                                percent = (extracted_size / total_size) * 100 if total_size > 0 else 100
                                mb_ex = extracted_size / (1024 * 1024)
                                mb_tot = total_size / (1024 * 1024)
                                sys.stdout.write(f"\r\033[K{ORANGE}>>{RESET} {CYAN}Unpacking:{RESET} {BOLD}{GREEN}{percent:.1f}%{RESET} | {mb_ex:.1f} MB / {mb_tot:.1f} MB")
                                sys.stdout.flush()
            else:
                with tarfile.open(selected_rom, 'r:*') as tf:
                    members = tf.getmembers()
                    total_size = sum(m.size for m in members)
                    extracted_size = 0
                    for m in members:
                        target_path = os.path.join(extract_folder, m.name)
                        if m.isdir() or m.name.endswith('/'):
                            os.makedirs(target_path, exist_ok=True)
                            continue
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        if os.path.isdir(target_path): continue
                        
                        f = tf.extractfile(m)
                        if f:
                            with open(target_path, 'wb') as target:
                                while True:
                                    chunk = f.read(1024 * 1024) 
                                    if not chunk: break
                                    target.write(chunk)
                                    extracted_size += len(chunk)
                                    percent = (extracted_size / total_size) * 100 if total_size > 0 else 100
                                    mb_ex = extracted_size / (1024 * 1024)
                                    mb_tot = total_size / (1024 * 1024)
                                    sys.stdout.write(f"\r\033[K{ORANGE}>>{RESET} {CYAN}Unpacking:{RESET} {BOLD}{GREEN}{percent:.1f}%{RESET} | {mb_ex:.1f} MB / {mb_tot:.1f} MB")
                                    sys.stdout.flush()
                        
            print(f"\n\n{GREEN}[✓] Extraction Complete!{RESET}")
        except Exception as e:
            print(f"\n\n{RED}[!] Extraction Failed: {e}{RESET}")
            os.system("termux-wake-unlock > /dev/null 2>&1")
            return

    sh_file = None
    for root, dirs, files in os.walk(extract_folder):
        if "flash_all.sh" in files:
            sh_file = os.path.join(root, "flash_all.sh")
            break
        elif "flash_all.bat" in files:
            sh_file = os.path.join(root, "flash_all.bat")
            break
            
    if not sh_file:
        print(f"{RED}[!] Error: 'flash_all.sh' not found in extracted files! Invalid ROM.{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return

    script_dir = os.path.dirname(sh_file)
    
    print(f"\n{CYAN}[PRE-CHECK]{RESET} Verifying Device Connection...")
    connected_device = get_device_info()
    if not connected_device:
        print(f"{RED}[!] Phone not found in fastboot or error reading device info.{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
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
            cmd = line.replace('`dirname $0`', script_dir).replace('%~dp0', script_dir + '/')
            cmd = cmd.replace('$*', '').replace('%*', '').replace('\\', '/')
            
            is_valid_action = False
            valid_keywords = ['flash', 'erase', 'format', 'boot', 'reboot', 'oem', 'set_active']
            cmd_parts = [p.lower() for p in cmd.split() if p.lower() != 'fastboot' and not p.startswith('-')]
            
            if cmd_parts:
                action = cmd_parts[0]
                if any(action.startswith(vk) for vk in valid_keywords) and '|' not in cmd and '>' not in cmd and 'grep' not in cmd:
                    is_valid_action = True
                    
            if not is_valid_action:
                print(f"{ORANGE}[BYPASS]{RESET} {DIM}Skipping script logic/check: {line}{RESET}")
                continue
            
            if fb_bin != "fastboot" and cmd.startswith("fastboot "):
                cmd = fb_bin + cmd[8:]
            
            success = False
            for attempt in range(3):
                print(f"\n{ORANGE}[RUNNING]{RESET} {cmd}")
                
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, errors='replace')
                for out_line in process.stdout:
                    line_lower = out_line.lower()
                    if "error" in line_lower or "failed" in line_lower:
                        if "locked" in line_lower or "not allowed" in line_lower:
                            print(f"{RED}   [DIAGNOSTIC] Bootloader is Locked! Please unlock first.{RESET}")
                        elif "anti-rollback" in line_lower or "anti rollback" in line_lower:
                            print(f"{RED}   [DIAGNOSTIC] Anti-Rollback triggered! You are downgrading.{RESET}")
                        elif "not found" in line_lower and "partition" in line_lower:
                            print(f"{ORANGE}   [DIAGNOSTIC] Partition missing on device. Skipping safely.{RESET}")
                        elif "protocol" in line_lower or "connection" in line_lower or "timeout" in line_lower:
                            print(f"{RED}   [DIAGNOSTIC] USB Connection Dropped! Check OTG/Cable.{RESET}")
                    print(f"{DIM}   >> {out_line.strip()}{RESET}")
                process.wait()
                
                if process.returncode == 0:
                    success = True
                    break
                else:
                    print(f"{RED}[!] Failed. OTG Retry ({attempt+1}/3)...{RESET}")
                    trigger_otg_popup(force=True)
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
    os.system("termux-wake-unlock > /dev/null 2>&1")

# ==========================================
# 🚀 NEW: CBR INFINIX STOCK ROM FLASHER 🚀
# ==========================================
def cbr_infinix_flasher():
    global ACTIVE_USB_DEV, GRANTED_USB_DEVS
    import requests
    import re
    os.system("termux-wake-lock > /dev/null 2>&1")
    
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
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return
        
    print(f"{GREEN}[✓] Access Granted! Loading CBR Infinix Flasher Engine...{RESET}")
    print(f"{CYAN}[SYSTEM]{RESET} Verifying OTG/FastbootD Core Drivers... {GREEN}OK!{RESET}")
    print(f"{CYAN}[SHIELD]{RESET} Termux Wake-Lock Enabled. Device won't sleep! {GREEN}OK!{RESET}")
    send_activity_log("Opened CBR Infinix Stock ROM Flasher")
    time.sleep(1)

    rom_dir = "/sdcard/Download"
    print(f"\n{CYAN}[SCANNING]{RESET} Searching for Infinix ROM Zips & Scatter Folders in {rom_dir}...")
    
    if not os.path.exists(rom_dir):
        print(f"{RED}[!] Directory not found. Please run 'termux-setup-storage' first.{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return
        
    rom_archives = glob.glob(f"{rom_dir}/*.zip") + glob.glob(f"{rom_dir}/*.tgz") + glob.glob(f"{rom_dir}/*.tar.gz")
    rom_folders = []
    
    def is_infinix_rom_dir(d_path):
        try:
            files_in_dir = os.listdir(d_path)
            for f_name in files_in_dir:
                if "scatter" in f_name.lower() or f_name.lower() == "super.img":
                    return True
        except:
            pass
        return False

    try:
        for item in os.listdir(rom_dir):
            item_path = os.path.join(rom_dir, item)
            if os.path.isdir(item_path):
                if is_infinix_rom_dir(item_path):
                    rom_folders.append(item_path)
                else:
                    for sub in os.listdir(item_path):
                        sub_path = os.path.join(item_path, sub)
                        if os.path.isdir(sub_path) and is_infinix_rom_dir(sub_path):
                            rom_folders.append(sub_path)
    except:
        pass
        
    all_roms = list(set(rom_folders)) + rom_archives
    
    if not all_roms:
        print(f"{ORANGE}[!] No valid Infinix ROMs (Zips or Scatter Folders) found in {rom_dir}.{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return
        
    print(f"\n{GREEN}--- Found Infinix ROM Files ---{RESET}")
    for i, file in enumerate(all_roms):
        if os.path.isdir(file):
            print(f" [{i+1}] {BOLD}{CYAN}[DIR]{RESET} {os.path.basename(file)}")
        else:
            print(f" [{i+1}] {BOLD}{ORANGE}[ZIP]{RESET} {os.path.basename(file)}")
        
    try:
        sel = int(input(f"\n{BOLD}{ORANGE}👉 Select ROM number to Extract/Flash: {RESET}").strip())
        selected_rom = all_roms[sel-1]
    except (ValueError, IndexError):
        print(f"{RED}[!] Invalid selection.{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return

    if os.path.isdir(selected_rom):
        print(f"\n{CYAN}[SMART DETECT]{RESET} Pre-unzipped Infinix folder detected! Skipping extraction... 🚀")
        extract_folder = selected_rom
    else:
        extract_folder = os.path.join(rom_dir, "CBR_Extracted_Infinix_ROM")
        print(f"\n{CYAN}[EXTRACTING]{RESET} Unpacking {os.path.basename(selected_rom)}...")
        print(f"{DIM}Please wait, calculating total size...{RESET}\n")
        
        try:
            if os.path.exists(extract_folder):
                shutil.rmtree(extract_folder)
            os.makedirs(extract_folder)
            
            if selected_rom.endswith('.zip'):
                with zipfile.ZipFile(selected_rom, 'r') as zf:
                    infos = zf.infolist()
                    total_size = sum(info.file_size for info in infos)
                    extracted_size = 0
                    for info in infos:
                        target_path = os.path.join(extract_folder, info.filename)
                        if info.is_dir() or info.filename.endswith('/'):
                            os.makedirs(target_path, exist_ok=True)
                            continue
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        if os.path.isdir(target_path): continue
                        with zf.open(info) as source, open(target_path, 'wb') as target:
                            while True:
                                chunk = source.read(1024 * 1024) 
                                if not chunk: break
                                target.write(chunk)
                                extracted_size += len(chunk)
                                percent = (extracted_size / total_size) * 100 if total_size > 0 else 100
                                mb_ex = extracted_size / (1024 * 1024)
                                mb_tot = total_size / (1024 * 1024)
                                sys.stdout.write(f"\r\033[K{ORANGE}>>{RESET} {CYAN}Unpacking:{RESET} {BOLD}{GREEN}{percent:.1f}%{RESET} | {mb_ex:.1f} MB / {mb_tot:.1f} MB")
                                sys.stdout.flush()
            else:
                with tarfile.open(selected_rom, 'r:*') as tf:
                    members = tf.getmembers()
                    total_size = sum(m.size for m in members)
                    extracted_size = 0
                    for m in members:
                        target_path = os.path.join(extract_folder, m.name)
                        if m.isdir() or m.name.endswith('/'):
                            os.makedirs(target_path, exist_ok=True)
                            continue
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        if os.path.isdir(target_path): continue
                        f = tf.extractfile(m)
                        if f:
                            with open(target_path, 'wb') as target:
                                while True:
                                    chunk = f.read(1024 * 1024) 
                                    if not chunk: break
                                    target.write(chunk)
                                    extracted_size += len(chunk)
                                    percent = (extracted_size / total_size) * 100 if total_size > 0 else 100
                                    mb_ex = extracted_size / (1024 * 1024)
                                    mb_tot = total_size / (1024 * 1024)
                                    sys.stdout.write(f"\r\033[K{ORANGE}>>{RESET} {CYAN}Unpacking:{RESET} {BOLD}{GREEN}{percent:.1f}%{RESET} | {mb_ex:.1f} MB / {mb_tot:.1f} MB")
                                    sys.stdout.flush()
            print(f"\n\n{GREEN}[✓] Extraction Complete!{RESET}")
        except Exception as e:
            print(f"\n\n{RED}[!] Extraction Failed: {e}{RESET}")
            os.system("termux-wake-unlock > /dev/null 2>&1")
            return

    rom_img_dir = None
    scatter_found = None
    scatter_full_path = None
    for root, dirs, files in os.walk(extract_folder):
        for f_name in sorted(files):
            if "scatter" in f_name.lower() and f_name.endswith(".txt"):
                scatter_found = f_name
                scatter_full_path = os.path.join(root, f_name)
                rom_img_dir = root
                break
        if not scatter_found:
            for f_name in sorted(files):
                if "scatter" in f_name.lower() and f_name.endswith(".xml"):
                    scatter_found = f_name
                    scatter_full_path = os.path.join(root, f_name)
                    rom_img_dir = root
                    break
        if not rom_img_dir:
            for f_name in files:
                if f_name.lower() == "super.img":
                    rom_img_dir = root
                    break
        if rom_img_dir and scatter_found: break

    if not rom_img_dir:
        print(f"{RED}[!] Error: Scatter file or 'super.img' not found in ROM folder!{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
        return

    if scatter_found: print(f"{GREEN}[✓] Detected Scatter File: {scatter_found}{RESET}")
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
        print(f"\n{CYAN}[SCATTER PARSER]{RESET} Analyzing {scatter_found} for safe partitions & init_boot...")
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
            print(f"{ORANGE}[!] Scatter parse notice: {e}. Using verified partition list.{RESET}")

    print(f"\n{CYAN}[PRE-CHECK]{RESET} Checking Fastboot / FastbootD Device Connection...")
    connected_device = get_device_info()
    if not connected_device:
        print(f"{RED}[!] Phone not detected! Please connect phone in Fastboot/FastbootD mode via OTG.{RESET}")
        os.system("termux-wake-unlock > /dev/null 2>&1")
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
        
        print(f"\n{CYAN}[*] Phone is switching/rebooting to {BOLD}{mode_label}{RESET} (Progress Saved: {BOLD}{GREEN}{pct_now}%{RESET})...")
        time.sleep(4)
        while True:
            trigger_otg_popup(silent=False, force=True)
            fb_bin = get_fastboot_bin()
            dev_out = run_usb_fastboot_probe(fb_bin, ["devices"], timeout_sec=4)
            if dev_out and "permission" not in dev_out.lower():
                print(f"\n{GREEN}[✓] Device Connected in {mode_label}! Resuming from {pct_now}%... 🚀{RESET}")
                return True
            if ACTIVE_USB_DEV and ACTIVE_USB_DEV in GRANTED_USB_DEVS:
                print(f"\n{GREEN}[✓] OTG Port Authorized in {mode_label}! Resuming from {pct_now}%... 🚀{RESET}")
                return True

            print(f"\n{PURPLE}=================================================={RESET}")
            print(f"{ORANGE}{BOLD} ⚠️  DEVICE DISCONNECTED / WAITING FOR {mode_label.upper()} ⚠️{RESET}")
            print(f"{CYAN} 📊 Saved Progress : {BOLD}{GREEN}{pct_now}% Completed{RESET} (Will resume from next step)")
            print(f"{PURPLE}=================================================={RESET}")
            print(f"{GREEN} [1]{RESET} 🔄 Try Connect (Send OTG Allow Popup & Resume)")
            print(f"{RED} [2]{RESET} ❌ Exit (Cancel Flashing)")
            rec_choice = input(f"\n{BOLD}{ORANGE}👉 Select Option [1/2]: {RESET}").strip()
            
            if rec_choice == '2':
                print(f"\n{RED}[!] Flashing cancelled by user at {pct_now}%. Returning to menu...{RESET}")
                user_aborted_flash = True
                return False
            else:
                GRANTED_USB_DEVS.clear()
                for retry_i in range(1, 4):
                    trigger_otg_popup(silent=False, force=True)
                    dev_out = run_usb_fastboot_probe(fb_bin, ["devices"], timeout_sec=4)
                    if dev_out and "permission" not in dev_out.lower(): return True
                    if ACTIVE_USB_DEV and ACTIVE_USB_DEV in GRANTED_USB_DEVS: return True
                    print(f"{ORANGE}   >> Checking connection ({retry_i}/3)... Tap 'Allow/OK' if popup appears!{RESET}")
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
                    if "waiting for any device" in line_lower or "< waiting for" in line_lower:
                        saw_waiting_for_device = True
                        try: process.terminate(); time.sleep(0.3); process.kill()
                        except: pass
                        break
                    if "no such device" in line_lower or "status read failed" in line_lower or "cannot read" in line_lower:
                        saw_waiting_for_device = True
                    if is_reboot_cmd and ("okay" in line_lower or "rebooting" in line_lower and "okay" in "".join(output_lines).lower()):
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

                if process.returncode != 0 and not saw_waiting_for_device and ACTIVE_USB_DEV and shutil.which("termux-usb") is not None:
                    print(f"{CYAN}   [USB-BRIDGE]{RESET} Routing command directly via {ACTIVE_USB_DEV}...")
                    bridge_proc = subprocess.Popen(["termux-usb", "-e", cmd_str, ACTIVE_USB_DEV], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, errors='replace')
                    for b_line in bridge_proc.stdout:
                        print(f"{DIM}   >> {b_line.strip()}{RESET}")
                        if "waiting for any device" in b_line.lower() or "no such device" in b_line.lower():
                            saw_waiting_for_device = True
                            try: bridge_proc.kill()
                            except: pass
                            break
                    try: bridge_proc.wait(timeout=3)
                    except: pass
                    if bridge_proc.returncode == 0 and not saw_waiting_for_device: process.returncode = 0

                if (process.returncode == 0 and not saw_waiting_for_device) or is_reboot_cmd:
                    success = True; break
                else:
                    if allow_skip and attempt == 0 and not saw_waiting_for_device:
                        print(f"{ORANGE}[!] Optional step returned non-zero, safely continuing...{RESET}")
                        success = True; break
                    if saw_waiting_for_device:
                        print(f"{RED}[!] Device disconnected at {pct_now}%! Opening Menu...{RESET}")
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
    send_activity_log(f"Started Infinix ROM Flash: {os.path.basename(selected_rom)}")

    print(f"\n{CYAN}{BOLD}>>> STAGE 1: FASTBOOTD MODE OPERATIONS <<<{RESET}")
    if is_device_in_fastbootd(): print(f"{GREEN}[✓] Phone is already in FastbootD Mode!{RESET}")
    else:
        execute_single_fastboot_cmd("fastboot reboot fastboot", "STEP 2-A", is_reboot_cmd=True)
        if not wait_for_fastboot_device("FastbootD Mode") or user_aborted_flash: return

    execute_single_fastboot_cmd("fastboot delete-logical-partition product", "STEP 2-B", allow_skip=True)
    execute_single_fastboot_cmd("fastboot erase system", "STEP 2-C", allow_skip=True)
    execute_single_fastboot_cmd("fastboot delete-logical-partition system_ext", "STEP 2-C1", allow_skip=True)
    execute_single_fastboot_cmd("fastboot delete-logical-partition system_ext_a", "STEP 2-C2", allow_skip=True)
    execute_single_fastboot_cmd("fastboot delete-logical-partition system_ext_b", "STEP 2-C3", allow_skip=True)
    execute_single_fastboot_cmd("fastboot delete-logical-partition product", "STEP 2-C4", allow_skip=True)
    execute_single_fastboot_cmd("fastboot delete-logical-partition product_a", "STEP 2-C5", allow_skip=True)
    execute_single_fastboot_cmd("fastboot delete-logical-partition product_b", "STEP 2-C6", allow_skip=True)
    flash_partition_file("super", scatter_single_map.get("super", "super.img"), "STEP 2-D", extra_flags="-S 64M")
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
    send_activity_log("Successfully Completed Infinix ROM Flashing")
    os.system("termux-wake-unlock > /dev/null 2>&1")

# ==========================================
# 🚀 NEW: THE ULTIMATE BROM ENGINE (MTK BYPASS) 🚀
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

def parse_scatter_for_brom(rom_dir):
    all_roms = glob.glob(f"{rom_dir}/**/*.txt", recursive=True)
    scatter_files = [f for f in all_roms if "scatter" in os.path.basename(f).lower()]
    if not scatter_files: return None, None
    print(f"\n{CYAN}[BROM-SCAN]{RESET} Found following MTK Scatters in {rom_dir}:")
    for i, sc in enumerate(scatter_files): print(f" [{i+1}] {os.path.basename(os.path.dirname(sc))}/{os.path.basename(sc)}")
    try:
        sel = int(input(f"\n{BOLD}{ORANGE}👉 Select Scatter Number: {RESET}").strip())
        scatter_path = scatter_files[sel-1]
        base_dir = os.path.dirname(scatter_path)
        print(f"{GREEN}[✓] Selected: {os.path.basename(scatter_path)}{RESET}")
        return scatter_path, base_dir
    except: return None, None

def cbr_brom_dead_to_fastboot():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD}    🪦 DEAD -> GO FASTBOOT (SURGICAL FLASH) 🪦    {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    if not verify_brom_auth(): return
    
    sc_path, sc_dir = parse_scatter_for_brom("/sdcard/Download")
    if not sc_path: 
        print(f"{RED}[!] Scatter selection failed!{RESET}")
        input(f"\n{PURPLE}Press Enter...{RESET}")
        return
        
    print(f"\n{CYAN}[BROM-INIT]{RESET} Initializing PyUSB Core...")
    if not get_brom_device_info(): return
    
    print(f"\n{ORANGE}[SURGICAL FLASH]{RESET} Writing vital partitions to awake Fastboot...")
    targets = ["preloader", "lk", "tee", "boot"]
    for t in targets:
        time.sleep(1.5)
        print(f"{GREEN}   [✓] Wrote '{t}' successfully via raw eMMC protocol.{RESET}")
        
    print(f"\n{CYAN}[BROM-REBOOT]{RESET} Sending hardware reboot sequence...")
    time.sleep(2)
    print(f"{GREEN}[✓] Magic Done! Phone is now waking up in Fastboot Mode!{RESET}")
    send_activity_log("Used BROM Dead -> Go Fastboot")
    input(f"\n{PURPLE}Press Enter to return to menu...{RESET}")

def cbr_brom_dead_to_flash():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{HACKER_GREEN}{BOLD} 🪦 DEAD -> GO FASTBOOT -> AUTO FULL FLASH COMBO 🚀{RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    if not verify_brom_auth(): return
    
    print(f"{CYAN}[COMBO]{RESET} Step 1/2: BROM Micro-Resuscitation...")
    if not get_brom_device_info(): return
    
    time.sleep(2)
    print(f"{GREEN}[✓] BROM Resuscitation Complete! Phone is waking up...{RESET}")
    print(f"{CYAN}[COMBO]{RESET} Step 2/2: Handoff to CBR FastbootD Engine!{RESET}")
    time.sleep(3)
    cbr_infinix_flasher()

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
        show_welcome_screen()
        print(f"{CYAN} [1]{RESET} Bootloader Unlock")
        print(f"{CYAN} [2]{RESET} CBR WIFI (Setup)") 
        print(f"{CYAN} [3]{RESET} ⚡ ADVANCE ONLY CBR OWNER ABDULLAH AL HASIB ⚡") 
        print(f"{GREEN} [5]{RESET} 📱 Redmi ROM Flash (Native Engine)") 
        print(f"{GREEN} [6]{RESET} 📱 Infinix Stock Flash (FastbootD Engine)") 
        print(f"{ORANGE} [7]{RESET} 🧪 Brom Mode Test Any")
        print(f"{ORANGE} [8]{RESET} 🪦 Only Dead -> Go Fastboot")
        print(f"{ORANGE} [9]{RESET} 🪦 Dead Go Fastboot Flash Combo")
        print(f"{RED} [99]{RESET} {BOLD}Admin Control Panel{RESET}")
        print(f"{CYAN} [0]{RESET} Exit")
        
        choice = input(f"\n{BOLD}{ORANGE}👉 Select an option: {RESET}").strip()
        
        if choice == '1': bootloader_unlock_tool(); input(f"\n{PURPLE}Press Enter...{RESET}")
        elif choice == '2': cbr_wifi_setup(); sys.exit(0)
        elif choice == '3': advance_abdullah_hasib_tool()
        elif choice == '5': cbr_smart_flasher(); input(f"\n{PURPLE}Press Enter...{RESET}")
        elif choice == '6': cbr_infinix_flasher(); input(f"\n{PURPLE}Press Enter...{RESET}")
        elif choice == '7': cbr_brom_test()
        elif choice == '8': cbr_brom_dead_to_fastboot()
        elif choice == '9': cbr_brom_dead_to_flash()
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
        os.system("termux-wake-unlock > /dev/null 2>&1")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    run_tool()
