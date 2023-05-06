from q2terminal.q2terminal import Q2Terminal
import sys
import os
from packaging import version
from tkinter import messagebox

if "win32" in sys.platform:
    python = "py"
else:
    python = "python3"

messagebox_title = "q2rad launcher error"

t = Q2Terminal(echo=True)
python_version = t.run(f"{python} --version")[0].lower().replace("python ", "")

if t.exit_code != 0:
    messagebox.showerror(
        messagebox_title,
        "Python was not found, go to www.python.org ",
    )
    exit(1)

if version.parse(python_version) < version.parse("3.8.1"):
    messagebox.showerror(
        messagebox_title,
        "Python version must at least 3.8.1",
    )
    exit(2)
    
if not os.path.isdir("q2rad"):