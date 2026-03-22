import redis
import time
import json
import random
import os
import logging
from datetime import datetime, timezone

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger("TrafficProducer")

# Configuration
REDIS_HOST = os.getenv("REDIS_DB_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_DB_PORT", 6379))
QUEUE_NAME = os.getenv("QUEUE_NAME", "order-queue")

def generate_job_payload(order_id: int) -> str:
    """Generate a simulated JSON order payload."""
    return json.dumps({
        "order_id": order_id,
        "amount": round(random.uniform(10, 500), 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

def main() -> None:
    """Main execution loop for the load generator."""
    logger.info("Initializing synthetic traffic generator...")
    
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        logger.info(f"Connected to Redis broker at {REDIS_HOST}:{REDIS_PORT}")
    except redis.ConnectionError as e:
        logger.critical(f"Failed to connect to Redis broker: {e}")
        return

    order_id = 0
    logger.info(f"Targeting queue: '{QUEUE_NAME}'. Commencing traffic generation loop.")

    try:
        while True:
            # Simulate traffic bursts: sometimes push many, sometimes few
            batch_size = random.choice([1, 1, 2, 3, 5, 10, 20])  # occasional spikes
            
            pipeline = r.pipeline()
            for _ in range(batch_size):
                order_id += 1
                payload = generate_job_payload(order_id)
                pipeline.rpush(QUEUE_NAME, payload)
            
            pipeline.execute()
            
            queue_len = r.llen(QUEUE_NAME)
            logger.info(f"Transmitted batch of {batch_size} jobs | Current queue depth: {queue_len}")
            
            # Stochastic delay between bursts
            time.sleep(random.uniform(1.0, 3.0))
            
    except KeyboardInterrupt:
        logger.info("Traffic generator stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error during transmission: {e}")

if __name__ == "__main__":
    main()
