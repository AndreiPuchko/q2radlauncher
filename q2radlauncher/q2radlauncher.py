from q2terminal.q2terminal import Q2Terminal
import sys
import os
from packaging import version
from tkinter import messagebox
from q2splash import Q2Splash, GREEN, RED, RESET
import subprocess
import urllib.request
import logging
import time
import webbrowser


if "darwin" in sys.platform:
    path = sys.argv[0].split("/Contents/MacOS")[0]
    path = os.path.dirname(path)
    os.chdir(path)

start_dir = os.path.abspath(".")

messagebox_title = "q2rad launcher"

py3bin = os.path.abspath(
    f"""q2rad/q2rad/{"Scripts" if "win32" in sys.platform else "bin"}/python"""
)
code_string = "from q2rad.q2rad import main;main()"


def mess(text):
    messagebox.showerror(
        messagebox_title,
        text,
    )


def run_q2rad():
    try:
        os.chdir("q2rad")
        if "win32" not in sys.platform:
            os.execv(py3bin, [py3bin, "-c", code_string])
        else:
            subprocess.Popen(
                ["powershell", f'&"{py3bin}w"', "-c", f'"{code_string}"'],
                start_new_session=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        return True
    except Exception as e:
        print(e)
        os.chdir(start_dir)
    return False


logging.basicConfig(
    filename="q2launcher.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="[%(asctime)s] - %(message)s",
)


class launcher:
    def __init__(self, splash: Q2Splash = None):
        if "win32" in sys.platform:
            self.python = "py"
        else:
            self.python = "python3"

        self.q2rad_folder = "./q2rad"
        self.bin_folder = "Scripts" if "win32" in sys.platform else "bin"
        self.py3bin = os.path.abspath(
            f"{self.q2rad_folder}/q2rad/{self.bin_folder}/python"
        )

        self.splash = splash
        self.remove_temp_file()
        self.t = Q2Terminal(callback=self.terminal_callback)
        self.put(GREEN + "Starting q2rad..." + RESET)

        if run_q2rad():
            self.exit()

        self.splash.centerWindow("70%", "50%")
        self.put(RED + "q2rad did not start...")

        self.put(GREEN + "Checking python...")
        time.sleep(0.5)
        if self.check_python() == False:
            self.splash.close()
            sys.exit()

        self.put(GREEN + "Installing q2rad...")
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/AndreiPuchko/q2rad/main/install/get-q2rad.py",
            "_tmp.py",
        )

        self.t.run(f"{self.python} _tmp.py")
        print("Done...")
        self.remove_temp_file()

        self.exit()

    def remove_temp_file(self):
        if os.path.isfile("_tmp.py"):
            os.remove("_tmp.py")

    def put(self, text):
        if self.splash:
            self.splash.put(text)
        else:
            print(text)

    def exit(self, exit_code=0):
        self.put(None)
        sys.exit(exit_code)

    def hide(self):
        self.put("__hide__")

    def show_splash(self):
        self.put("__show__")

    def terminal_callback(self, text):
        if text in ["True", "False", "0", "1"]:
            return
        self.put(text)
        if "Failed to" in text:
            self.put("__error__")

    def check_python(self):
        self.put(GREEN + "Checking python version...")
        python_version = (
            self.t.run(f"{self.python} --version")[0].lower().replace("python ", "")
        )

        if self.t.exit_code != 0:
            self.splash.hide()
            mess("Python was not found, please install and try again.")
            webbrowser.open("python.org/downloads")
            return False

        if version.parse(python_version) < version.parse("3.8.1"):
            self.splash.hide()
            mess("Python version must be at least 3.8.1")
            webbrowser.open("python.org/downloads")
            return False
        return True

    def set_timeout(self, timeout=0):
        if self.splash:
            self.splash.set_timeout(timeout)


def worker(splash):
    launcher(splash)


if run_q2rad():
    sys.exit(0)
else:
    Q2Splash(worker=worker, width="15%", height="15%")
