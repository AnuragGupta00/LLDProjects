from collections import deque

import threading
import time
import random
from datetime import datetime


class LeakyBucket:
    def __init__(self, max_capacity, leak_rate):
        self.max_capacity = max_capacity
        self.leak_rate = leak_rate
        self.leaky_queue = deque()
        self.THROTTLED = "THROTTLED"
        self.queue_lock = threading.Lock()
        self.queue_conditional = threading.Condition(self.queue_lock)
        self.stop_executor_event = threading.Event()
        self.request_processor = threading.Thread(target=self.process_requests)
        self.request_processor.start()


    def __del__(self):
       self.shutdown()

    def shutdown(self):
        self.stop_executor_event.set()
        if self.request_processor.is_alive():
            self.request_processor.join()

    def conditional_predicate(self):
        return len(self.leaky_queue) < self.max_capacity

    def submit(self, request):
        id = request["id"]
        time1 = request["time"]
        with self.queue_lock:
            if len(self.leaky_queue) >= self.max_capacity:
                return f"{id}-{str(time1)} -> {self.THROTTLED}"

        with self.queue_conditional:
            self.queue_conditional.wait_for(self.conditional_predicate)
            self.leaky_queue.append(request)
        return f"{id}-{time1} -> Accepted"

    def process_requests(self):
        while not self.stop_executor_event.is_set():
            with self.queue_conditional:
                temp = self.leak_rate
                while temp > 0 and len(self.leaky_queue) > 0:
                    temp -= 1
                    request = self.leaky_queue.popleft()
                    id = request["id"]
                    time1 = request["time"]
                    print(f"Resolving request {id} -> {time1}")
                    self.queue_conditional.notify()
            time.sleep(3)

        # graceful exit
        print(f"Exiting the processing")
        while len(self.leaky_queue) > 0:
            request = self.leaky_queue.popleft()
            id = request["id"]
            time1 = request["time"]
            print(f"Resolving request {id} -> {time1}")


def create_request():
    request = {"id": random.randint(1,7), "data": "Anurag", "time": datetime.now()}
    return request



if __name__ == "__main__":
    limiter = LeakyBucket(max_capacity=3, leak_rate=5)
    try:
        while True:
            req = create_request()
            resp = limiter.submit(req)
            print(resp)
            time.sleep(0.1)
    except KeyboardInterrupt:
        limiter.shutdown()

