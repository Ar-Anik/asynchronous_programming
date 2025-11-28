"""
subprocess.call() is a function in the Python subprocess module that is used to run a command in a separate process
and wait for it to complete. It returns the return code of the command, which is zero if the command was successful
and non-zero if it failed.

The call() function takes the same arguments as run().
"""

import sys
import subprocess

return_code = subprocess.call([sys.executable, "--version"])
"""
equivalent to :
return_code = subprocess.run([sys.executable, "--version"]).returncode 
"""

if return_code == 0:
    print("Command executed successfully.")
else:
    print("Command failed with return code", return_code)

"""
This will run the command python -–version in a separate process and wait for it to complete. The command's return 
code will be stored in the return_code variable, which will be zero if the command was successful, and non-zero if 
it failed.

subprocess.call() is useful when we want to run a command and check the return code, but do not need to capture the 
output.
"""
