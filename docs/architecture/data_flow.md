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

3. Dataset metadata is extracted (e.g., period, organization reference) and stored in PostgreSQL

4. If processing fails:

   * upload status → `failed`
   * dataset status → `failed`

5. If successful:

   * a processed dataset is generated
   * dataset status → `ready`


## 3. Storage Flow

1. The processed dataset is stored in S3 (processed layer) in Parquet format

2. Data is partitioned (e.g., by year) to enable efficient reads

3. A dataset record is created in PostgreSQL including:

   * org_id / hotel_id
   * period_start / period_end
   * storage_path
   * status


## 4. Activation Flow

1. Once validated, the dataset is marked as `ready`

2. The system may mark the dataset as `active`

3. Constraint:

   * Only one dataset can be active per `(hotel_id, year)`

4. Previously active datasets for the same scope are deactivated


## 5. Read Flow

1. The frontend requests data from the backend

2. The backend queries PostgreSQL to determine:

   * which dataset is `active`
   * which storage_path to use

3. The backend retrieves the dataset from S3

4. Data is optionally transformed into a JSON-friendly format

5. The response is returned to the frontend


## 6. Error Flow

Failures may occur at different stages:

* Upload failure → remains `pending` or marked `failed`
* Validation failure → dataset marked `failed`
* Processing failure → dataset marked `failed`
* Storage failure → retry or mark failed

The system should support:

* retry mechanisms
* idempotent processing
* clear status reporting


## 7. Aggregation Flow

1. Aggregation jobs are triggered periodically (e.g., daily) or manually

2. The system selects a predefined aggregation configuration:

   * metric (e.g., occupancy, ADR)
   * dimensions (e.g., city, region)
   * time granularity (e.g., monthly, yearly)

3. The backend queries PostgreSQL to select relevant datasets:

   * only datasets with status = `active`
   * filtered by:

     * period (period_start / period_end)
     * provider attributes (via Hotel and HotelEvent: city, country, category, last_renovation_date)

4. The system retrieves the selected datasets from S3 (processed layer)

5. Data from multiple datasets is combined

6. Aggregated metrics are computed:

   * average occupancy
   * ADR
   * revenue trends

7. Aggregated results are stored in S3 (aggregated layer), e.g.:

```plaintext
/aggregated/metric=occupancy/city=xxx/year=2025/
```

8. Aggregation metadata is stored in PostgreSQL:

   * aggregation_id
   * metric
   * dimensions
   * period
   * storage_path
   * created_at

9. Aggregations are exposed as DataProducts


