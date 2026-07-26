# DOMAIN MODEL

## What exists in the system?

The system follows a data marketplace flow:

```text
Data Provider (Organization) → Upload → Dataset → Aggregation → DataProduct → Data Consumer (Organization)
                                                                      ↓
                                                                Points/Money
```


## User

Represents a person interacting with the platform.

A user:

* belongs to an organization
* has a role (org_admin, org_member, platform_admin)
* performs actions such as uploading data or consuming data products
* does not own data directly (ownership belongs to the organization)

Key attributes:

* user_id
* external_id (from auth provider like Clerk)
* org_id
* email
* role
* created_at


## Organization

Represents a real-world entity that either provides or consumes data.

Types:

* provider → supplies data (e.g., hotels, aparthotels)
* consumer → consumes data (e.g., investors, companies)

An organization:

* owns accommodations (if provider)
* owns datasets
* has one or more users
* has a points balance
* can purchase points with money
* can spend points to access data products

Key attributes:

* org_id
* name
* type (provider | consumer)
* points_balance
* stripe_account_id (for providers receiving payouts)
* stripe_customer_id (for consumers making payments)
* created_at


## Accommodation

Represents a lodging unit (hotel, hostel, aparthotel, resort).

Used to store domain-specific attributes required for segmentation and analytics.

Represents the **current state** of the accommodation.

Key attributes:

* id
* org_id
* city
* country
* type (hotel | hostel | aparthotel | resort)
* category_system (stars | keys)
* category_value
* current_room_count
* created_at


## AccommodationEvent

Represents structural changes in an accommodation over time.

Used to track:

* category changes
* renovations
* capacity changes
* type changes

An accommodation event:

* belongs to an accommodation
* represents a single type of change
* is effective at a specific point in time

Supported event types:

* capacity_change → room count changes
* category_change → star/key rating changes
* renovation → partial or full renovations
* type_change → hotel → aparthotel, etc.

Key attributes:

* event_id
* accommodation_id
* event_type
* effective_date
* description
* created_at

Each event type has specialized attributes in separate tables (capacity_changes, category_changes, renovations, type_changes).


## DataSharingConsent

Defines whether a provider allows their accommodation data to be shared.

Required for raw data monetization.

Key attributes:

* consent_id
* accommodation_id
* allow_raw_sharing (boolean)
* allow_aggregated (boolean)
* revenue_share_pct (percentage received when individual data is sold)
* terms_version
* consent_given_at
* revoked_at (nullable)


## Upload

Represents raw data submitted by a provider.

An upload:

* belongs to an organization
* is stored as a raw file (CSV in S3)
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
* error_message
* file_path
* created_at


## Dataset

Represents processed and normalized data derived from an upload.

A dataset:

* belongs to a provider organization
* is associated with a specific accommodation
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
* accommodation_id
* source_upload_id
* period_start
* period_end
* storage_path
* is_active (only one active dataset per accommodation per period)
* state (draft | ready | archived)
* created_at


## Aggregation

Represents aggregated data derived from multiple datasets.

Used to:

* anonymize provider data
* generate market-level metrics

Examples:

* average occupancy per city
* ADR per region

Aggregations can be pre-computed for common queries (e.g., by geographic level) or computed on-demand.

Key attributes:

* aggregation_id
* aggregation_type (location | category | custom)
* parameters (JSON: dimensions, filters)
* storage_path
* status (pending | computing | ready | failed)
* computed_at
* expires_at (optional cache expiration)
* created_at


## AggregatedProduct

Represents a consumable aggregated data asset.

Based on aggregations, anonymized across multiple providers.

Key attributes:

* product_id
* name
* description
* aggregation_id
* template_name (reference to JSON report template)
* price_points
* is_public
* is_featured
* status (active | inactive)
* created_at


## RawProduct

Represents access to individual accommodation data.

Based on a specific accommodation's datasets.

Key attributes:

* product_id
* name
* description
* accommodation_id
* template_name (reference to JSON report template)
* preview_config (JSON: what metrics non-paying users see)
* price_points
* is_public
* is_featured
* status (active | inactive)
* created_at


## MarketReport

Represents a saved market analysis report for a consumer.

Key attributes:

* report_id
* org_id (consumer)
* aggregated_product_id
* filters (JSON: user-selected filters like zone, period, category)
* created_at


## AccommodationReport

Represents a saved individual accommodation report for a consumer.

Key attributes:

* report_id
* org_id (consumer)
* raw_product_id
* created_at


## Entitlement

Represents access rights to a data product.

Used to control:

* points-based access (consumer spent points)
* granted access (manual platform grant)

Key attributes:

* entitlement_id
* org_id (consumer)
* aggregated_product_id (nullable)
* raw_product_id (nullable)
* entitlement_type (points | granted)
* granted_at
* expires_at (nullable)


## PaymentRecord

Represents a real money payment where a consumer purchases points.

Key attributes:

* payment_id
* org_id
* amount (cents)
* currency (ISO 4217)
* points_awarded
* stripe_payment_id
* status (pending | completed | failed | refunded)
* created_at


## PointsLedger

Immutable record of all point movements for audit trail.

Every point earned or spent creates a ledger entry.

Key attributes:

* ledger_id
* org_id
* points (positive for earned, negative for spent)
* reason (purchase | welcome_bonus | data_used | product_access | refund | manual)
* reference_id (ID of related entity)
* reference_type (payment | product | aggregation)
* created_at


## RevenueDistribution

Represents a payout to a provider when their individual accommodation data is purchased.

Key attributes:

* distribution_id
* raw_product_id (what was sold)
* buyer_org_id (who bought it)
* org_id (provider receiving payment)
* accommodation_id (which accommodation's data)
* amount (cents)
* revenue_share_pct (locked at time of purchase)
* stripe_transfer_id
* status (pending | paid | failed)
* created_at


## Key Flows

**Consumer purchases points:**
1. PaymentRecord created (pending)
2. Stripe processes payment
3. PaymentRecord updated (completed)
4. PointsLedger entry created (+points, reason=purchase)
5. Organization.points_balance updated

**Consumer accesses product:**
1. Check points_balance >= product.price_points
2. PointsLedger entry created (-points, reason=product_access)
3. Organization.points_balance updated
4. Entitlement created

**Provider earns from aggregation:**
1. Aggregation uses provider's dataset
2. PointsLedger entry created (+points, reason=data_used)
3. Organization.points_balance updated

**Provider earns from individual sale:**
1. Consumer purchases raw_product
2. RevenueDistribution created (pending)
3. Stripe Connect transfers money to provider
4. RevenueDistribution updated (paid)

