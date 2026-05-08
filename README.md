# E-Commerce Sales Analytics (ClickHouse)

DSCI 551 Course Project, Spring 2026

## Team

- Wenxin Li
- Isabelle Du
- Xinyuan Huang

## Database

ClickHouse (columnar analytical database, MergeTree engine family)

## Prerequisites

- macOS / Linux
- Docker Desktop
- Python 3.10+

## Setup

```bash
cd ecommerce-analytics
pip3 install -r requirements.txt
docker compose up -d
sleep 10
python3 schema.py
python3 generate_data.py
python3 app.py
```

## File Structure

| File | Description |
|---|---|
| `docker-compose.yml` | 2-shard ClickHouse cluster + ZooKeeper |
| `clickhouse-config/` | Cluster topology and shard macros |
| `config.py` | Connection parameters |
| `schema.py` | Database, tables, skip indexes |
| `generate_data.py` | Synthetic dataset (1M rows) |
| `queries.py` | All SQL statements |
| `app.py` | Interactive CLI application |

## Application Features

| # | Feature | DB Internal Mapping |
|---|---|---|
| 1 | Regional sales aggregation | Columnar scan + vectorized pipeline |
| 2 | Time range query | Partition pruning + sparse index |
| 3 | User order lookup | Bloom filter skip index |
| 4 | Monthly revenue trend | Partition-level scan |
| 5 | Category statistics | Column-only read + uniqExact |
| 6 | Approx vs exact COUNT DISTINCT | HyperLogLog vs exact |
| 7 | Top spending users | Aggregation + sort |
| 8 | Price range filter | MinMax skip index |
| 9 | Cross-shard aggregation | Distributed table engine |
| 10 | Batch insert | MergeTree write path (data parts) |
| 11 | Partition stats | system.parts metadata |
| 12 | Column storage size | Compression ratio per column |
| 13 | Cluster info | system.clusters |
| 14 | Shard distribution | Row count per shard |
| 15 | Recent query stats | system.query_log |
| 16 | Index vs full scan | Primary key hit vs miss |

## Dataset

Synthetic e-commerce orders: 1,000,000 rows covering Jan 2023 to Dec 2024, with 6 regions, 30 cities, 8 categories, 100K users.

## Teardown

```bash
docker compose down
```