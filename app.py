import clickhouse_connect
import time
import random
from datetime import datetime, timedelta
from config import HOST, SHARD1_PORT, SHARD2_PORT, DB, CLUSTER
from queries import (
    Q_REGIONAL_SALES, Q_TIME_RANGE, Q_USER_LOOKUP, Q_MONTHLY_TREND,
    Q_CATEGORY_STATS, Q_APPROX_DISTINCT, Q_TOP_USERS, Q_PRICE_RANGE,
    Q_CROSS_SHARD, Q_PARTITION_STATS, Q_COLUMN_SIZE, Q_CLUSTER_INFO,
    Q_MARKS_READ
)

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


def client(port=SHARD1_PORT):
    return clickhouse_connect.get_client(host=HOST, port=port, database=DB)


def execute(c, q, label):
    t0 = time.time()
    r = c.query(q)
    dt = time.time() - t0
    print(f"\n[{label}]")
    print(f"columns: {r.column_names}")
    for row in r.result_rows:
        print(row)
    print(f"rows={r.row_count} time={dt:.4f}s")
    return r


def explain_plan(c, q, label):
    print(f"\n[EXPLAIN PLAN - {label}]")
    r = c.query(f"EXPLAIN indexes=1 {q}")
    for row in r.result_rows:
        print(row[0])


def explain_pipeline(c, q, label):
    print(f"\n[EXPLAIN PIPELINE - {label}]")
    r = c.query(f"EXPLAIN PIPELINE {q}")
    for row in r.result_rows:
        print(row[0])


def shard_dist(c):
    print("\n[SHARD DISTRIBUTION]")
    for port, name in [(SHARD1_PORT, "shard-1"), (SHARD2_PORT, "shard-2")]:
        sc = clickhouse_connect.get_client(host=HOST, port=port, database=DB)
        r = sc.query("SELECT count() FROM orders_local")
        print(f"{name}: {r.result_rows[0][0]} rows")


def insert_batch(c, n=1000):
    base = datetime(2024, 6, 1)
    cols = [
        "order_id", "user_id", "product_id", "category", "region",
        "city", "price", "quantity", "order_date", "order_time", "payment_method"
    ]
    start_id = int(time.time() * 1000)
    rows = []
    for i in range(n):
        reg = random.choice(REGIONS)
        d = base + timedelta(days=random.randint(0, 60))
        t = d + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
        rows.append((
            start_id + i,
            random.randint(1, 100_000),
            random.randint(1, 5000),
            random.choice(CATEGORIES),
            reg,
            random.choice(CITIES[reg]),
            round(random.uniform(1.0, 500.0), 2),
            random.randint(1, 10),
            d.date(),
            t,
            random.choice(PAYMENTS),
        ))
    t0 = time.time()
    c.insert("orders", rows, column_names=cols)
    dt = time.time() - t0
    print(f"\n[BATCH INSERT] {n} rows in {dt:.4f}s")


def recent_query_stats(c):
    print("\n[RECENT QUERY STATS]")
    r = c.query(Q_MARKS_READ)
    for row in r.result_rows:
        q_text = row[0][:80].replace('\n', ' ')
        print(f"  query: {q_text}...")
        print(f"  read_rows={row[1]} read_bytes={row[2]} result_rows={row[3]} duration_ms={row[5]}")


def compare_index_usage(c):
    print("\n[INDEX VS FULL SCAN COMPARISON]")

    q_idx = f"""
    SELECT count() FROM {DB}.orders_local
    WHERE region = 'Asia' AND order_date >= '2023-06-01' AND order_date <= '2023-06-30'
    """
    q_no = f"""
    SELECT count() FROM {DB}.orders_local
    WHERE city = 'Tokyo'
    """

    print("-- Query using primary key (region, order_date):")
    explain_plan(c, q_idx, "primary key filter")
    t0 = time.time()
    r1 = c.query(q_idx)
    dt1 = time.time() - t0
    print(f"result={r1.result_rows[0][0]} time={dt1:.4f}s")

    print("\n-- Query NOT using primary key (city):")
    explain_plan(c, q_no, "non-key filter")
    t0 = time.time()
    r2 = c.query(q_no)
    dt2 = time.time() - t0
    print(f"result={r2.result_rows[0][0]} time={dt2:.4f}s")


