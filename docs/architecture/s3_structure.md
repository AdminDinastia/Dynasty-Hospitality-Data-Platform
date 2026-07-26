# S3 Storage Structure

## Overview

The platform uses a single S3 bucket (`plozeus-data`) organized following the Medallion Architecture (Bronze, Silver, Gold) to manage data progression from raw uploads to analytics-ready datasets.

**Bucket:** `plozeus-data`

**Architecture:** Medallion (Bronze → Silver → Gold)

---

## Layers

### Bronze Layer (Raw Data)

**Purpose:** Store raw CSV uploads as submitted by providers.

**Lifecycle:** 7 days (delete after successful processing)

**Structure:**
```
bronze/org_id={org_id}/upload_id={upload_id}/{filename}.csv
```

**Example:**
```
bronze/org_id=123/upload_id=a7f3c2e1-4b9d-4e8a-9f1c-6d2b8e4a5c7f/hotel_data_2024.csv
```

**Rationale:**
- `org_id`: Groups uploads by organization for access control and billing
- `upload_id`: Immutable UUID ensures traceability (metadata in PostgreSQL)
- Short TTL saves storage costs after Parquet conversion

---

### Silver Layer (Processed Datasets)

**Purpose:** Standardized, validated datasets in Parquet format ready for analysis.

**Lifecycle:** Permanent (business-critical data)

**Structure:**
```
silver/org_id={org_id}/accommodation_id={accommodation_id}/year={year}/dataset.parquet
```

**Example:**
```
silver/org_id=123/accommodation_id=456/year=2025/dataset.parquet
```

**Rationale:**
- `org_id`: Enables efficient aggregation queries at organization level (hotel chains)
- `accommodation_id`: Primary entity for individual analysis
- `year`: Partitioning for query performance (most queries filter by time)
- Parquet: Columnar format optimized for analytics (compression + fast reads)

**Partitioning benefits:**
- Query: "All hotels from chain X in 2024" → reads only `org_id=X/*/year=2024/`
- Query: "Hotel Y performance 2020-2025" → reads only `accommodation_id=Y/year=*/`

---

### Gold Layer (Analytics-Ready)

**Purpose:** Pre-computed datasets and aggregations optimized for consumption by data products.

**Lifecycle:** Permanent

**Structure:**

#### Individual Accommodation Reports
```
gold/individual/accommodation_id={accommodation_id}/year={year}/report.parquet
```

**Example:**
```
gold/individual/accommodation_id=456/year=2025/report.parquet
```

**Use case:** Raw data products (single hotel reports sold to investors)

---

#### Market Aggregations
```
gold/aggregated/{aggregation_type}/{dimension_key}={dimension_value}/.../{dimension_key}={dimension_value}/year={year}/aggregation.parquet
```

**Examples:**

**Geographic aggregation:**
```
gold/aggregated/geographic/level=city/location=gran-canaria/year=2025/aggregation.parquet
gold/aggregated/geographic/level=country/location=spain/year=2025/aggregation.parquet
```

**Chain aggregation:**
```
gold/aggregated/chain/org_id=5/year=2025/aggregation.parquet
```

**Category aggregation:**
```
gold/aggregated/category/stars=4/year=2025/aggregation.parquet
```

**Multi-dimensional aggregation:**
```
gold/aggregated/mixed/country=spain/stars=4/type=hotel/year=2025/aggregation.parquet
```

**Rationale:**
- Flexible schema: new aggregation types added without structural changes
- Mirrors `aggregations` table design (aggregation_type + parameters JSON)
- Pre-computed for fast marketplace access
- Partitioned by year for efficient queries

**Use case:** Aggregated data products (market reports sold to analysts)

---

## Complete Structure Overview

