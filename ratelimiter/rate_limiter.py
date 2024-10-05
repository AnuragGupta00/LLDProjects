
import threading
import time


# We will implement a token bucket rate limiting algorithm here.

# First lets implement this as a standalone function.

class TokenBucket:
    def __init__(self, initial_capacity, refill_rate_time=3):
        self.bucket = {}
        self.initial_capacity = initial_capacity
        self.throttled = "THROTTLED"
        self.bucket_lock = threading.Lock()
        self.refiller_rate = 1
        self.refill_rate_time = refill_rate_time
        self.stop_refiller = False
        self.refiller_thread = threading.Thread(target=self.refiller_function)
        self.refiller_thread.start()


    def __del__(self):
        print("Deleting thread")
        self.stop_refiller = True
        self.refiller_thread.join()


    def refiller_function(self):
        while not self.stop_refiller:
            time.sleep(self.refill_rate_time)
            print(f"Refilling the tokens in the bucket every {self.refill_rate_time} seconds")
            self.bucket_lock.acquire(blocking=True)
            for k, val in self.bucket.items():
                self.bucket[k] += self.refiller_rate
                self.bucket[k] = min(self.bucket[k], self.initial_capacity)
            self.bucket_lock.release()


    def throttle(self, request):
        request_id = request["id"]
        if request_id not in self.bucket:
            self.bucket[request_id] = self.initial_capacity
        if self.bucket[request_id] <= 0:
            return f"{request_id} -> {self.throttled}"

        with self.bucket_lock:
           self.bucket[request_id] -= 1

        data = request["data"]
        return f"{request_id} -> {str(data + str(len(data)))}"








def create_request(count):
    request = {"id": str(count%5), "data": "Anurag"}
    count+=1
    return request


if __name__ == "__main__":
    limiter = TokenBucket(initial_capacity=2, refill_rate_time=5)
    count = 0
    while True:
        print(limiter.throttle(create_request(count)))
        count += 1
        count %= 5
        time.sleep(0.5)

