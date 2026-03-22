import redis
import time
import json
import os
import logging
from typing import Optional, Dict, Any

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger("QueueWorker")

# Configuration
REDIS_HOST = os.getenv("REDIS_DB_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_DB_PORT", 6379))
QUEUE_NAME = os.getenv("QUEUE_NAME", "order-queue")
WORKER_ID = os.getenv("HOSTNAME", "local-worker")

def process_job(job: Dict[str, Any]) -> None:
    """Simulate processing an order containing payload data."""
    order_id = job.get("order_id", "unknown")
    amount = job.get("amount", 0.0)
    
    # Simulate processing time based on order complexity
    process_time = 0.5 + (amount / 500)
    time.sleep(process_time)
    
    logger.info(f"Processed Order #{order_id} (${amount}) in {process_time:.2f}s")

def get_redis_client() -> redis.Redis:
    """Initialize and return a Redis client."""
    try:
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        # Ping to verify connection immediately
        client.ping()
        logger.info(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return client
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis at {REDIS_HOST}:{REDIS_PORT}: {e}")
        raise

def main() -> None:
    """Main worker loop execution."""
    logger.info(f"Worker [{WORKER_ID}] initialized.")
    logger.info(f"Listening for jobs on queue: '{QUEUE_NAME}'")
    
    try:
        r = get_redis_client()
    except Exception:
        logger.critical("Cannot start worker without Redis connection. Exiting...")
        return

    while True:
        try:
            # BLPOP: blocking pop, waits for a job (timeout 5s)
            result: Optional[tuple] = r.blpop(QUEUE_NAME, timeout=5)
            
            if result:
                _, job_data = result
                job = json.loads(job_data)
                process_job(job)
            else:
                logger.debug(f"Worker [{WORKER_ID}] idle, queue empty...")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode job payload: {e}")
        except redis.RedisError as e:
            logger.error(f"Redis communication error: {e}")
            time.sleep(2) # Backoff before retrying
        except KeyboardInterrupt:
            logger.info("Worker shutting down gracefully...")
            break

if __name__ == "__main__":
    main()
