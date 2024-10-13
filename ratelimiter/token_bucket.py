
import threading
import time
from datetime import datetime, timedelta
import random
import concurrent.futures

processed_requests = 0
throttled_requests = 0
request_lock = threading.Lock()
start_time = time.time()

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


    # multithreaded requests can be handled now
    def throttle(self, request):
        global processed_requests, throttled_requests, request_lock
        request_id = request["id"]
        last_accessed_time = request["time"]
        thread_id = request["threadId"]
        with self.bucket_lock:  #necessary for multithreaded request.
            if request_id not in self.bucket:
                self.bucket[request_id] = self.initial_capacity
                self.last_accessed[request_id] = last_accessed_time
            self.last_accessed[request_id] = last_accessed_time
            if self.bucket[request_id] <= 0:
                with request_lock:
                    throttled_requests += 1
                return f"{request_id}-{thread_id} -> {self.throttled}"
            self.bucket[request_id] -= 1
        with request_lock:
            processed_requests += 1
        data = request["data"]
        return f"{request_id}-{thread_id} -> {str(data + str(len(data)))}"


def create_request():
    thread_id = threading.current_thread().ident
    request = {"id": random.randint(1,50), "data": "Anurag", "time": datetime.now(), "threadId": thread_id}
    return request


def execute_requests(limiter):
    request = create_request()
    response = limiter.throttle(request)
    # print(response)
    time.sleep(0.5)
    return response


if __name__ == "__main__":
    print(f"Main thread id: {threading.current_thread().ident}")
    limiter = TokenBucket(initial_capacity=2, refill_rate_time=5)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as threadpool:
            while True:
                threadpool.submit(execute_requests, limiter)

                current_time = time.time()
                if current_time - start_time > 5:
                    total_requests = processed_requests + throttled_requests
                    print(f"Total = {total_requests}, Processed % = {(processed_requests / total_requests)*100}, Throttled %= {(throttled_requests / total_requests)*100} ")
                    start_time = time.time()
                    throttled_requests = 0
                    processed_requests = 0
                time.sleep(0.1)
    except KeyboardInterrupt:
        limiter.shutdown()
