import queue
import threading

"""
class ThreadPool:
    
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.threads = []
        self.tasks = queue.Queue()

    def start(self):
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.threads.append(thread)

    def worker(self):
        while True:
            task = self.tasks.get()
            if task is None:
                break
            task()
            self.tasks.task_done()

    def submit(self, task):
        self.tasks.put(task)
"""