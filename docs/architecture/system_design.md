# SYSTEM DESIGN 

## 1. Purpose

The goal of this system is to address the lack of standardized and accessible data within the hotel industry by transforming fragmented operational data into structured, monetizable data products.

Hotels (data providers) generate valuable operational data but rarely leverage it beyond internal use. This platform enables them to contribute their data and extract value through aggregation and optional data sharing.

At the same time, investors, analysts, and companies (data consumers) gain access to structured, aggregated, and up-to-date datasets that support decision-making, market analysis, and investment strategies.

The platform operates as a **data marketplace**, where:

* **Data Providers (Hotels):**

  * Upload historical operational data
  * Optionally allow data sharing (aggregated and/or raw)
  * Contribute to aggregated insights

* **Data Consumers (Investors / Companies):**

  * Access aggregated data products
  * Optionally purchase access to more granular datasets
  * Use data for analysis, benchmarking, and decision-making


### MVP Scope

The MVP focuses on building a robust data pipeline and basic marketplace capabilities:

Included:

* CSV-based data ingestion
* Batch processing and dataset generation
* Aggregated data generation
* Data product exposure
* Basic access control

Excluded:

* Complex external integrations (PMS systems, APIs like Amadeus)
* Machine learning or predictive models
* Fully automated ingestion pipelines
* Advanced pricing or subscription systems


## 2. High-level Architecture

The system is composed of five main components:

* **Frontend:** User interface for uploads, browsing data products, and visualization
* **Backend API:** Orchestration layer and access control
* **PostgreSQL:** Metadata and system state
* **S3 (Data Lake):** Raw and processed data storage
* **Processing Layer:** Data transformation, aggregation, and dataset generation


## 3. Core Data Flow

### Upload Flow (Provider)

1. The user uploads a CSV file (via pre-signed URL directly to S3)
2. The backend registers the upload in PostgreSQL
3. A processing job is triggered asynchronously
4. The system validates and transforms the data
5. A dataset is generated and stored in S3
6. The dataset is marked as **ready**, and may later be **activated** for use in queries and aggregations


### Processing & Aggregation Flow

1. Processed datasets are standardized and stored in Parquet format
2. Aggregation jobs combine multiple datasets across providers
3. Aggregation is performed based on predefined configurations (metric, dimensions, time granularity)
4. Aggregated outputs are stored in S3
5. Aggregations are registered and made available for DataProduct creation


### Data Product Flow

1. DataProducts are defined based on:

   * Aggregations (aggregated products)
   * Datasets (raw products, if allowed)

2. DataProducts are registered in PostgreSQL

3. Access rules are applied (free, granted, or purchased)


### Read Flow (Consumer)

```text
Frontend → Backend API → DataProduct → (Aggregation or Dataset in S3) → Response
```

1. The frontend requests a DataProduct
2. The backend validates access permissions
3. The backend resolves the underlying data source
4. Data is retrieved from S3 (or cache)
5. A structured JSON response is returned


## 4. Synchronization Model

* **Asynchronous:**

  * Upload processing
  * Data validation
  * Dataset generation
  * Aggregation jobs

* **Synchronous:**

  * Authentication
  * Data product access
  * Metadata queries


## 5. Main Components

### Frontend

The frontend provides:

* Upload interface for providers
* Marketplace interface for browsing DataProducts
* Visualization of aggregated data
* Access management (basic)

It focuses on presentation and user interaction, consuming preprocessed data in JSON format.


### Backend API

The backend acts as the central orchestrator.

Responsibilities:

* Authentication and user management
* Organization and role handling
* Upload registration and tracking
* Pre-signed URL generation for S3 uploads
* Triggering processing jobs
* DataProduct management
* Access control and authorization
* Transaction handling (purchases)

It performs lightweight validation and delegates heavy processing to the processing layer.


### PostgreSQL

PostgreSQL is the source of truth for system state and relationships.

It stores:

* Users and organizations
* Hotel metadata (for providers)
* HotelEvent records (structural changes such as category updates, renovations, and capacity changes)
* Upload metadata and status
* Dataset references, status, and versioning
* Aggregation metadata
* DataProducts
* Access control (entitlements)
* Transactions and pricing

PostgreSQL also stores dataset metadata required for filtering and aggregation (e.g., period, status, and provider attributes via Hotel), enabling efficient dataset selection without scanning S3.

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
/processed/org_id=123/year=2025/part-*.parquet
/aggregated/metric=occupancy/city=xxx/year=2025/part-*.parquet
```

S3 provides:

* Scalability
* Cost efficiency
* Data lineage and traceability
* Compatibility with batch processing systems


### Processing Layer

The processing layer runs asynchronously after uploads.

Responsibilities:

1. Schema validation
2. Data cleaning
3. Normalization into a standard format
4. Deduplication and consistency checks
5. Dataset generation (snapshot-based)
6. Aggregation across datasets based on predefined configurations (metric, dimensions, time granularity)
7. Writing outputs to S3

The processing layer also extracts and persists dataset metadata required for downstream aggregation and filtering.

The system tracks structural changes in hotels (e.g., category updates, renovations, capacity changes) via HotelEvent records, enabling historical consistency in analytical queries.

The output is:

* A clean dataset per upload
* Aggregated data ready for DataProducts


## 6. Data Storage Strategy

* **PostgreSQL:**

  * Metadata
  * Relationships
  * Access control
  * Transactions

* **S3:**

  * Raw data
  * Processed datasets
  * Aggregated datasets

This separation ensures:

* Fast transactional queries
* Scalable analytical storage
* Clean architecture boundaries


## 7. Initial Technical Decisions

* **FastAPI:**

  * High performance
  * Strong typing with Pydantic
  * Good fit for API-driven architecture

* **React + Recharts:**

  * Flexible UI for dashboards and marketplace views
  * Fast iteration for MVP


## 8. Data Governance & Access Control

The system enforces:

* Organization-level ownership of data
* Provider consent for data sharing
* Access control via DataProduct entitlements
* Separation between aggregated and raw data products


## 9. Failure Handling

Failures may occur during:

* Upload validation
* Data processing
* S3 writes
* Metadata updates

The system must support:

* Retry mechanisms
* Error logging
* Clear status reporting to users


## 10. Future Improvements

* Automated ingestion pipelines
* Streaming / incremental processing
* Advanced aggregation strategies
* Pricing and subscription models
* Integration with external systems (PMS, APIs)
* Distributed processing (Spark, AWS Glue, EMR)


