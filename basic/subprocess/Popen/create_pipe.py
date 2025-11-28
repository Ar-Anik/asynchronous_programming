"""
Link : https://www.datacamp.com/tutorial/python-subprocess (Python Subprocess Pipe)
"""

import subprocess

ls_process = subprocess.Popen(["ls"], stdout=subprocess.PIPE, text=True)
grep_process_1 = subprocess.Popen(["grep", "sample"], stdin=ls_process.stdout, stdout=subprocess.PIPE, text=True)
grep_process_2 = subprocess.Popen(["grep", ".py"], stdin=ls_process.stdout, stdout=subprocess.PIPE, text=True)

ls_process.stdout.close()
output_1, error_1 = grep_process_1.communicate()
output_2, error_2 = grep_process_2.communicate()

print(output_1, "--", error_1)
print(output_2, "--", error_2)
