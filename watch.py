"""
watch.py - Real-time terminal monitor for KEDA scaling behavior.
Shows queue length and pod count side by side.
Run this OUTSIDE the cluster: python watch.py
"""
import subprocess
import time
import os

def get_pod_count():
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-l", "app=worker", "--no-headers"],
            capture_output=True, text=True, timeout=5
        )
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        running = sum(1 for l in lines if "Running" in l)
        return len(lines), running
    except:
        return 0, 0

def get_queue_length():
    try:
        result = subprocess.run(
            ["kubectl", "exec", "deploy/redis", "--", "redis-cli", "LLEN", "order-queue"],
            capture_output=True, text=True, timeout=5
        )
        return int(result.stdout.strip())
    except:
        return -1

print("=" * 60)
print("  KEDA Scaling Monitor - FinOps Demo")
print("=" * 60)

while True:
    total_pods, running_pods = get_pod_count()
    queue_len = get_queue_length()

    bar = "█" * min(running_pods, 20)
    queue_bar = "▓" * min(queue_len // 2, 30)

    print(f"  Queue: {queue_len:>4} {queue_bar}")
    print(f"  Pods:  {running_pods:>4} {bar}")
    print("-" * 60)

    time.sleep(3)
