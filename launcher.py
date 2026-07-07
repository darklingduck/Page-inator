import os
import shutil
import subprocess
import sys
import time
import win32com.client

from pdf_utils import safe_copy, safe_copytree, log

LOCAL_DIR = r"C:\Page-Inator"
NETWORK_DIR = r"\\hwcfs01\Appdeployment\Page-Inator"

LOCAL_LAUNCHER = os.path.join(LOCAL_DIR, "Launcher.exe")
LOCAL_PAGEINATOR = os.path.join(LOCAL_DIR, "PageInator.exe")
LOCAL_BOOTSTRAP = os.path.join(LOCAL_DIR, "Bootstrap", "Bootstrap.exe")
LOCAL_VERSION = os.path.join(LOCAL_DIR, "version.txt")

NETWORK_PAGEINATOR = os.path.join(NETWORK_DIR, "PageInator.exe")
NETWORK_BOOTSTRAP = os.path.join(NETWORK_DIR, "Bootstrap")
NETWORK_VERSION = os.path.join(NETWORK_DIR, "version.txt")

FLAG_FILE = os.path.join(LOCAL_DIR, "launcher_updated.flag")
LOG_FILE = os.path.join(LOCAL_DIR, "update.log")


# ======================
# Process handling
# ======================
def is_running(process_name):
    try:
        output = subprocess.check_output("tasklist", shell=True).decode()
        return process_name.lower() in output.lower()
    except:
        return False


def kill_process(process_name):
    try:
        subprocess.call(f'taskkill /f /im "{process_name}"', shell=True)
        log(LOG_FILE, f"Killed process: {process_name}")
    except Exception as e:
        log(LOG_FILE, f"Failed to kill {process_name}: {e}")


def ensure_not_running():
    if is_running("PageInator.exe"):
        log(LOG_FILE, "Page-Inator is running, closing...")
        kill_process("PageInator.exe")


# ======================
# Shortcut creation
# ======================
def create_shortcut():
    try:
        desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
        shortcut_path = os.path.join(desktop, "Launch Page-Inator.lnk")

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.Targetpath = LOCAL_LAUNCHER
        shortcut.WorkingDirectory = LOCAL_DIR
        shortcut.save()

        log(LOG_FILE, "Shortcut created")

    except Exception as e:
        log(LOG_FILE, f"Shortcut failed: {e}")


# ======================
# Bootstrap copy
# ======================
def copy_bootstrap():
    try:
        local_bootstrap_dir = os.path.join(LOCAL_DIR, "Bootstrap")

        log(LOG_FILE, "Copying Bootstrap folder")

        if os.path.exists(local_bootstrap_dir):
            try:
                shutil.rmtree(local_bootstrap_dir)
            except:
                log(LOG_FILE, "Retrying Bootstrap delete...")
                time.sleep(1)
                shutil.rmtree(local_bootstrap_dir)

        safe_copytree(NETWORK_BOOTSTRAP, local_bootstrap_dir, "Bootstrap", LOG_FILE)

        log(LOG_FILE, "Bootstrap copied successfully")

    except Exception as e:
        log(LOG_FILE, f"Bootstrap copy failed: {e}")
        raise


# ======================
# First install
# ======================
def first_install():
    log(LOG_FILE, "=== First Install ===")

    os.makedirs(LOCAL_DIR, exist_ok=True)

    safe_copy(NETWORK_PAGEINATOR, LOCAL_PAGEINATOR, "Page-Inator executable", LOG_FILE)
    safe_copy(NETWORK_VERSION, LOCAL_VERSION, "version.txt", LOG_FILE)

    copy_bootstrap()
    create_shortcut()

    log(LOG_FILE, "Launching Bootstrap for initial setup")
    subprocess.Popen([LOCAL_BOOTSTRAP])

    time.sleep(0.5)
    sys.exit()


# ======================
# Version reading
# ======================
def read_versions(path):
    versions = {}
    with open(path) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=")
                versions[k.strip()] = v.strip()
    return versions


# ======================
# Updates
# ======================
def update_pageinator():
    log(LOG_FILE, "Updating Page-Inator")

    ensure_not_running()

    safe_copy(NETWORK_PAGEINATOR, LOCAL_PAGEINATOR, "Page-Inator executable", LOG_FILE)


def run_bootstrap():
    log(LOG_FILE, "Launcher update required")

    ensure_not_running()

    copy_bootstrap()

    log(LOG_FILE, "Waiting before launching Bootstrap")
    time.sleep(1)

    subprocess.Popen([LOCAL_BOOTSTRAP])

    time.sleep(0.5)
    sys.exit()


# ======================
# Main
# ======================
def main():
    try:
        log(LOG_FILE, "=== Launcher Started ===")

        if not os.path.exists(LOCAL_VERSION):
            first_install()

        net = read_versions(NETWORK_VERSION)
        local = read_versions(LOCAL_VERSION)

        skip_launcher = os.path.exists(FLAG_FILE)

        if not skip_launcher:
            if net.get("launcher") != local.get("launcher"):
                run_bootstrap()

        if net.get("pageinator") != local.get("pageinator"):
            update_pageinator()

        safe_copy(NETWORK_VERSION, LOCAL_VERSION, "version.txt", LOG_FILE)

        if os.path.exists(FLAG_FILE):
            os.remove(FLAG_FILE)

        log(LOG_FILE, "Launching Page-Inator")
        subprocess.Popen([LOCAL_PAGEINATOR])

        time.sleep(0.5)

        log(LOG_FILE, "=== Launcher Complete ===")

    except Exception as e:
        log(LOG_FILE, f"FATAL ERROR:\n{str(e)}")


if __name__ == "__main__":
    main()
