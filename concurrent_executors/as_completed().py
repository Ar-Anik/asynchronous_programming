"""
as_completed() function is a core utility in Python's concurrent.futures module. It serves as an iterator that yields
Future instances as they finish their execution, regardless of the order in which they were started. This allows a
program to process results immediately upon completion, improving the perceived performance and responsiveness of
concurrent applications.

as_completed() equivalent to below code
"""

import threading

def as_completed(future):
    # 1. Create a local copy to avoid modifying the original list
    # and to track which futures are not yet finished.
    pending = list(future)

    # 2. It acts as the central signaling hub.
    condition = threading.Condition()

    # 3. Define a 'callback' function.
    # This is the "Wake-up Call" mentioned earlier.
    def waiter_callback(finished_future):
        with condition:
            # When a future finishes, it notifies the condition variable
            condition.notify_all()

    # 4. Register the callback on every future.
    # The Executor will call 'waiter_callback' automatically when a task ends.
    for f in pending:
        if f.done():
            continue
        f.add_done_callback(waiter_callback)

    # 5. The main loop that yields finished futures
    while pending:
        with condition:
            # Identify which futures are actually done right now
            done_now = [f for f in pending if f.done()]

            if not done_now:
                # If nothing is done, "Sleep" here (Block).
                # The thread releases the lock and waits for condition.notify_all()
                condition.wait()
                # Once woken up, re-check which are done
                done_now = [f for f in pending if f.done()]

            # 6. Yield the finished ones and remove them from the pending list
            for f in done_now:
                pending.remove(f)
                yield f

"""
Imagine a Restaurant scenario where a Waiter (the main program) is waiting for Chefs (background threads) to finish 
cooking different dishes.

Instead of walking into the kitchen every 5 seconds to check if the food is ready, the Waiter uses a Bell. This "Bell" 
is the threading.Condition()

2. The Signaling Hub: threading.Condition()
condition = threading.Condition() is an object that allows threads to talk to each other. It has two main function:

-> .wait(): Tells a thread to sit down, close its eyes, and stop doing anything until it hears a signal.

-> .notify_all(): Sends a signal (rings the bell) to wake up any thread that is currently waiting.
"""

"""
3. waiter_callback it's a callback function, it have a part:
    with condition:
        condition.notify_all()

Q : How does `with condition:` actually work, and how is it different from a standard if statement?
-> In standard programming, an if statement is a decision point. If the condition is false, the program simply skips the 
code block and moves to the next line. 

However, `with condition:` is a gatekeeper. It manages a "Lock" (or a "Key"). When a thread reaches this line, it doesn't 
check for a True/False value; it checks for availability.

Imagine a room with only one key. When Thread A reaches `with condition:`, it tries to take the key. If it succeeds, it 
enters the room and locks the door. If Thread B arrives while Thread A is inside, Thread B cannot skip the block. It is 
forced to pause (block) and wait in a line outside the door.

This ensures that only one thread can execute the "sensitive" code (like signaling a status change) at a time, preventing 
"Race Conditions" where multiple threads try to update the same data simultaneously and cause a crash.


Q : What is the "Magic Trick" of the wait() method in as_completed() function?
-> The biggest challenge in multithreading is avoiding a "Deadlock"—a situation where everyone is waiting and no one can move.

When the main thread (the one running the as_completed loop) calls condition.wait(), it does something counter-intuitive:
1. Releases the Key: Even though it is inside the with block, it "drops" the key back on the table.
2. Goes to Sleep: The thread enters a deep-sleep state where it uses zero CPU.

By dropping the key, it allows a background thread (the one downloading the flag) to grab that same key, enter its own 
`with condition:` block, and ring the bell (notify_all). 
If the main thread kept the key in its pocket while sleeping, the background threads would wait outside the door forever 
and the program would freeze.


Q : How do wait() and notify_all() work together to create an efficient loop?
-> This pair of methods creates a highly efficient "Signal and Response" system.

1. The Signal (notify_all): When a background task finishes, it briefly grabs the key, "rings the bell" using notify_all() 
and leaves. This signal tells the computer: "Something is ready!"

2. The Response (wait): The main thread, which was sleeping, hears the bell. It immediately tries to re-acquire the key. 
Once it has the key, it checks the list of tasks, finds the one that finished, and gives it to the for loop.

This process is much better than "Polling" (checking if task.done() over and over). In this system, the main thread 
stays 100% silent and uses no power until the exact moment a background thread finishes its work.
"""

"""
5. Main Part

-> `while pending:` block
The pending variable is a list containing all the Future objects (tasks) that have not been finished and yielded yet.
The loop continues as long as there is at least one task left in the list. Once every task is removed from pending, the 
loop ends, and the generator closes.

-> `with condition:` block
Before the thread can check the status of any task, it must acquire the Internal Lock of the condition object.
- Mutual Exclusion: Only one thread can be "inside" this block at a time. This prevents a background thread from trying 
to signal a completion at the exact same microsecond the main thread is trying to read the list.
- Think of this as the thread grabbing a "Key" to enter a restricted room where the status data is kept.

-> `done_now = [....]` block
Inside the room, the thread immediately scans the pending list using a list comprehension. Here have : 
- f.done(): This is a non-blocking check. It returns True if the task is finished (successfully or with an error) and 
False if it is still running.
- Scenario A: If tasks were already finished before the thread entered the block, done_now will contain those tasks.
- Scenario B: If the work is still in progress, done_now will be an empty list.

-> If done_now is empty, the thread reaches the `if not done_now:`
When condition.wait() is called, three actions happen automatically:
- Release: The thread puts the "Key" (lock) back on the hook.
- Block: The thread enters a suspended state (sleep). It stops execution exactly at this line.
- Waking Up: The thread stays asleep until a background worker thread calls condition.notify_all().

- The Re-Check:
Once woken up, the thread must re-acquire the Key before it can move to the next line. Once it has the Key, it runs 
the inventory check a second time: done_now = [f for f in pending if f.done()]. This time, it is guaranteed to find 
at least one finished task.

-> yield f and remove
Once the thread has a list of finished tasks (done_now), it processes them one by one.
"""
