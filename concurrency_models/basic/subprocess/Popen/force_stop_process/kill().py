"""
- Process is terminated immediately
- No cleanup chance
- Used for frozen or deadlocked processes
"""

import subprocess
import sys
import time

p = subprocess.Popen([sys.executable, "infinite_loop.py"])

time.sleep(3)

print("Force Killing Process...")
p.kill()

p.wait()
print("Process Killed with code : ", p.returncode)
