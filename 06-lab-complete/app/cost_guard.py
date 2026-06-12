from datetime import datetime, timedelta
import redis
from fastapi import HTTPException
from app.config import settings

# Connect to your Redis instance
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def check_and_record_cost(input_tokens: int, output_tokens: int) -> None:
    # 1. Generate a unique key for today (e.g., "cost:2026-06-12")
    today_key = f"cost:{datetime.now().strftime('%Y-%m-%d')}"
    
    # 2. Get current daily cost (defaults to 0.0 if key doesn't exist)
    current_cost = float(r.get(today_key) or 0.0)
    
    if current_cost >= settings.daily_budget_usd:
        raise HTTPException(503, "Daily budget exhausted. Try tomorrow.")
        
    # 3. Calculate new cost
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    
    # 4. Atomically increment in Redis
    r.incrbyfloat(today_key, cost)
    
    # 5. Automatically delete the key after 24 hours so your database stays clean
    r.expire(today_key, timedelta(hours=24))