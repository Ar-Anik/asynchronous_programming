"""
Used when synchronous execution is required.
- Blocks the parent program
- Waits until child exits
- Collects exit code
- Reaps process (prevents zombie
"""

import subprocess
import sys

p = subprocess.Popen([sys.executable, "delayed_exit.py"])

print("Waiting for process to finish....")
p.wait()

print("Process Finished with exit code : ", p.returncode)
