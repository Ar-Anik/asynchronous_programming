"""
Check Argument is a optional Boolean argument. When check=True in subprocess.run function, the function will check
the return code of the command and raise a CalledProcessError exception if the return code is non-zero.
"""

import subprocess

try:
    # result = subprocess.run(["python", "script_1.py"], capture_output=True, text=True, check=True)
    result = subprocess.run(["python", "file_does_not_exist_1.py"], capture_output=True, text=True, check=True)

    """
        Here, The first element of the list ("python") tells the operating system:
                Run the program named python
        This is exactly the Python interpreter installed on the system. like we run command in Terminal : 
                python file_does_not_exist.py
    """

    print("Argument : ", result.args)
    print("Code : ", result.returncode)
    print("Output : ", result.stdout)
    print("Error : ", result.stderr)
except subprocess.CalledProcessError as e:
    print("CalledProcessError Output : ", e.stdout)
    print("CalledProcessError Error : ", e.stderr)


output = subprocess.run(["python", "file_does_not_exist_2.py"], capture_output=True, text=True, check=False)
print("Second Output : ", output.stdout)
print("Second Error : ", output.stderr)
