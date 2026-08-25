import asyncio
import time
import argparse
import statistics
import random
from typing import List, Dict, Any
import httpx

# Configuration defaults
DEFAULT_HOST = "http://localhost:8000"
DEFAULT_USERS = 100
DEFAULT_DURATION = 60  # seconds

class LoadTestMetrics:
    def __init__(self):
        self.latencies: List[float] = []  # in milliseconds
        self.success_count: int = 0
        self.fail_count: int = 0
        self.start_time: float = 0
        self.end_time: float = 0

    def add_result(self, latency_ms: float, is_success: bool):
        self.latencies.append(latency_ms)
        if is_success:
            self.success_count += 1
        else:
            self.fail_count += 1

    def summary(self) -> Dict[str, Any]:
        total_requests = len(self.latencies)
        duration = max(self.end_time - self.start_time, 0.001)
        rps = total_requests / duration

        if self.latencies:
            sorted_latencies = sorted(self.latencies)
            avg_lat = statistics.mean(sorted_latencies)
            min_lat = sorted_latencies[0]
            max_lat = sorted_latencies[-1]
            p50 = sorted_latencies[int(len(sorted_latencies) * 0.50)]
            p90 = sorted_latencies[int(len(sorted_latencies) * 0.90)]
            p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)]
        else:
            avg_lat = min_lat = max_lat = p50 = p90 = p95 = p99 = 0.0

        return {
            "total_requests": total_requests,
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "duration_seconds": round(duration, 2),
            "rps": round(rps, 2),
            "min_ms": round(min_lat, 2),
            "max_ms": round(max_lat, 2),
            "avg_ms": round(avg_lat, 2),
            "p50_ms": round(p50, 2),
            "p90_ms": round(p90, 2),
            "p95_ms": round(p95, 2),
            "p99_ms": round(p99, 2),
        }

async def virtual_user(
    user_id: int,
    base_url: str,
    duration: float,
    metrics: LoadTestMetrics,
    stop_event: asyncio.Event
):
    """
    Simulates a single virtual user executing HTTP requests until stop_event is set.
    """
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    async with httpx.AsyncClient(base_url=base_url, limits=limits, timeout=10.0) as client:
        # Pre-authenticate or register virtual user
        email = f"loaduser_{user_id}_{random.randint(1000, 9999)}@example.com"
        password = "Password123!"
        token = None

        try:
            reg_resp = await client.post("/api/auth/register", json={
                "email": email,
                "password": password,
                "name": f"LoadUser {user_id}"
            })
            if reg_resp.status_code == 201:
                token = reg_resp.json().get("access_token")
        except Exception:
            pass

        if not token:
            try:
                login_resp = await client.post("/api/auth/login", json={
                    "email": email,
                    "password": password
                })
                if login_resp.status_code == 200:
                    token = login_resp.json().get("access_token")
            except Exception:
                pass

        headers = {"Authorization": f"Bearer {token}"} if token else {}

        endpoints = [
            ("GET", "/api/dashboard/today"),
            ("GET", "/api/dashboard/summary"),
            ("GET", "/api/water/today"),
            ("GET", "/docs"),
        ]

        while not stop_event.is_set():
            method, path = random.choice(endpoints)
            start_req = time.perf_counter()
            try:
                if method == "GET":
                    resp = await client.get(path, headers=headers)
                elif method == "POST":
                    resp = await client.post(path, json={"amount_ml": 250}, headers=headers)
                
                latency = (time.perf_counter() - start_req) * 1000.0
                is_success = resp.status_code < 400
                metrics.add_result(latency, is_success)
            except Exception:
                latency = (time.perf_counter() - start_req) * 1000.0
                metrics.add_result(latency, False)

            # Small random sleep to simulate realistic pacing (10ms - 50ms)
            await asyncio.sleep(random.uniform(0.01, 0.05))

async def run_load_test(host: str, users: int, duration: int):
    print("=" * 60)
    print(" 🚀 NUTRIGUIDE BASELINE LOAD TEST BENCHMARK")
    print("=" * 60)
    print(f" Target Host     : {host}")
    print(f" Virtual Users   : {users}")
    print(f" Duration        : {duration} seconds")
    print("=" * 60)
    print("Spawning virtual users and initializing load test...\n")

    metrics = LoadTestMetrics()
    stop_event = asyncio.Event()

    metrics.start_time = time.perf_counter()

    # Create virtual user tasks
    tasks = [
        asyncio.create_task(virtual_user(i, host, duration, metrics, stop_event))
        for i in range(users)
    ]

    # Run for specified duration
    try:
        await asyncio.sleep(duration)
    finally:
        stop_event.set()
        metrics.end_time = time.perf_counter()
        await asyncio.gather(*tasks, return_exceptions=True)

    res = metrics.summary()

    print("\n" + "=" * 60)
    print(" 📊 LOAD TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f" Total Requests Sent  : {res['total_requests']:,}")
    print(f" Successful Requests  : {res['success_count']:,}")
    print(f" Failed Requests      : {res['fail_count']:,}")
    print(f" Test Duration        : {res['duration_seconds']} sec")
    print("-" * 60)
    print(f" 🔥 Requests / Sec (RPS) : {res['rps']:,} req/sec")
    print("-" * 60)
    print(" ⏱️  RESPONSE TIME (LATENCY)")
    print(f"   • Minimum          : {res['min_ms']} ms")
    print(f"   • Average          : {res['avg_ms']} ms")
    print(f"   • Maximum          : {res['max_ms']} ms")
    print(f"   • 50th Percentile  : {res['p50_ms']} ms")
    print(f"   • 90th Percentile  : {res['p90_ms']} ms")
    print(f"   • 95th Percentile  : {res['p95_ms']} ms")
    print(f"   • 99th Percentile  : {res['p99_ms']} ms")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baseline Load Test Runner for NutriGuide Backend")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Target API host base URL")
    parser.add_argument("--users", type=int, default=DEFAULT_USERS, help="Number of concurrent virtual users")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION, help="Duration of load test in seconds")

    args = parser.parse_args()

    asyncio.run(run_load_test(args.host, args.users, args.duration))
