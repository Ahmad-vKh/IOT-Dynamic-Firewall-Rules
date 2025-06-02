# ****************************************************************************************
#  File Name      : resources_log.py
#  Version        : 1.1
#  Description    : This script displays and logs the cpu and ram values with separate
#                   date & time
#  Authors        : Ahmad, Zaid, Omar
#  Target         : Raspberry pi 4 & 5
#  Last Updated   : 28 April 2025
#  Libraries Used : psutil, time, csv, os
#  Extra Notes    : Requires: psutil install
# ****************************************************************************************

import psutil
import time
import csv
import os

# ======= Configuration =======
T = 10  # Time interval in seconds
LOG_FILE = "system_stats_log.csv"
scheduled_time_set = "19:20:00"  # <-- Set the desired start time here to start
# =============================


def initialize_log_file():
    """Create log file and header if it doesn't exist."""
    if not os.path.isfile(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Time", "CPU (%)", "RAM (%)"])


def log_system_stats(current_date, current_time, cpu, ram):
    """Append CPU and RAM stats to the CSV log file."""
    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([current_date, current_time, cpu, ram])


def monitor_system():
    """Main monitoring loop for CPU and RAM."""
    initialize_log_file()

    try:
        print("\nSystem Resource Monitoring Started (CPU & RAM)\n")
        while True:
            current_date = time.strftime("%Y-%m-%d")
            current_time = time.strftime("%H:%M:%S")
            cpu_percent = psutil.cpu_percent()
            ram_percent = psutil.virtual_memory().percent

            print(
                f"[DATE: {current_date}] [TIME: {current_time}] CPU: {cpu_percent:.1f}% | RAM: {ram_percent:.1f}%"
            )

            log_system_stats(current_date, current_time, cpu_percent, ram_percent)

            time.sleep(T)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


def wait_until(start_time_str):
    """Wait until the system clock reaches the specified start time (HH:MM:SS)."""
    print(f"Waiting until {start_time_str} to start monitoring...")
    while True:
        now = time.strftime("%H:%M:%S")
        if now >= start_time_str:
            break
        time.sleep(1)


if __name__ == "__main__":
    # Change this to your desired start time
    scheduled_time = scheduled_time_set  # <-- Set the desired start time here to start
    wait_until(scheduled_time)
    monitor_system()
