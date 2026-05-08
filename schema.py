import clickhouse_connect
from config import HOST, SHARD1_PORT, DB, CLUSTER

def run():
    c = clickhouse_connect.get_client(host=HOST, port=SHARD1_PORT)

    c.command(f"CREATE DATABASE IF NOT EXISTS {DB} ON CLUSTER {CLUSTER}")

    c.command(f"""
        CREATE TABLE IF NOT EXISTS {DB}.orders_local ON CLUSTER {CLUSTER} (
            order_id    UInt64,
            user_id     UInt64,
            product_id  UInt32,
            category    LowCardinality(String),
            region      LowCardinality(String),
            city        LowCardinality(String),
            price       Float64,
            quantity    UInt32,
            order_date  Date,
            order_time  DateTime,
            payment_method LowCardinality(String)
        ) ENGINE = ReplicatedMergeTree(
            '/clickhouse/tables/{{shard}}/orders_local', '{{replica}}'
        )
        PARTITION BY toYYYYMM(order_date)
        ORDER BY (region, order_date, user_id)
        SETTINGS index_granularity = 8192, min_bytes_for_wide_part = 0, min_rows_for_wide_part = 0
    """)

    c.command(f"""
        ALTER TABLE {DB}.orders_local ON CLUSTER {CLUSTER}
        ADD INDEX IF NOT EXISTS idx_user user_id TYPE bloom_filter GRANULARITY 4
    """)

    c.command(f"""
        ALTER TABLE {DB}.orders_local ON CLUSTER {CLUSTER}
        ADD INDEX IF NOT EXISTS idx_price price TYPE minmax GRANULARITY 4
    """)

    c.command(f"""
        CREATE TABLE IF NOT EXISTS {DB}.orders ON CLUSTER {CLUSTER}
        AS {DB}.orders_local
        ENGINE = Distributed({CLUSTER}, {DB}, orders_local, xxHash64(user_id))
    """)

    print("schema created")

if __name__ == "__main__":
    run()
