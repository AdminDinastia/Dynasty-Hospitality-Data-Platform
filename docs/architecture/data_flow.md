# Data Flow Overview

## 1. Upload Flow

1. The backend creates an upload record in PostgreSQL
   * Initial status: `pending`
2. The user uploads the file directly to S3 (raw layer) via pre-signed URL
3. Once the upload is confirmed, the backend updates the status to `processing`

## 2. Processing Flow

1. An asynchronous job is triggered to process the upload
2. The processing layer:
   * validates the dataset schema
   * checks required fields and granularity
   * cleans and normalizes the data
   * transforms it into a standard format
3. Dataset metadata is extracted (e.g., period, accommodation reference) and stored in PostgreSQL
4. If processing fails:
   * upload status → `failed`
   * dataset state → `failed`
5. If successful:
   * a processed dataset is generated
   * dataset state → `ready`

## 3. Storage Flow

1. The processed dataset is stored in S3 (processed layer) in Parquet format
2. Data is partitioned (e.g., by year and accommodation) to enable efficient reads
3. A dataset record is created in PostgreSQL including:
   * org_id
   * accommodation_id
   * period_start / period_end
   * storage_path
   * state

## 4. Activation Flow

1. Once validated, the dataset is marked as `ready`
2. The system may mark the dataset as `active`
3. Constraint:
   * Only one dataset can be active per `(accommodation_id, period)`
4. Previously active datasets for the same scope are deactivated

## 5. Aggregation Flow

1. Aggregation jobs are triggered periodically (e.g., daily) or on-demand
2. For pre-computed aggregations, the system uses predefined configurations:
   * aggregation_type (e.g., location)
   * parameters (e.g., {"level": "city", "location": "Gran Canaria"})
3. The backend queries PostgreSQL to select relevant datasets:
   * only datasets with `is_active = true`
   * filtered by:
     * period (period_start / period_end)
     * accommodation attributes (city, country, type, category)
     * data_sharing_consent (allow_aggregated = true)
4. The system retrieves the selected datasets from S3 (processed layer)
5. Data from multiple datasets is combined
6. Aggregated metrics are computed:
   * average occupancy
   * ADR
   * RevPAR
   * market distribution
7. Aggregated results are stored in S3 (aggregated layer), e.g.:
   ```plaintext
   /aggregated/level=city/location=gran-canaria/year=2025/
   ```
8. Aggregation metadata is stored in PostgreSQL:
   * aggregation_id
   * aggregation_type
   * parameters
   * storage_path
   * status
   * computed_at
9. When datasets are used in aggregations, providers earn points:
   * PointsLedger entry created (+points, reason=data_used)
   * Organization.points_balance updated

## 6. Product Access Flow (Consumer)

1. Consumer browses available data products
2. Consumer selects a product (aggregated or raw)
3. Backend checks:
   * Does the consumer have sufficient points?
   * Does an entitlement already exist?
4. If purchasing:
   * PointsLedger entry created (-points, reason=product_access)
   * Organization.points_balance updated
   * Entitlement created
5. If accessing raw product:
   * Check data_sharing_consent.allow_raw_sharing = true
   * RevenueDistribution created (pending) for the provider
   * Stripe Connect transfer initiated
6. Backend resolves the data source:
   * For aggregated products → retrieves from aggregation storage_path
   * For raw products → retrieves from dataset storage_path
7. Data is retrieved from S3
8. Data is mapped to the appropriate report template
9. Structured JSON response is returned to frontend

## 7. Points Purchase Flow (Consumer)

1. Consumer initiates point purchase
2. PaymentRecord created (status=pending)
3. Stripe payment processed
4. On success:
   * PaymentRecord updated (status=completed)
   * PointsLedger entry created (+points, reason=purchase)
   * Organization.points_balance updated
5. On failure:
   * PaymentRecord updated (status=failed)

## 8. Revenue Distribution Flow (Provider)

1. Consumer purchases access to raw_product
2. RevenueDistribution record created:
   * Links to raw_product_id, buyer_org_id, provider org_id
   * Calculates amount based on revenue_share_pct from data_sharing_consent
   * Status: pending
3. Stripe Connect transfer initiated to provider's stripe_account_id
4. On success:
   * RevenueDistribution updated (status=paid)
5. On failure:
   * RevenueDistribution updated (status=failed)
   * Retry mechanism triggered

## 9. Read Flow (Consumer accessing purchased product)

1. Frontend requests data from backend
2. Backend validates entitlement exists for org_id + product_id
3. Backend resolves the data source:
   * For aggregated products → queries aggregation metadata
   * For raw products → queries dataset metadata
4. Backend retrieves data from S3 using storage_path
5. Data is transformed into JSON format according to report template
6. Response is returned to frontend with:
   * Structured data
   * Template information
   * Metadata (period, filters applied)

## 10. Error Flow

Failures may occur at different stages:

* **Upload failure** → remains `pending` or marked `failed`
* **Validation failure** → dataset state → `failed`
* **Processing failure** → dataset state → `failed`
* **Storage failure** → retry or mark failed
* **Payment failure** → PaymentRecord status → `failed`
* **Payout failure** → RevenueDistribution status → `failed`, retry

The system must support:

* Retry mechanisms for transient failures
* Idempotent processing to handle retries safely
* Clear status reporting to users
* Error logging for debugging


