import asyncio
from datetime import datetime, timedelta
import random


class TokenBucketAsync:
    def __init__(self, refill_rate = 1, max_capacity = 5, ttl=10):
        self.bucket = {}
        self.last_accessed = {}
        self.bucket_async_lock = asyncio.Lock()
        self.expire_after = ttl
        self.refill_rate = refill_rate
        self.refill_rate_time = 5
        self.max_capacity = max_capacity
        self.refiller_stop_event = asyncio.Event()
        self.throttled = "THROTTLED"
        self.refiller_task = None


    async def start_refiller(self):
        self.refiller_task = asyncio.create_task(self.refiller_coroutine())

    async def stop_refiller(self):
        self.refiller_stop_event.set()
        await self.refiller_task


    async def remove_expired_entries(self):
        async with self.bucket_async_lock:
            current_time = datetime.now()
            request_ids = [k for k in self.last_accessed.keys()
                           if (current_time - self.last_accessed[k]).__gt__(timedelta(seconds=self.expire_after))]
            for request_id in request_ids:
                print(f"Deleting {request_id} from the bucket")
                del self.bucket[request_id]
                del self.last_accessed[request_id]


    async def throttle(self, request):
        id = request["id"]
        time = request["time"]

        async with self.bucket_async_lock:
            if id not in self.bucket:
                self.bucket[id] = self.max_capacity
                self.last_accessed[id] = time
            self.last_accessed[id] = time
            if self.bucket[id] <= 0:
                return f"{id} -> {self.throttled}"
            self.bucket[id] -= 1

        data = request["data"]
        return f"{id} -> {str(data + str(len(data)))}"

    async def refiller_coroutine(self):
        while not self.refiller_stop_event.is_set():
            await asyncio.sleep(self.refill_rate_time)
            await self.remove_expired_entries()
            print(f"Refilling the tokens in the bucket every {self.refill_rate} seconds -> {datetime.now()}")
            async with self.bucket_async_lock:
                for k, val in self.bucket.items():
                    self.bucket[k] += self.refill_rate
                    self.bucket[k] = min(self.bucket[k], self.max_capacity)
        print(f"Shutting down re-filler thread")

def create_request():
    request = {"id": random.randint(1,7), "data": "Anurag", "time": datetime.now()}
    return request


async def main():
    limiter = TokenBucketAsync(max_capacity=2, refill_rate=5)
    await limiter.start_refiller()
    try:
        while True:
            x = await limiter.throttle(create_request())
            print(x)
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print(f"Stopping re-filler thread")
        await limiter.stop_refiller()


if __name__ == "__main__":
    asyncio.run(main())

######## CLAUDE ###########
"""
import asyncio
from datetime import datetime, timedelta
import random

class AsyncTokenBucket:
    def __init__(self, refill_rate=1, max_capacity=5, ttl=10):
        self.bucket = {}
        self.last_accessed = {}
        self.bucket_lock = asyncio.Lock()
        self.expire_after = ttl
        self.refill_rate = refill_rate
        self.refill_interval = 5
        self.max_capacity = max_capacity
        self.throttled = "THROTTLED"
        self.stop_event = asyncio.Event()
        self.refiller_task = None

    async def start(self):
        self.refiller_task = asyncio.create_task(self.refiller_coroutine())

    async def stop(self):
        self.stop_event.set()
        if self.refiller_task:
            await self.refiller_task

    async def remove_expired_entries(self):
        async with self.bucket_lock:
            current_time = datetime.now()
            expired = [k for k, v in self.last_accessed.items()
                       if (current_time - v) > timedelta(seconds=self.expire_after)]
            for request_id in expired:
                print(f"Deleting {request_id} from the bucket")
                del self.bucket[request_id]
                del self.last_accessed[request_id]

    async def throttle(self, request):
        id = request["id"]
        time = request["time"]

        async with self.bucket_lock:
            if id not in self.bucket:
                self.bucket[id] = self.max_capacity
                self.last_accessed[id] = time
            self.last_accessed[id] = time
            if self.bucket[id] <= 0:
                return f"{id} -> {self.throttled}"
            self.bucket[id] -= 1

        data = request["data"]
        return f"{id} -> {str(data + str(len(data)))}"

    async def refiller_coroutine(self):
        while not self.stop_event.is_set():
            await asyncio.sleep(self.refill_interval)
            await self.remove_expired_entries()
            print(f"Refilling the tokens in the bucket every {self.refill_interval} seconds")
            async with self.bucket_lock:
                for k in self.bucket:
                    self.bucket[k] = min(self.bucket[k] + self.refill_rate, self.max_capacity)
        print("Refiller coroutine stopped")

def create_request():
    return {"id": random.randint(1, 7), "data": "Anurag", "time": datetime.now()}

async def main():
    limiter = AsyncTokenBucket(max_capacity=2, refill_rate=1)
    await limiter.start()
    try:
        for _ in range(20):  # Process 20 requests
            result = await limiter.throttle(create_request())
            print(result)
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        print("Main task cancelled")
    finally:
        await limiter.stop()
        print("Limiter stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down.")
"""