```
plozeus-data/
├── bronze/                                    # Raw uploads (TTL: 7 days)
│   └── org_id={id}/
│       └── upload_id={uuid}/
│           └── {filename}.csv
│
├── silver/                                    # Processed datasets (permanent)
│   └── org_id={id}/
│       └── accommodation_id={id}/
│           └── year={yyyy}/
│               └── dataset.parquet
│
└── gold/                                      # Analytics-ready (permanent)
    ├── individual/                            # Single accommodation
    │   └── accommodation_id={id}/
    │       └── year={yyyy}/
    │           └── report.parquet
    │
    └── aggregated/                            # Market aggregations
        └── {aggregation_type}/
            └── {key}={value}/
                └── ...
                    └── year={yyyy}/
                        └── aggregation.parquet
```

---

## Naming Conventions

### File Naming
- **Bronze:** Original filename preserved (e.g., `hotel_data_2024.csv`)
- **Silver:** `dataset.parquet` (metadata in PostgreSQL)
- **Gold Individual:** `report.parquet`
- **Gold Aggregated:** `aggregation.parquet`

### Partition Keys
- Use `key=value` format (Hive-style partitioning)
- Keys in lowercase with underscores: `accommodation_id`, `org_id`, `aggregation_type`
- Values URL-safe: replace spaces with hyphens (`gran-canaria`, not `Gran Canaria`)

---

## Data Format Standards

| Layer  | Format  | Compression | Schema Evolution |
|--------|---------|-------------|------------------|
| Bronze | CSV     | None        | N/A (raw)        |
| Silver | Parquet | Snappy      | Backward compatible |
| Gold   | Parquet | Snappy      | Backward compatible |

---

## Access Patterns

### Common Queries & Optimizations

**Query 1:** "Get all data for accommodation X"
```
Path: silver/org_id=*/accommodation_id=X/year=*
Optimization: Direct accommodation_id lookup
```

**Query 2:** "Aggregate all hotels from chain Y in 2024"
```
Path: silver/org_id=Y/accommodation_id=*/year=2024
Optimization: org_id + year partition pruning
```

**Query 3:** "Market report for Gran Canaria"
```
Path: gold/aggregated/geographic/level=city/location=gran-canaria/year=*
Optimization: Pre-computed, direct read
```

---

## Lifecycle Policies

| Layer         | Retention      | Rationale                                      |
|---------------|----------------|------------------------------------------------|
| Bronze        | 7 days        | Temporary staging; deleted after Parquet conversion |
| Silver        | Permanent      | Source of truth for historical analysis        |
| Gold          | Permanent      | Business-critical analytics and products       |

---

## Future Considerations

### Scaling
- **Multi-region replication:** Consider replicating gold layer to edge locations
- **Incremental processing:** Partition by month for more granular updates
- **Data catalog:** Add AWS Glue or Databricks Unity Catalog for discoverability

### Cost Optimization
- **Storage classes:** Move old silver data (>2 years) to S3 Glacier
- **Compression:** Test ZSTD compression for better compression ratios
- **Deduplication:** Implement content-addressable storage for common aggregations

### Advanced Aggregations
- **Real-time:** Add streaming layer (e.g., Kinesis → hot aggregations)
- **ML features:** Add `gold/features/` for pre-computed ML feature stores
- **Time-series:** Consider specialized formats (Parquet + Delta Lake) for temporal queries

---

## Design Decisions Summary

| Decision | Rationale |
|----------|-----------|
| Single bucket | Simplifies permissions and reduces operational overhead for MVP |
| Medallion architecture | Industry standard, clear data quality progression |
| org_id in silver | Enables efficient chain-level aggregations |
| Flexible gold/aggregated | Supports new aggregation types without refactoring |
| Year partitioning | Most queries filter by time; balances granularity and partition count |
| 30-day bronze TTL | Cost savings; raw data preserved in PostgreSQL metadata |
| Parquet format | Columnar, compressed, schema evolution support |

---

## Implementation Notes

### MinIO (Development)
- Endpoint: `http://minio:9000`
- Same structure as production AWS S3
- Bind mount: `./data/minio` for local inspection

### AWS S3 (Production)
- Bucket: `plozeus-data`
- Region: `eu-west-1` (or closest to primary users)
- Versioning: Enabled for silver and gold layers
- Encryption: AES-256 (SSE-S3)

---

