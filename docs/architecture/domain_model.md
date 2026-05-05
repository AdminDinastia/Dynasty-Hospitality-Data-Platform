# DOMAIN MODEL 

## What exists in the system?

The system follows a data marketplace flow:

```text
Data Provider (Organization) → Upload → Dataset → Aggregation → DataProduct → Data Consumer (Organization)
```


## User

Represents a person interacting with the platform.

A user:

* belongs to an organization
* performs actions such as uploading data or consuming data products
* does not own data directly (ownership belongs to the organization)

Key attributes:

* user_id
* email
* created_at


## Organization

Represents a real-world entity that either provides or consumes data.

Types:

* provider → supplies data (e.g., hotels)
* consumer → consumes data (e.g., investors, companies)

An organization:

* owns datasets
* has one or more users
* can purchase or access data products

Key attributes:

* org_id
* name
* type (provider | consumer)
* created_at


## Hotel

A specialization of Organization (type = provider).

Used to store domain-specific attributes required for segmentation and analytics.

Represents the **current state** of the hotel.

Key attributes:

* hotel_id (org_id)
* city
* country
* current_category (e.g., stars)
* current_room_count
* last_renovation_date (optional, derived)


## HotelEvent

Represents structural changes in a hotel over time.

Used to track:

* category changes
* renovations
* capacity changes

A hotel event:

* belongs to a hotel
* represents a single type of change
* is effective at a specific point in time

Supported event types:

* category_change
* renovation
* capacity_change

Key attributes:

```text
- event_id
- hotel_id
- event_type

-- category_change
- old_category (optional)
- new_category (optional)

-- capacity_change
- old_room_count (optional)
- new_room_count (optional)

-- renovation
- renovation_type (partial | full)
- renovation_scope (rooms | common_areas | amenities | structural | full_property)
- renovation_detail (optional)
- renovation_cost (optional)

-- shared
- effective_date
- created_at
```

Design notes:

* Each event represents **a single type of change**
* Multiple events can occur on the same date
* Historical state can be reconstructed from events if needed


## Upload

Represents raw data submitted by a provider.

An upload:

* belongs to an organization
* is stored as a raw file (e.g., CSV in S3)
* triggers a processing job

States:

* pending
* processing
* completed
* failed

Key attributes:

* upload_id
* org_id
* status
* file_path
* created_at


## Dataset

Represents processed and normalized data derived from an upload.

A dataset:

* belongs to a provider organization
* is generated from a single upload (MVP decision)
* is immutable
* represents a consistent snapshot of operational data

Design decisions:

* one upload generates one dataset
* datasets are versioned implicitly
* datasets represent **historical data**

Key attributes:

* dataset_id
* org_id
* source_upload_id
* period_start
* period_end
* storage_path
* created_at

State:

* processing
* ready
* active
* failed

Optional attributes:

* category_snapshot (optional, for historical consistency)


## Aggregation

Represents aggregated data derived from multiple datasets.

Used to:

* anonymize provider data
* generate global metrics

Examples:

* average occupancy per city
* ADR per region

Key attributes:

* aggregation_id
* metric
* dimensions (e.g., city, time)
* period
* storage_path
* created_at


## DataProduct

Represents a consumable data asset.

Types:

* aggregated → based on aggregations (anonymized)
* raw → based on individual datasets (controlled access)

Aggregated DataProduct:

* derived from aggregations
* anonymized
* scalable

Raw DataProduct:

* derived from individual provider datasets
* higher value
* requires permission and access control

Key attributes:

* product_id
* type (aggregated | raw)
* name
* description
* source_ref (aggregation_id or dataset_id)
* period
* created_at


## DataAccess

Represents access rights to a data product.

Used to control:

* granted access
* purchased access

Key attributes:

* access_id
* org_id (consumer)
* product_id
* access_type (granted | purchased)
* created_at


## Transaction

Represents a purchase of a data product.

Used for:

* monetization
* commission tracking

Key attributes:

* transaction_id
* buyer_org_id
* product_id
* price
* commission
* created_at


## ProviderConsent

Defines whether a provider allows their data to be shared.

Required for raw data monetization.

Key attributes:

* org_id
* allow_data_sharing (boolean)
* sharing_scope (aggregated | raw)

