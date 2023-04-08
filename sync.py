from rq import Queue
import redis
import os

queue = Queue(connection=redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), password=os.getenv("REDIS_PASSWORD", None)), default_timeout=3600)
# queue maximum timeout value 1000 seconds