"""
check_output is a function in the subprocess module that is similar to run(), but it only returns the standard output
of the command, and raises a CalledProcessError exception if the return code is non-zero.

The check_output() function takes the same arguments as run().
"""

import subprocess
import sys

try:
    output = subprocess.check_output([sys.executable, "--version"], text=True)
    print(output)
except subprocess.CalledProcessError as e:
    print(f"Command failed with return code {e.returncode}")

