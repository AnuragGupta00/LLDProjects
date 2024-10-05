
import threading
import time
from datetime import datetime, timedelta
import random

class TokenBucket:
    def __init__(self, initial_capacity, refill_rate_time=3, ttl=10):
        self.bucket = {}
        self.last_accessed = {}
        self.expire_after = ttl
        self.initial_capacity = initial_capacity
        self.throttled = "THROTTLED"
        self.bucket_lock = threading.Lock()
        self.refiller_rate = 1
        self.refill_rate_time = refill_rate_time
        self.stop_refiller_event = threading.Event()
        self.refiller_thread = threading.Thread(target=self.refiller_function)
        self.refiller_thread.start()


    def __del__(self):
       self.shutdown()

    def shutdown(self):
        self.stop_refiller_event.set()
        if self.refiller_thread.is_alive():
            self.refiller_thread.join()

    def remove_expired_entries(self):
        with self.bucket_lock:
            current_time = datetime.now()
            request_ids = [k for k in self.last_accessed.keys()
                           if (current_time - self.last_accessed[k]).__gt__(timedelta(seconds=self.expire_after))]
            for request_id in request_ids:
                print(f"Deleting {request_id} from the bucket")
                del self.bucket[request_id]
                del self.last_accessed[request_id]

    def refiller_function(self):
        while not self.stop_refiller_event.is_set():
            time.sleep(self.refill_rate_time)
            self.remove_expired_entries()
            print(f"Refilling the tokens in the bucket every {self.refill_rate_time} seconds")
            self.bucket_lock.acquire(blocking=True)
            for k, val in self.bucket.items():
                self.bucket[k] += self.refiller_rate
                self.bucket[k] = min(self.bucket[k], self.initial_capacity)
            self.bucket_lock.release()
        print(f"Shutting down re-filler thread")



    def throttle(self, request):
        request_id = request["id"]
        last_accessed_time = request["time"]

        if request_id not in self.bucket:
            self.bucket[request_id] = self.initial_capacity
            self.last_accessed[request_id] = last_accessed_time
        self.last_accessed[request_id] = last_accessed_time
        if self.bucket[request_id] <= 0:
            return f"{request_id} -> {self.throttled}"

        with self.bucket_lock:
           self.bucket[request_id] -= 1

        data = request["data"]
        return f"{request_id} -> {str(data + str(len(data)))}"


def create_request():
    request = {"id": random.randint(1,7), "data": "Anurag", "time": datetime.now()}
    return request


if __name__ == "__main__":
    limiter = TokenBucket(initial_capacity=2, refill_rate_time=5)
    try:
        while True:
            print(limiter.throttle(create_request()))
            time.sleep(0.5)
    except KeyboardInterrupt:
        limiter.shutdown()
