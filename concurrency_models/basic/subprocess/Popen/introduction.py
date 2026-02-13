import subprocess

p = subprocess.Popen(["python", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

"""
Q : What means PIPE?
-> This pipe is a real OS-level kernel buffer, not a Python variable.

Q : What is an OS-level Kernel Buffer?
-> An OS-level kernel buffer is a region of memory managed by the operating system kernel that temporarily stores 
data when it is being transferred between hardware, processes or files.

It acts as a temporary holding area so that:
- A writer (process or device) can send data quickly
- A reader (process or device) can receive that data later
- Both can operate at different speeds without blocking immediately

This buffering mechanism is a core part of every modern operating system such as Linux, Windows and macOS.
the OS creates kernel pipe buffers like this: Child Process ──▶ Kernel Buffer ──▶ Parent Process

By default when a program is launched using Python subprocess facilities:
- The child process writes its normal output (stdout) directly to the terminal.
- The child process writes its error messages (stderr) directly to the terminal.
- The parent Python program cannot see, capture, analyze or store that output.

Writing :
stdout = subprocess.PIPE and stderr = subprocess.PIPE
It Means, Redirect both output streams from the terminal into pipes so the parent Python program can read and 
control them programmatically.

subprocess.PIPE instructs the operating system to:
- Create an inter-process communication pipe
- Connect:
    * Child process stdout → pipe → parent process
    * Child process stderr → pipe → parent process

So instead of this flow:
- Child stdout → Terminal
- Child stderr → Terminal

it becomes:
- Child stdout → PIPE → Parent Python program
- Child stderr → PIPE → Parent Python program

-> subprocess.PIPE tells Python:
Create a pipe so the parent Python program can capture the child process’s output (stdout) or error stream (stderr).

# Without PIPE
- Output goes directly to the terminal.
- The parent program cannot read or process the output.
- No ability to store or modify the output.

# With PIPE
- Output is redirected from terminal → into Python memory.
- The parent program can read, store, modify, filter, or parse it.

Terminal output → PIPE → variable → print / save / process

So subprocess.PIPE acts like a communication channel between processes.
"""

output, errors = p.communicate()

"""
# communicate() reads data from stdout & stderr
When using : stdout=subprocess.PIPE and stderr=subprocess.PIPE
the child process sends data into a pipe. Pipes have limited buffer size (typically 64 KB).
If the buffer becomes full, the child process blocks and cannot continue, causing a deadlock.

communicate() empties those buffers safely: output, errors = p.communicate()
This returns:
- output → collected STDOUT text
- errors → collected STDERR text

# communicate() waits for the process to finish
Popen() starts the process asynchronously. Meaning : p = subprocess.Popen(...)
The process runs in the background immediately. To wait for it to complete: p.communicate()
It blocks until:
- the process finishes execution
- all output is collected
- pipes are closed

Equivalent to:
- p.wait()   # wait
- read stdout
- read stderr

But communicate() does all steps safely in one call.

# communicate() prevents deadlocks
This is the most important reason. If a process prints a lot of text and the buffer fills up calling: p.stdout.read()

directly use of p.stdout.read() can cause:
- deadlock
- infinite hang
- partial output

communicate() ensures:
- pipes are drained(free) safely
- both stdout and stderr are handled together

Buffer overflow cannot happen.

# communicate() closes the pipes
After reading:
- Closes p.stdout
- Closes p.stderr
- Releases system resources
Otherwise the program may leak file descriptors.
"""

print("Output : ", output)
print("Errors : ", errors)

"""
Result :
 
Output :  usage: /Users/aubdurrobanik/.pyenv/versions/3.13.2/bin/python [option] ... [-c cmd | -m mod | file | -] [arg] ...
Options (and corresponding environment variables):
-b     : issue warnings about converting bytes/bytearray to str and comparing
         bytes/bytearray with str or bytes with int. (-bb: issue errors)
-B     : don't write .pyc files on import; also PYTHONDONTWRITEBYTECODE=x
-c cmd : program passed in as string (terminates option list)
-d     : turn on parser debugging output (for experts only, only works on
         debug builds); also PYTHONDEBUG=x
-E     : ignore PYTHON* environment variables (such as PYTHONPATH)
-h     : print this help message and exit (also -? or --help)
-i     : inspect interactively after running script; forces a prompt even
         if stdin does not appear to be a terminal; also PYTHONINSPECT=x
-I     : isolate Python from the user's environment (implies -E and -s)
-m mod : run library module as a script (terminates option list)
-O     : remove assert and __debug__-dependent statements; add .opt-1 before
         .pyc extension; also PYTHONOPTIMIZE=x
-OO    : do -O changes and also discard docstrings; add .opt-2 before
         .pyc extension
-P     : don't prepend a potentially unsafe path to sys.path; also
         PYTHONSAFEPATH
-q     : don't print version and copyright messages on interactive startup
-s     : don't add user site directory to sys.path; also PYTHONNOUSERSITE=x
-S     : don't imply 'import site' on initialization
-u     : force the stdout and stderr streams to be unbuffered;
         this option has no effect on stdin; also PYTHONUNBUFFERED=x
-v     : verbose (trace import statements); also PYTHONVERBOSE=x
         can be supplied multiple times to increase verbosity
-V     : print the Python version number and exit (also --version)
         when given twice, print more information about the build
-W arg : warning control; arg is action:message:category:module:lineno
         also PYTHONWARNINGS=arg
-x     : skip first line of source, allowing use of non-Unix forms of #!cmd
-X opt : set implementation-specific option
--check-hash-based-pycs always|default|never:
         control how Python invalidates hash-based .pyc files
--help-env: print help about Python environment variables and exit
--help-xoptions: print help about implementation-specific -X options and exit
--help-all: print complete help information and exit

Arguments:
file   : program read from script file
-      : program read from stdin (default; interactive mode if a tty)
arg ...: arguments passed to program in sys.argv[1:]

Errors :  
"""


