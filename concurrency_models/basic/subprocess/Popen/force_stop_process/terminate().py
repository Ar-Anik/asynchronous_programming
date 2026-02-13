"""
terminate() → controlled shutdown. It Allows cleanup.
By terminate function the subprocess gets a chance to exit cleanly.
"""

import subprocess
import sys
import time

p = subprocess.Popen([sys.executable, "infinite_loop.py"])

time.sleep(3)

print("Sending Terminate Signal....")
p.terminate()

p.wait()
print("Process Terminated with Code : ", p.returncode)
