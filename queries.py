Q_REGIONAL_SALES = """
SELECT region, sum(price * quantity) AS total_sales, count() AS order_count
FROM {db}.orders
GROUP BY region
ORDER BY total_sales DESC
"""

Q_TIME_RANGE = """
SELECT order_id, user_id, category, price, quantity, order_date
FROM {db}.orders
WHERE order_date >= '{start}' AND order_date <= '{end}'
ORDER BY order_date
LIMIT 100
"""

Q_USER_LOOKUP = """
SELECT order_id, category, price, quantity, order_date
FROM {db}.orders
WHERE user_id = {uid}
ORDER BY order_date DESC
LIMIT 50
"""

Q_MONTHLY_TREND = """
SELECT toYYYYMM(order_date) AS month, sum(price * quantity) AS revenue, count() AS orders
FROM {db}.orders
GROUP BY month
ORDER BY month
"""

Q_CATEGORY_STATS = """
SELECT category,
       sum(price * quantity) AS total_sales,
       avg(price) AS avg_price,
       count() AS order_count,
       uniqExact(user_id) AS unique_users
FROM {db}.orders
GROUP BY category
ORDER BY total_sales DESC
"""

Q_APPROX_DISTINCT = """
SELECT uniqHLL12(user_id) AS approx_unique,
       uniqExact(user_id) AS exact_unique
FROM {db}.orders
"""

Q_TOP_USERS = """
SELECT user_id, sum(price * quantity) AS total_spent, count() AS order_count
FROM {db}.orders
GROUP BY user_id
ORDER BY total_spent DESC
LIMIT 20
"""

Q_PRICE_RANGE = """
SELECT order_id, user_id, category, region, price, quantity
FROM {db}.orders
WHERE price >= {lo} AND price <= {hi}
ORDER BY price DESC
LIMIT 100
"""

Q_CROSS_SHARD = """
SELECT region, category,
       sum(price * quantity) AS sales,
       count() AS orders,
       uniqExact(user_id) AS users
FROM {db}.orders
GROUP BY region, category
ORDER BY sales DESC
LIMIT 50
"""

Q_PARTITION_STATS = """
SELECT partition, count() AS parts, sum(rows) AS total_rows, sum(bytes_on_disk) AS disk_bytes
FROM system.parts
WHERE database = '{db}' AND table = 'orders_local' AND active
GROUP BY partition
ORDER BY partition
"""

Q_COLUMN_SIZE = """
SELECT column,
       sum(column_data_compressed_bytes) AS compressed,
       sum(column_data_uncompressed_bytes) AS uncompressed,
       round(sum(column_data_uncompressed_bytes) / sum(column_data_compressed_bytes), 2) AS ratio
FROM system.parts_columns
WHERE database = '{db}' AND table = 'orders_local' AND active
GROUP BY column
ORDER BY compressed DESC
"""

Q_CLUSTER_INFO = """
SELECT shard_num, replica_num, host_name, port
FROM system.clusters
WHERE cluster = '{cluster}'
"""

Q_MARKS_READ = """
SELECT query,
       read_rows, read_bytes,
       result_rows, result_bytes,
       query_duration_ms
FROM system.query_log
WHERE type = 'QueryFinish'
  AND query_kind = 'Select'
  AND event_time > now() - INTERVAL 60 SECOND
ORDER BY event_time DESC
LIMIT 5
"""

Q_INSERT_BATCH = """
INSERT INTO {db}.orders VALUES
"""
