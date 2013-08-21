import sys
import subprocess

PY_VERSION = sys.version_info[:2]

cmd = ["pip", "install", "pytest"]
if PY_VERSION >= (3, 3) or PY_VERSION < (3, 0):
    cmd.append("HTTPretty")

if PY_VERSION < (3, 3):
    cmd.append("mock")

ret = subprocess.call(cmd)
sys.exit(ret)
