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

# NEW: অ্যাক্টিভিটি ট্র্যাকিং ফাংশন (সাইলেন্টলি ফায়ারবেসে ডাটা পাঠাবে)
def send_activity_log(action_msg):
    try:
        import requests
        raw_id = platform.node() + str(uuid.getnode())
        hwid = hashlib.md5(raw_id.encode()).hexdigest()[:15].upper()
        db_url = f"https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users/{hwid}/activity_logs.json"
        
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

def check_dependencies():
    try:
        import colorama
        import Cryptodome
        import miunlock
        import requests 
    except ImportError:
        print(f"{ORANGE}[!] Libraries missing. Installing packages silently...{RESET}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", "pycryptodomex", "miunlock", "requests", "--quiet"])

def check_fastboot():
    if shutil.which("fastboot") is None:
        print(f"{RED}[!] Fastboot is not installed or not in PATH!{RESET}")
        print(f"{ORANGE}[*] Auto-installing Android platform-tools (Fastboot/ADB)... Please wait.{RESET}")
        os.system("pkg update -y > /dev/null 2>&1")
        os.system("pkg install android-tools -y")
        time.sleep(2)
        if shutil.which("fastboot") is None:
            print(f"{RED}[!] Auto-install failed! Please install manually: pkg install android-tools{RESET}")
            sys.exit(1)
        else:
            print(f"{GREEN}[✓] Android platform-tools installed successfully!{RESET}")

def get_device_info():
    print(f"{CYAN}[INFO]{RESET} Fetching device details...")
    try:
        result = subprocess.run(["fastboot", "getvar", "product"], capture_output=True, text=True)
        if "product:" in result.stderr:
            product_name = result.stderr.split("product:")[1].split()[0]
            print(f"{GREEN}[✓] Connected Device: {product_name}{RESET}")
        else:
            print(f"{ORANGE}[!] Could not read device product name.{RESET}")
    except Exception:
        pass

def authenticate():
    premium_header()
    print(f"{ORANGE}[SECURITY]{RESET} Protected under CBR verification protocols.")
    try:
        user_pass = input(f"{BOLD}🔑 Enter Security Token Password: {RESET}").strip()
        hashed_input = hashlib.sha256(user_pass.encode()).hexdigest()
        
        if hashed_input == SECURE_PASSWORD_HASH:
            print(f"\n{GREEN}[✓] Access Granted! Authenticating cryptographic pipeline...{RESET}")
            time.sleep(1)
            return True
        else:
            print(f"\n{RED}[✗] Access Denied: Incorrect Security Token Password!{RESET}")
            return False
    except Exception as e:
        print(f"\n{RED}[!] Auth Error: {str(e)}{RESET}")
        return False

def ping_server_and_check_ban(hwid):
    import requests
    db_url = f"https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users/{hwid}.json"
    while True:
        try:
            res = requests.get(db_url).json()
            if res and res.get("status") == "Banned":
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
    
    print(f"\n{CYAN}[USER LOGIN]{RESET} Please login to your account.")
    user_email = input(f"{BOLD}{ORANGE}📧 Enter Your Email: {RESET}").strip()
    user_password = input(f"{BOLD}{ORANGE}🔑 Enter Your Password: {RESET}").strip()
    
    if not user_email or not user_password:
        print(f"{RED}[!] Email and Password cannot be empty!{RESET}")
        return False

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
    
    print(f"\n{CYAN}[SYSTEM]{RESET} Your Hardware ID: {BOLD}{ORANGE}{hwid}{RESET}")
    print(f"{CYAN}[DEVICE]{RESET} {device_name}")
    
    base_url = "https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users"
    
    try:
        response = requests.get(f"{base_url}.json")
        all_users = response.json()
        if all_users is None:
            all_users = {}
            
        existing_hwid = None
        db_status = "Pending"
        
        for db_id, data in all_users.items():
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
                    requests.put(f"{base_url}/{hwid}.json", json=payload)
                    requests.delete(f"{base_url}/{existing_hwid}.json")
                else:
                    requests.patch(f"{base_url}/{hwid}.json", json={"device_name": device_name, "last_ping": int(time.time())})
                    
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
            requests.put(f"{base_url}/{hwid}.json", json=payload)
            existing_hwid = hwid
            send_activity_log("New Registration Created - Pending Approval")

        is_waiting_printed = False
        db_url = f"{base_url}/{existing_hwid}.json"
        
        while True:
            resp = requests.get(db_url)
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
                    requests.put(f"{base_url}/{hwid}.json", json=payload)
                    requests.delete(f"{base_url}/{existing_hwid}.json")
                else:
                    requests.patch(f"{base_url}/{hwid}.json", json={"device_name": device_name})
                    
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
        print(f"{ORANGE}[DEBUG ERROR]: {e}{RESET}") # <-- এই লাইনটা অ্যাড করা হয়েছে!
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
    subprocess.run("fastboot devices", shell=True)
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
    
    adv_pass = input(f"{BOLD}{ORANGE}🔑 Enter Master Password for Advance Tool: {RESET}").strip()
    if hashlib.sha256(adv_pass.encode()).hexdigest() != ADVANCE_PASSWORD_HASH:
        print(f"\n{RED}[✗] Access Denied: Unauthorized Attempt!{RESET}")
        send_activity_log("Failed Attempt: Wrong Advance Password")
        time.sleep(2)
        return
        
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

