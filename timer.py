import threading, time

class Timer(threading.Thread):

    def __init__(self, callback, seconds):
        threading.Thread.__init__(self)
        self.callback = callback
        self.running = True
        self.seconds = seconds

    def run(self):
        time.sleep(self.seconds)
        if self.running:
            self.callback()
        self.running = False
    
    def finish(self):
        self.running = False
