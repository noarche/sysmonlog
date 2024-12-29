import os
import psutil
import json
import time
from datetime import datetime, timedelta
import random
import string
from colorama import Fore, Style, init
import argparse
import cpuinfo

# Initialize colorama
init(autoreset=True)

# HOW TO USE
# Commands to run are:
#  '-nolog' for faster update and no write to log.json file.
#  '-all' to override user config and toggle all metrics as true. 
# Set the update intervals and path to save log.json below. 
#
# User-configurable settings
NOLOG_TIMER = 1.25  # Timer when '-nolog' is used
SLEEP_TIMER = 1800  # Default time interval between logs (in seconds)
OUTPUT_PATH = 'log.json'  # Default path for the output log file
MAX_LOG_ENTRIES = 0  # 0 for unlimited, >0 to limit entries in log.json

# Metrics toggle settings
settings = {
    "show_uptime": True,
    "show_cpu_info": False,
    "show_cpu_frequency": False,
    "show_cpu_cores": False,
    "show_cpu_threads": False,
    "show_disk_io": True,
    "show_disk_usage": True,
    "show_total_processes": True,
    "show_active_connections": True,
    "show_cpu_usage": True,
    "show_ram_usage": True,
    "show_network_io": False,
    "show_data_downloaded": True,
    "show_data_uploaded": True,
    "show_cpu_temperature": False,
    "show_battery_status": False,
    "show_swap_memory": False,
    "show_top_processes": False
}

# Argument parsing
parser = argparse.ArgumentParser(description="System Metrics Monitor Script")
parser.add_argument('-nolog', action='store_true', help="Do not write results to log file and set sleep timer to NOLOG_TIMER seconds")
parser.add_argument('-all', action='store_true', help="Enable all metrics regardless of individual settings")
args = parser.parse_args()

if args.nolog:
    SLEEP_TIMER = NOLOG_TIMER  # Override sleep timer when -nolog is used
    OUTPUT_PATH = None  # Disable logging to file

if args.all:
    for key in settings:
        settings[key] = True

# Function to convert bytes to megabytes
def bytes_to_mb(bytes_value):
    return round(bytes_value / (1024 * 1024), 2)

# Function to convert bytes to gigabytes
def bytes_to_gb(bytes_value):
    return round(bytes_value / (1024 * 1024 * 1024), 2)

# Function to format data size in MB or GB based on value
def format_data_size(bytes_value):
    if bytes_value >= 1024 * 1024 * 1024:  # 1 GB or greater
        return f"{bytes_to_gb(bytes_value)} GB"
    else:
        return f"{bytes_to_mb(bytes_value)} MB"

# Function to convert seconds to human-readable format
def seconds_to_human_readable(seconds):
    uptime_str = str(timedelta(seconds=int(seconds)))
    days, time_str = uptime_str.split(', ') if ', ' in uptime_str else ('0 days', uptime_str)
    days = days.split()[0]
    return f"{days} days, {time_str}"

