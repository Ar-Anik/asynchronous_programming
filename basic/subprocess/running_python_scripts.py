import subprocess
import sys

result = subprocess.run([sys.executable, "./script_1.py"], capture_output=True, text=True)

"""
Here, sys.executable points to the current Python interpreter.
"""

print("Arguments : ", result.args)
print("Return Code : ", result.returncode)
print("Standard Output : ", result.stdout)
print("Standard Error : ", result.stderr)

"""
Output : 
Arguments :  ['/usr/local/bin/python3.13', './script_1.py']
Return Code :  0
Standard Output :  Aubdur Rob Anik
Currently Work On ERP System
I know RDBMS

Standard Error :  
"""