import threading

opponent = ""
exit = False
def exit_threads():
    global exit
    exit = True

lock_exit = threading.Lock()