# Function to get system metrics
def get_system_metrics():
    metrics = {}

    if settings["show_uptime"]:
        metrics["System_Uptime"] = seconds_to_human_readable(time.time() - psutil.boot_time())
    if settings["show_active_connections"]:
        metrics["Active_Connections"] = len(psutil.net_connections(kind='inet'))
    if settings["show_disk_usage"]:
        metrics["Disk_Usage%"] = psutil.disk_usage('/').percent
    if settings["show_total_processes"]:
        metrics["Total_Processes"] = len(psutil.pids())
    if settings["show_cpu_usage"]:
        metrics["CPU_Usage%"] = psutil.cpu_percent(interval=1)
    if settings["show_ram_usage"]:
        metrics["RAM_Usage%"] = psutil.virtual_memory().percent
    if settings["show_data_downloaded"]:
        metrics["Data_Downloaded"] = format_data_size(psutil.net_io_counters().bytes_recv)
    if settings["show_data_uploaded"]:
        metrics["Data_Uploaded"] = format_data_size(psutil.net_io_counters().bytes_sent)

    # CPU temperature (requires "psutil.sensors_temperatures")
    if settings["show_cpu_temperature"]:
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                metrics["CPU_Temperature"] = f"{temps['coretemp'][0].current} °C"
            else:
                metrics["CPU_Temperature"] = "N/A"
        except AttributeError:
            metrics["CPU_Temperature"] = "N/A"

    # Battery status
    if settings["show_battery_status"]:
        try:
            battery = psutil.sensors_battery()
            if battery:
                metrics["Battery_Status"] = f"{battery.percent}% {'Charging' if battery.power_plugged else 'Discharging'}"
            else:
                metrics["Battery_Status"] = "N/A"
        except AttributeError:
            metrics["Battery_Status"] = "N/A"

    # CPU frequency
    if settings["show_cpu_frequency"]:
        freq = psutil.cpu_freq()
        if freq:
            metrics["CPU_Frequency"] = f"{freq.current} MHz (Min: {freq.min}, Max: {freq.max})"
        else:
            metrics["CPU_Frequency"] = "N/A"

    # CPU core and thread count
    if settings["show_cpu_cores"]:
        metrics["CPU_Cores"] = psutil.cpu_count(logical=False)
    if settings["show_cpu_threads"]:
        metrics["CPU_Threads"] = psutil.cpu_count(logical=True)

    # CPU information
    if settings["show_cpu_info"]:
        cpu_info = cpuinfo.get_cpu_info()
        metrics["CPU_Model"] = cpu_info.get("brand_raw", "N/A")
        metrics["CPU_Architecture"] = cpu_info.get("arch", "N/A")

    # Swap memory
    if settings["show_swap_memory"]:
        swap = psutil.swap_memory()
        metrics["Swap_Usage"] = f"{swap.percent}% (Used: {format_data_size(swap.used)}, Total: {format_data_size(swap.total)})"

    # Disk I/O
    if settings["show_disk_io"]:
        disk_io = psutil.disk_io_counters()
        metrics["Disk_IO"] = f"Read: {format_data_size(disk_io.read_bytes)}, Write: {format_data_size(disk_io.write_bytes)}"

    # Network I/O
    if settings["show_network_io"]:
        net_io = psutil.net_io_counters()
        metrics["Network_IO"] = f"Sent: {format_data_size(net_io.bytes_sent)}, Received: {format_data_size(net_io.bytes_recv)}"

    # Top processes by CPU and memory usage
    if settings["show_top_processes"]:
        processes = [(p.info["name"], p.info["cpu_percent"], p.info["memory_percent"]) for p in psutil.process_iter(attrs=["name", "cpu_percent", "memory_percent"])]
        top_processes = sorted(processes, key=lambda x: (x[1], x[2]), reverse=True)[:5]
        metrics["Top_Processes"] = [{"Name": p[0], "CPU%": p[1], "Memory%": p[2]} for p in top_processes]

    return metrics

# Function to generate event ID
def generate_eventid(index):
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
    return f"{index:08d}{random_str}"

# Function to log all information to JSON
def log_metrics(event_index):
    data = {
        "eventID": generate_eventid(event_index),
        "sysMonLog": get_system_metrics(),
    }

    # Only write to file if logging is enabled
    if OUTPUT_PATH:
        existing_data = []
        if os.path.exists(OUTPUT_PATH):
            with open(OUTPUT_PATH, 'r') as log_file:
                try:
                    existing_data = json.load(log_file)
                except json.JSONDecodeError:
                    existing_data = []

        # Insert new entry at the beginning (newest at the top)
        existing_data.insert(0, data)

        # Enforce log entry limit if MAX_LOG_ENTRIES > 0
        if MAX_LOG_ENTRIES > 0:
            existing_data = existing_data[:MAX_LOG_ENTRIES]

        with open(OUTPUT_PATH, 'w') as log_file:
            json.dump(existing_data, log_file, indent=4)

    return data

# Function to clear the console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to display data in colorful format
def display_metrics(data):
    metrics = data["sysMonLog"]
    print(Fore.BLUE + "=" * 50)
    print(Fore.CYAN + "             System Metrics Monitor")
    print(Fore.BLUE + "=" * 50)
    for key, value in metrics.items():
        print(Fore.GREEN + f"{key}: " + Fore.WHITE + f"{value}")
    print(Fore.BLUE + "=" * 50)

# Main loop to continuously monitor and log metrics
try:
    print("SCRIPT IS RUNNING, Press CTRL+C to stop script.")
    event_index = 1
    while True:
        # Log metrics and display them
        logged_data = log_metrics(event_index)
        event_index += 1
        clear_console()
        display_metrics(logged_data)
        time.sleep(SLEEP_TIMER)
except KeyboardInterrupt:
    print(Fore.RED + "Monitoring stopped.")
