# SYSTEM DESIGN

## 1. Purpose

The goal of this system is to address the lack of standardized and accessible data within the hospitality industry by transforming fragmented operational data into structured, monetizable data products.

Accommodation providers generate valuable operational data but rarely leverage it beyond internal use. This platform enables them to contribute their data and extract value through aggregation and optional data sharing.

At the same time, investors, analysts, and companies (data consumers) gain access to structured, aggregated, and up-to-date datasets that support decision-making, market analysis, and investment strategies.

The platform operates as a **data marketplace**, where:

* **Data Providers (Accommodation Providers):**
  * Upload historical operational data
  * Optionally allow data sharing (aggregated and/or raw)
  * Earn money via Stripe Connect when their individual data is purchased
  * Earn points when their data is used in aggregations
  * Spend earned points to benchmark against market data

* **Data Consumers (Investors / Companies):**
  * Purchase points with money
  * Receive welcome points upon registration
  * Spend points to access aggregated market reports
  * Spend points to access individual accommodation datasets
  * Use data for analysis, benchmarking, and investment decisions

### MVP Scope

The MVP focuses on building a robust data pipeline and basic marketplace capabilities:

Included:

* CSV-based data ingestion
* Batch processing and dataset generation
* Aggregated data generation with geographic pre-computation
* Unified points-based monetization system
* Data product exposure (aggregated and raw)
* Provider revenue distribution via Stripe Connect
* Basic consent management per accommodation

Excluded:

* Complex external integrations (PMS systems, APIs)
* Machine learning or predictive models
* Fully automated ingestion pipelines
* Advanced subscription systems
* Portfolio or chain-level data products


## 2. High-level Architecture

The system is composed of five main components:

* **Frontend:** User interface for uploads, browsing data products, and visualization
* **Backend API:** Orchestration layer and access control
* **PostgreSQL:** Metadata and system state
* **S3 (Data Lake):** Raw and processed data storage
* **Processing Layer:** Data transformation, aggregation, and dataset generation


## 3. Core Data Flow

### Upload Flow (Provider)

1. The user uploads a CSV file via pre-signed URL directly to S3
2. The backend registers the upload in PostgreSQL
3. A processing job is triggered asynchronously
4. The system validates and transforms the data
5. A dataset is generated and stored in S3
6. The dataset is marked as **ready**, and may later be **activated** for use in queries and aggregations

### Processing & Aggregation Flow

1. Processed datasets are standardized and stored in Parquet format
2. Geographic pre-computations are generated for key levels (country, region, city)
3. On-demand aggregations are computed at query time using active datasets
4. Aggregated outputs are stored in S3
5. Aggregation metadata is registered in PostgreSQL

### Data Product Flow

1. DataProducts are defined by the platform based on:
   * Aggregations (aggregated products) — priced in points
   * Individual datasets (raw products) — priced in points
2. DataProducts are registered in PostgreSQL
3. Access rules are applied via entitlements

### Read Flow (Consumer)

```text
Frontend → Backend API → DataProduct → (Aggregation or Dataset in S3) → Response
```

1. The frontend requests a DataProduct
2. The backend validates access permissions via entitlements
3. The backend checks points balance and deducts points
4. The backend resolves the underlying data source
5. Data is retrieved from S3
6. A structured JSON response is returned, mapped to a report template


## 4. Monetization Model

The platform uses a **unified points-based system**:

**For Consumers:**
* Purchase points with money (via Stripe)
* Receive welcome points upon registration (e.g., 1000 points)
* Spend points to access aggregated reports (200-500 points)
* Spend points to access individual accommodation data (2000+ points)

**For Providers:**
* Earn points when their data is used in aggregations
* Earn money (via Stripe Connect) when their individual data is purchased
* Spend earned points to access market reports and benchmark their performance

**Points Ledger:**
* All point movements are recorded in an immutable ledger
* Points balance is maintained at the organization level
* Full audit trail of earnings and spending

**Revenue Distribution:**
* When individual accommodation data is purchased, the provider receives a percentage via Stripe Connect
* Revenue share percentage is locked at the time of purchase for historical accuracy


