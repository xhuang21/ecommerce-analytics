import clickhouse_connect
import random
from datetime import datetime, timedelta
from config import HOST, SHARD1_PORT, DB

REGIONS = ["North America", "Europe", "Asia", "South America", "Africa", "Oceania"]
CITIES = {
    "North America": ["New York", "Los Angeles", "Chicago", "Toronto", "Mexico City"],
    "Europe": ["London", "Paris", "Berlin", "Madrid", "Rome"],
    "Asia": ["Tokyo", "Shanghai", "Mumbai", "Seoul", "Bangkok"],
    "South America": ["Sao Paulo", "Buenos Aires", "Lima", "Bogota", "Santiago"],
    "Africa": ["Lagos", "Cairo", "Nairobi", "Casablanca", "Johannesburg"],
    "Oceania": ["Sydney", "Melbourne", "Auckland", "Brisbane", "Perth"],
}
CATEGORIES = ["Electronics", "Clothing", "Books", "Home", "Sports", "Food", "Toys", "Beauty"]
PAYMENTS = ["Credit Card", "Debit Card", "PayPal", "Apple Pay", "Cash"]

def run(n=1_000_000):
    c = clickhouse_connect.get_client(host=HOST, port=SHARD1_PORT, database=DB)
    batch = 50_000
    base = datetime(2023, 1, 1)

    cols = [
        "order_id", "user_id", "product_id", "category", "region",
        "city", "price", "quantity", "order_date", "order_time", "payment_method"
    ]

    for off in range(0, n, batch):
        sz = min(batch, n - off)
        rows = []
        for i in range(sz):
            oid = off + i + 1
            uid = random.randint(1, 100_000)
            pid = random.randint(1, 5000)
            cat = random.choice(CATEGORIES)
            reg = random.choice(REGIONS)
            cty = random.choice(CITIES[reg])
            prc = round(random.uniform(1.0, 500.0), 2)
            qty = random.randint(1, 10)
            d = base + timedelta(days=random.randint(0, 729))
            t = d + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            pay = random.choice(PAYMENTS)
            rows.append((oid, uid, pid, cat, reg, cty, prc, qty, d.date(), t, pay))

        c.insert("orders", rows, column_names=cols)
        print(f"{off + sz}/{n}")

    print("data loaded")

if __name__ == "__main__":
    run()
