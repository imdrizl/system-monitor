
import os
import sys
import time
import socket
import shutil
import platform
import ctypes
from datetime import timedelta

# ==========================================
# SYSTEM MONITOR
# Developed by imdrizl
# Version 1.0.0
# ==========================================

BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GREY = "\033[90m"
GREEN = "\033[92m"
RESET = "\033[0m"
BOLD = "\033[1m"

START = time.time()
last_cpu = None


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def get_cpu():
    global last_cpu

    try:
        if sys.platform == "win32":
            class FILETIME(ctypes.Structure):
                _fields_ = [
                    ("low", ctypes.c_ulong),
                    ("high", ctypes.c_ulong)
                ]

            idle = FILETIME()
            kernel = FILETIME()
            user = FILETIME()

            ctypes.windll.kernel32.GetSystemTimes(
                ctypes.byref(idle),
                ctypes.byref(kernel),
                ctypes.byref(user)
            )

            def value(ft):
                return (ft.high << 32) | ft.low

            current = (
                value(idle),
                value(kernel) + value(user)
            )

        else:
            with open("/proc/stat") as file:
                values = list(map(int, file.readline().split()[1:]))

            current = (values[3], sum(values))

        if last_cpu is None:
            last_cpu = current
            return 0

        idle_delta = current[0] - last_cpu[0]
        total_delta = current[1] - last_cpu[1]
        last_cpu = current

        if total_delta <= 0:
            return 0

        return round(
            (1 - idle_delta / total_delta) * 100, 1
        )

    except Exception:
        return None


def get_memory():
    try:
        if sys.platform == "win32":
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)
                ]

            mem = MEMORYSTATUSEX()
            mem.dwLength = ctypes.sizeof(mem)

            ctypes.windll.kernel32.GlobalMemoryStatusEx(
                ctypes.byref(mem)
            )

            return mem.dwMemoryLoad

        with open("/proc/meminfo") as file:
            data = {}

            for line in file:
                key, value = line.split(":")
                data[key] = int(value.strip().split()[0])

        total = data["MemTotal"]
        available = data.get("MemAvailable", data["MemFree"])

        return round((1 - available / total) * 100, 1)

    except Exception:
        return None


def get_disk():
    total, used, free = shutil.disk_usage(
        os.path.abspath(os.sep)
    )

    return round(used / total * 100, 1), total, used


def get_uptime():
    try:
        if sys.platform == "win32":
            seconds = ctypes.windll.kernel32.GetTickCount64() / 1000
        else:
            with open("/proc/uptime") as file:
                seconds = float(file.read().split()[0])

        return str(timedelta(seconds=int(seconds))).split(".")[0]

    except Exception:
        return "Unavailable"


def bar(value, width=25):
    if value is None:
        return GREY + "N/A" + RESET

    filled = round(value / 100 * width)
    return (
        BLUE + "█" * filled +
        GREY + "░" * (width - filled) +
        RESET
    )


def panel(title, value, suffix="%"):
    if value is None:
        display = "N/A"
    else:
        display = f"{value}{suffix}"

    print(f"  {CYAN}{title:<12}{RESET} {WHITE}{display:>10}{RESET}")
    print(f"  {bar(value)}")


def dashboard():
    clear()

    cpu = get_cpu()
    memory = get_memory()
    disk, total, used = get_disk()

    hostname = socket.gethostname()
    os_name = platform.system()
    python_version = platform.python_version()

    print()
    print(f"  {BLUE}{BOLD}")
    print("  ███████╗██╗   ██╗███████╗")
    print("  ██╔════╝╚██╗ ██╔╝██╔════╝")
    print("  ███████╗ ╚████╔╝ ███████╗")
    print("  ╚════██║  ╚██╔╝  ╚════██║")
    print("  ███████║   ██║   ███████║")
    print("  ╚══════╝   ╚═╝   ╚══════╝")
    print(f"  {RESET}{GREY}REAL-TIME SYSTEM MONITORING{RESET}")
    print()
    print(f"  {GREY}{'─' * 49}{RESET}")

    print(f"  {WHITE}SYSTEM OVERVIEW{RESET}")
    print(f"  Host       : {CYAN}{hostname}{RESET}")
    print(f"  Platform   : {CYAN}{os_name} {platform.release()}{RESET}")
    print(f"  Python     : {CYAN}{python_version}{RESET}")
    print(f"  Uptime     : {CYAN}{get_uptime()}{RESET}")

    print(f"\n  {GREY}{'─' * 49}{RESET}")
    print(f"  {WHITE}RESOURCE MONITOR{RESET}\n")

    panel("CPU LOAD", cpu)
    print()
    panel("MEMORY", memory)
    print()
    panel("DISK USAGE", disk)

    print(f"\n  {GREY}{'─' * 49}{RESET}")

    print(f"  Storage    : {used // (1024**3)} GB / {total // (1024**3)} GB")
    print(f"  Session    : {int(time.time() - START)} seconds")

    print(f"\n  {GREY}{'─' * 49}{RESET}")
    print(f"  {GREEN}● SYSTEM OPERATIONAL{RESET}")
    print(f"  {GREY}Developed by imdrizl{RESET}")
    print(f"\n  {WHITE}Press CTRL+C to terminate.{RESET}")


def main():
    try:
        while True:
            dashboard()
            time.sleep(1)

    except KeyboardInterrupt:
        clear()
        print(f"\n  {BLUE}SYSTEM MONITOR{RESET} {GREY}SESSION TERMINATED.{RESET}\n")


if __name__ == "__main__":
    main()
