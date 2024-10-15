#!/usr/bin/env python3

import os
import subprocess
import sys
import threading
import datetime
import logging
import time
from colorama import Fore, Style, init

# Inisialisasi Colorama untuk pewarnaan terminal
init(autoreset=True)

# Direktori log utama
MAIN_LOG_DIR = "logs"
os.makedirs(MAIN_LOG_DIR, exist_ok=True)

# Tentukan direktori virtual environment yang sudah kamu buat
VENV_DIR = "/opt/venvs/ScanexEZ"  # Ganti dengan path virtual env kamu
os.environ["PATH"] = f"{VENV_DIR}/bin:" + os.environ["PATH"]  # Tambah venv ke PATH

# Daftar tools dengan perintah masing-masing
TOOLS = {
    "sql_injection": "sudo sqlmap -u '{url}' --batch --level=2 --risk=2",
    "xss": "sudo dalfox url '{url}' --silence",
    "lfi": "lfimap -U '{url}' --use-long --force-ssl -v",
    "csrf": "xsrfprobe -u '{url}' --verbose",
    "open_redirect": "echo '{url}' | openredirex"
}

def print_title():
    """Menampilkan judul dengan ASCII art dan pewarnaan."""
    title = f"""
{Fore.CYAN}{Style.BRIGHT}

   ▄████████  ▄████████    ▄████████ ███▄▄▄▄      ▄████████ ▀████    ▐████▀    ▄████████  ▄███████▄  
  ███    ███ ███    ███   ███    ███ ███▀▀▀██▄   ███    ███   ███▌   ████▀    ███    ███ ██▀     ▄██ 
  ███    █▀  ███    █▀    ███    ███ ███   ███   ███    █▀     ███  ▐███      ███    █▀        ▄███▀ 
  ███        ███          ███    ███ ███   ███  ▄███▄▄▄        ▀███▄███▀     ▄███▄▄▄      ▀█▀▄███▀▄▄ 
▀███████████ ███        ▀███████████ ███   ███ ▀▀███▀▀▀        ████▀██▄     ▀▀███▀▀▀       ▄███▀   ▀ 
         ███ ███    █▄    ███    ███ ███   ███   ███    █▄    ▐███  ▀███      ███    █▄  ▄███▀       
   ▄█    ███ ███    ███   ███    ███ ███   ███   ███    ███  ▄███     ███▄    ███    ███ ███▄     ▄█ 
 ▄████████▀  ████████▀    ███    █▀   ▀█   █▀    ██████████ ████       ███▄   ██████████  ▀████████▀ 
                                                                                                     

"""
    subtitle = f"""
{Fore.MAGENTA}{Style.BRIGHT}
			EASY VULNERABILITY SCANNER AUTOMATION
====================================================================================================
 		Scans: SQL Injection | XSS | LFI | CSRF | Open Redirect               		  ==
 		Logging enabled: Check 'logs/' directory for details.               	 	  ==
====================================================================================================
"""

    for line in title.splitlines():
        print(line)
        time.sleep(0.05)

    print(subtitle)

def setup_logging(tool):
    """Konfigurasi logging berdasarkan jenis scan."""
    log_dir = os.path.join(MAIN_LOG_DIR, tool)
    os.makedirs(log_dir, exist_ok=True)
    log_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"{tool}_log_{log_timestamp}.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info(f"Logging started for {tool.upper()} scan.")

def run_command_with_progress(command):
    """Menjalankan perintah CLI dan menampilkan progress bar berbasis waktu."""
    start_time = time.time()

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        elapsed_time = time.time() - start_time
        print(f"\r{Fore.YELLOW}Progress: Running... Elapsed Time: {int(elapsed_time)}s", end="", flush=True)
        time.sleep(1)

    stdout, stderr = process.communicate()
    total_time = time.time() - start_time
    print(f"\n{Fore.GREEN}Scan completed in {int(total_time)} seconds.")

    if stdout:
        logging.info(stdout.decode().strip())
    if stderr:
        logging.error(stderr.decode().strip())

def threaded_scan(tool, url, log_enabled=True):
    """Menjalankan scan untuk setiap URL."""
    if log_enabled:
        setup_logging(tool)
    command = TOOLS[tool].format(url=url)
    print(Fore.GREEN + f"\n[+] Scanning {tool.upper()} for {url}...")
    run_command_with_progress(command)

def process_urls_from_file(file_path):
    """Membaca URL dari file."""
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
            if not urls:
                print(Fore.RED + f"No valid URLs found in {file_path}.")
                sys.exit(1)
            return urls
    except FileNotFoundError:
        print(Fore.RED + f"File {file_path} not found.")
        sys.exit(1)

def run_parallel_scans(urls, tool, log_enabled=True):
    """Menjalankan scan secara paralel."""
    threads = []
    for url in urls:
        thread = threading.Thread(target=threaded_scan, args=(tool, url, log_enabled))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def main():
    print_title()

    input_type = input(Fore.CYAN + "Enter '1' for a single URL or '2' for a file with URLs: ").strip()

    if input_type == '1':
        url = input(Fore.CYAN + "Enter the target URL: ").strip()
        urls = [url]
    elif input_type == '2':
        file_path = input(Fore.CYAN + "Enter the path to the file with URLs: ").strip()
        urls = process_urls_from_file(file_path)
    else:
        print(Fore.RED + "Invalid input. Please enter '1' or '2'.")
        sys.exit(1)

    print(Fore.YELLOW + "\nSelect an option:")
    print(Fore.GREEN + "1. SQL Injection")
    print(Fore.GREEN + "2. Cross-site Scripting (XSS)")
    print(Fore.GREEN + "3. Local File Inclusion (LFI)")
    print(Fore.GREEN + "4. Cross-Site Request Forgery (CSRF)")
    print(Fore.GREEN + "5. Open Redirect")
    print(Fore.GREEN + "6. Run All Scans")

    try:
        choice = int(input(Fore.CYAN + "\nEnter your choice (1-6): ").strip())
    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a number between 1 and 6.")
        sys.exit(1)

    if choice not in range(1, 7):
        print(Fore.RED + "Invalid choice. Please enter a number between 1 and 6.")
        sys.exit(1)

    if choice == 6:
        first_tool = list(TOOLS.keys())[0]
        run_parallel_scans(urls, first_tool, log_enabled=True)

        for tool in list(TOOLS.keys())[1:]:
            run_parallel_scans(urls, tool, log_enabled=False)
    else:
        tool = list(TOOLS.keys())[choice - 1]
        run_parallel_scans(urls, tool)

    print(Fore.GREEN + f"\n[+] Scanning completed. Check '{MAIN_LOG_DIR}' for detailed logs.")

if __name__ == "__main__":
    main()