def menu():
    print("\nE-Commerce Sales Analytics (ClickHouse)")
    print(" 1  Regional Sales Aggregation")
    print(" 2  Time Range Query")
    print(" 3  User Order Lookup (Bloom Filter)")
    print(" 4  Monthly Revenue Trend")
    print(" 5  Category Statistics")
    print(" 6  Approximate vs Exact COUNT DISTINCT")
    print(" 7  Top Spending Users")
    print(" 8  Price Range Filter (MinMax Index)")
    print(" 9  Cross-Shard Multi-Dim Aggregation")
    print("10  Batch Insert Demo")
    print("11  Partition Stats")
    print("12  Column Storage Size")
    print("13  Cluster Info")
    print("14  Shard Distribution")
    print("15  Recent Query Stats")
    print("16  Index vs Full Scan Comparison")
    print(" 0  Exit")
    return input("select: ").strip()


def main():
    c = client()

    while True:
        ch = menu()

        if ch == "1":
            q = Q_REGIONAL_SALES.format(db=DB)
            explain_plan(c, q, "regional sales")
            explain_pipeline(c, q, "regional sales")
            execute(c, q, "regional sales")

        elif ch == "2":
            s = input("start date (YYYY-MM-DD) [2023-06-01]: ").strip() or "2023-06-01"
            e = input("end date (YYYY-MM-DD) [2023-06-30]: ").strip() or "2023-06-30"
            q = Q_TIME_RANGE.format(db=DB, start=s, end=e)
            explain_plan(c, q, "time range")
            execute(c, q, "time range")

        elif ch == "3":
            uid = input("user_id [42]: ").strip() or "42"
            q = Q_USER_LOOKUP.format(db=DB, uid=uid)
            explain_plan(c, q, "user lookup")
            execute(c, q, "user lookup")

        elif ch == "4":
            q = Q_MONTHLY_TREND.format(db=DB)
            explain_plan(c, q, "monthly trend")
            execute(c, q, "monthly trend")

        elif ch == "5":
            q = Q_CATEGORY_STATS.format(db=DB)
            explain_plan(c, q, "category stats")
            execute(c, q, "category stats")

        elif ch == "6":
            q = Q_APPROX_DISTINCT.format(db=DB)
            execute(c, q, "approx vs exact distinct")

        elif ch == "7":
            q = Q_TOP_USERS.format(db=DB)
            explain_plan(c, q, "top users")
            execute(c, q, "top users")

        elif ch == "8":
            lo = input("min price [400]: ").strip() or "400"
            hi = input("max price [500]: ").strip() or "500"
            q = Q_PRICE_RANGE.format(db=DB, lo=lo, hi=hi)
            explain_plan(c, q, "price range")
            execute(c, q, "price range")

        elif ch == "9":
            q = Q_CROSS_SHARD.format(db=DB)
            explain_plan(c, q, "cross-shard agg")
            explain_pipeline(c, q, "cross-shard agg")
            execute(c, q, "cross-shard agg")

        elif ch == "10":
            n = input("rows to insert [1000]: ").strip() or "1000"
            insert_batch(c, int(n))

        elif ch == "11":
            q = Q_PARTITION_STATS.format(db=DB)
            execute(c, q, "partition stats")

        elif ch == "12":
            q = Q_COLUMN_SIZE.format(db=DB)
            execute(c, q, "column storage size")

        elif ch == "13":
            q = Q_CLUSTER_INFO.format(cluster=CLUSTER)
            execute(c, q, "cluster info")

        elif ch == "14":
            shard_dist(c)

        elif ch == "15":
            recent_query_stats(c)

        elif ch == "16":
            compare_index_usage(c)

        elif ch == "0":
            break


if __name__ == "__main__":
    main()