## 5. Synchronization Model

* **Asynchronous:**
  * Upload processing
  * Data validation
  * Dataset generation
  * Aggregation jobs
  * Revenue distribution via Stripe

* **Synchronous:**
  * Authentication
  * Data product access
  * Metadata queries
  * Points balance checks
  * Points deduction


## 6. Main Components

### Frontend

The frontend provides:

* Upload interface for providers
* Marketplace interface for browsing data products
* Visualization of aggregated and individual data via report templates
* Access management (basic)
* Points balance display

It focuses on presentation and user interaction, consuming preprocessed data in JSON format.

### Backend API

The backend acts as the central orchestrator.

Responsibilities:

* Authentication and user management
* Organization and role handling
* Upload registration and tracking
* Pre-signed URL generation for S3 uploads
* Triggering processing jobs
* Data product management
* Access control and authorization via entitlements
* Points balance management and ledger recording
* Payment processing via Stripe
* Revenue distribution via Stripe Connect

It performs lightweight validation and delegates heavy processing to the processing layer.

### PostgreSQL

PostgreSQL is the source of truth for system state and relationships.

It stores:

* Users and organizations (with roles, points balance, and Stripe IDs)
* Accommodation metadata
* AccommodationEvent records (structural changes such as category updates, renovations, and capacity changes)
* Data sharing consent per accommodation
* Upload metadata and status
* Dataset references, status, and versioning
* Aggregation metadata
* Data products (aggregated and raw)
* Entitlements and access control
* Points ledger (immutable transaction history)
* Payment records (Stripe payments)
* Revenue distributions (payouts to providers)

PostgreSQL also stores dataset metadata required for filtering and aggregation, enabling efficient dataset selection without scanning S3.

It does not store large analytical datasets.

### S3 (Data Lake)

S3 is the primary storage layer for all data.

It contains:

* Raw uploads (CSV files)
* Processed datasets (Parquet format)
* Aggregated datasets

Example structure:

```plaintext
/raw/org_id=123/upload_id=xxx.csv
/processed/org_id=123/accommodation_id=456/year=2025/part-*.parquet
/aggregated/level=city/location=gran-canaria/year=2025/part-*.parquet
```

### Processing Layer

The processing layer runs asynchronously after uploads.

Responsibilities:

1. Schema validation
2. Data cleaning
3. Normalization into a standard format
4. Deduplication and consistency checks
5. Dataset generation (snapshot-based)
6. Geographic pre-aggregation for key levels
7. On-demand aggregation at query time
8. Writing outputs to S3


## 7. Data Storage Strategy

* **PostgreSQL:** Metadata, relationships, access control, points ledger, payment records
* **S3:** Raw data, processed datasets, aggregated datasets


## 8. Initial Technical Decisions

* **FastAPI:** High performance, strong typing with Pydantic, good fit for API-driven architecture
* **React + Recharts:** Flexible UI for dashboards and marketplace views
* **Report templates defined as JSON files** in the repository, one per context (market, accommodation)
* **Stripe:** Payment processing for point purchases
* **Stripe Connect:** Revenue distribution to providers
* **Alembic:** Database migrations with full version control


## 9. Data Governance & Access Control

The system enforces:

* Organization-level ownership of data
* Provider consent per accommodation for data sharing (aggregated and/or raw)
* Access control via entitlements per data product
* Separation between aggregated and raw data products
* Revenue share percentage locked at time of purchase for historical accuracy
* Immutable points ledger for full audit trail


## 10. Failure Handling

Failures may occur during:

* Upload validation
* Data processing
* S3 writes
* Metadata updates
* Payment processing via Stripe
* Revenue distribution via Stripe Connect

The system must support:

* Retry mechanisms
* Error logging
* Clear status reporting to users
* Payment record status tracking


## 11. Future Improvements

* Automated ingestion pipelines
* Streaming / incremental processing
* Advanced aggregation strategies
* Portfolio and chain-level data products
* Integration with external systems (PMS, APIs)
* Distributed processing (Spark, AWS Glue, EMR)
* Advanced subscription models
* Multi-currency support


