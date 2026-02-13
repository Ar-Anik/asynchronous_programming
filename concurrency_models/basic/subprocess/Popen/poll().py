"""
p.poll() checks the current execution state of the subprocess without blocking.
- Returns None → process still running
- Returns an integer → process already terminated
"""

import subprocess
import sys
import time

p = subprocess.Popen([sys.executable, "receive_output_gradually/slow_output.py"])

while True:
    status = p.poll()

    if status is None:
        print("Process is still running..")
        time.sleep(0.1)
    else:
        print("Process finished with exist code: ", status)
        break

"""
Q : What happens internally?
p.poll() repeatedly asks the OS: “Has this process terminated?”

Here, 
- No waiting
- No blocking
- No buffer interaction

Used for live monitoring and Used for non-blocking status check.
"""