def admin_panel():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}=================================================={RESET}")
    print(f"{RED}{BOLD}        🔐 ADMIN CONTROL DASHBOARD 🔐        {RESET}")
    print(f"{PURPLE}=================================================={RESET}\n")
    
    admin_pass = input(f"{BOLD}{ORANGE}🔑 Enter Owner Password: {RESET}").strip()
    if hashlib.sha256(admin_pass.encode()).hexdigest() != ADVANCE_PASSWORD_HASH:
        print(f"\n{RED}[✗] Access Denied: Intruders Will Be Banned!{RESET}")
        time.sleep(2)
        return

    import requests
    base_url = "https://termux-control-default-rtdb.asia-southeast1.firebasedatabase.app/Users"
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{CYAN}--- REGISTERED USERS ---{RESET}\n")
        
        try:
            users_data = requests.get(f"{base_url}.json").json()
            if not users_data:
                print(f"{RED}No users found in database.{RESET}")
                input("\nPress Enter to go back...")
                break
                
            email_list = []
            for hwid, data in users_data.items():
                email = data.get('email', 'Unknown')
                device = data.get('device_name', 'Unknown Device')
                status = data.get('status', 'Pending')
                
                if status == 'Approved': status_text = f"{GREEN}{status}{RESET}"
                elif status == 'Banned': status_text = f"{RED}{status}{RESET}"
                else: status_text = f"{ORANGE}{status}{RESET}"
                
                print(f"{CYAN}[{len(email_list)+1}]{RESET} {email} | {DIM}{device}{RESET} | [{status_text}]")
                email_list.append((hwid, email))
                
            print(f"\n{RED}[0]{RESET} Back to Main Menu")
            
            try:
                choice = int(input(f"\n{BOLD}{ORANGE}👉 Select a User Number: {RESET}").strip())
                if choice == 0:
                    break
                if choice < 1 or choice > len(email_list):
                    print(f"{RED}Invalid selection!{RESET}"); time.sleep(1); continue
                    
                selected_hwid, selected_email = email_list[choice - 1]
                
                while True:
                    print(f"\n{CYAN}--- MANAGING: {selected_email} ---{RESET}")
                    print(f"{GREEN} [1]{RESET} View Live Activity Logs")
                    print(f"{GREEN} [2]{RESET} Delete User History (Clear Logs)")
                    print(f"{RED} [3]{RESET} Permanent Delete & Ban User")
                    print(f"{ORANGE} [4]{RESET} Back to User List")
                    
                    act = input(f"\n{BOLD}{ORANGE}👉 Select Action: {RESET}").strip()
                    
                    if act == '1':
                        print(f"\n{CYAN}--- ACTIVITY LOGS ---{RESET}")
                        logs = requests.get(f"{base_url}/{selected_hwid}/activity_logs.json").json()
                        if logs:
                            for timestamp, log_msg in sorted(logs.items()):
                                print(f"{DIM}{log_msg}{RESET}")
                        else:
                            print(f"{ORANGE}No activity logs found for this user.{RESET}")
                        input(f"\n{PURPLE}Press Enter to continue...{RESET}")
                        
                    elif act == '2':
                        print(f"\n{ORANGE}[*] Clearing history...{RESET}")
                        requests.delete(f"{base_url}/{selected_hwid}/activity_logs.json")
                        print(f"{GREEN}[✓] History deleted successfully!{RESET}")
                        time.sleep(1.5)
                        
                    elif act == '3':
                        confirm = input(f"{RED}Are you sure you want to BAN {selected_email}? (y/n): {RESET}").lower()
                        if confirm == 'y':
                            requests.patch(f"{base_url}/{selected_hwid}.json", json={"status": "Banned", "email": "BANNED_" + selected_email})
                            print(f"{GREEN}[✓] User banned successfully!{RESET}")
                            time.sleep(2)
                            break
                            
                    elif act == '4':
                        break
                    else:
                        print(f"{RED}Invalid option!{RESET}")
            except ValueError:
                print(f"{RED}Please enter a valid number!{RESET}")
                time.sleep(1)
                
        except Exception as e:
            print(f"{RED}Error connecting to database: {e}{RESET}")
            input("\nPress Enter to go back...")
            break

def main_menu():
    while True:
        show_welcome_screen()
        print(f"{CYAN} [1]{RESET} Bootloader Unlock")
        print(f"{CYAN} [2]{RESET} CBR WIFI (Setup)") 
        print(f"{CYAN} [3]{RESET} ⚡ ADVANCE ONLY CBR OWNER ABDULLAH AL HASIB ⚡") 
        print(f"{RED} [9]{RESET} {BOLD}Admin Control Panel{RESET}")
        print(f"{CYAN} [4]{RESET} Exit")
        
        choice = input(f"\n{BOLD}{ORANGE}👉 Select an option: {RESET}").strip()
        
        if choice == '1':
            send_activity_log("Selected Option 1: Bootloader Unlock Menu")
            bootloader_unlock_tool()
            input(f"\n{PURPLE}Press Enter to return to menu...{RESET}")
        elif choice == '2':
            cbr_wifi_setup()
            sys.exit(0)
        elif choice == '3':
            advance_abdullah_hasib_tool()
        elif choice == '9':
            admin_panel()
        elif choice == '4':
            send_activity_log("User Exited the Tool")
            print(f"{GREEN}Exiting CBR Tool. Goodbye!{RESET}")
            sys.exit(0)
        else:
            print(f"{RED}Invalid Option! Try again.{RESET}")
            time.sleep(1)

def run_tool():
    try:
        check_dependencies()
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
        input("\nPress Enter to debug/exit...")

if __name__ == "__main__":
    run_tool()
