import os
import shutil
import subprocess
import time

LOCAL_DIR = r"C:\Page-Inator"
NETWORK_DIR = r"\\hwcfs01\Appdeployment\Page-Inator"

LOCAL_LAUNCHER = os.path.join(LOCAL_DIR, "Launcher.exe")
NETWORK_LAUNCHER = os.path.join(NETWORK_DIR, "Launcher.exe")

FLAG_FILE = os.path.join(LOCAL_DIR, "launcher_updated.flag")
LOG_FILE = os.path.join(LOCAL_DIR, "update.log")

MAX_LOG_SIZE = 200 * 1024


def log(message):
    try:
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()

            trimmed = lines[len(lines)//2:]

            with open(LOG_FILE, "w") as f:
                f.writelines(trimmed)

        with open(LOG_FILE, "a") as f:
            f.write(message + "\n")

    except:
        pass


def main():
    try:
        log("=== Bootstrap Started ===")

        temp = LOCAL_LAUNCHER + ".new"

        log("Copying Launcher")
        shutil.copy2(NETWORK_LAUNCHER, temp)

        time.sleep(1)

        if os.path.exists(LOCAL_LAUNCHER):
            log("Removing old Launcher")
            os.remove(LOCAL_LAUNCHER)

        log("Activating new Launcher")
        os.rename(temp, LOCAL_LAUNCHER)

        open(FLAG_FILE, "w").close()

        log("Launching new Launcher")
        subprocess.Popen([LOCAL_LAUNCHER])

        time.sleep(0.5)

        log("=== Bootstrap Complete ===")

    except Exception as e:
        log(f"ERROR: {str(e)}")


if __name__ == "__main__":
    main()
