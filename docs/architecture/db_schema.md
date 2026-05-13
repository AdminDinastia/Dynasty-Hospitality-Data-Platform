# Database Schema

This document defines the relational structure of the system, including both the **data layer** (datasets, aggregations) and the **business layer** (data products, access, monetization).

The schema is designed to support a scalable data platform where:

* Providers upload and manage data
* Data is processed into datasets and aggregations
* Consumers purchase points and access structured data products
* Providers earn points and money through data sharing


## Core Concepts

The system is structured around five main layers:

* **Organizations & Users** → who interacts with the platform
* **Accommodations & Events** → what entities provide data and their historical changes
* **Data Layer** → datasets and aggregations
* **Marketplace Layer** → data products and reports
* **Billing Layer** → monetization, points, and payments


## Schema (DBML)

```dbml
Enum organization_type {
  provider
  consumer
}

Table organizations {
  org_id int [pk]
  name varchar
  type organization_type
  
  // Monetization
  points_balance int [default: 0]
  stripe_account_id varchar [note: 'Stripe Connect for providers']
  stripe_customer_id varchar [note: 'Stripe Customer for consumers']
  
  created_at datetime
  updated_at datetime
}

Enum user_role {
  org_admin
  org_member
  platform_admin
}

Table users {
  user_id int [pk]
  external_id varchar [note: 'Auth provider ID (Clerk)']
  org_id int [ref: > organizations.org_id]
  email varchar
  role user_role
  created_at datetime
}

Enum accommodation_type {
  hotel
  hostel
  aparthotel
  resort
}

Enum category_system {
  stars
  keys
}

Table accommodations {
  id int [pk]
  org_id int [ref: > organizations.org_id]
  city varchar
  country varchar
  type accommodation_type
  category_system category_system
  category_value int
  current_room_count int
  created_at datetime
  updated_at datetime
}

Table tags {
  id int [pk]
  name varchar
  category varchar
}

Table accommodation_tags {
  accommodation_id int [ref: > accommodations.id]
  tag_id int [ref: > tags.id]
  
  indexes {
    (accommodation_id, tag_id) [pk]
  }
}

Table data_sharing_consents {
  consent_id int [pk]
  accommodation_id int [ref: > accommodations.id]
  
  // What can be shared
  allow_raw_sharing boolean [default: false]
  allow_aggregated boolean [default: false]
  
  // Monetization
  revenue_share_pct decimal(5,2) [default: 30.00]
  
  // Auditing
  terms_version varchar
  consent_given_at datetime
  revoked_at datetime [null]
}

Enum event_type {
  capacity_change
  category_change
  renovation
  type_change
}

Table accommodation_events {
  event_id int [pk]
  accommodation_id int [ref: > accommodations.id]
  event_type event_type
  effective_date date
  description varchar
  created_at datetime
  updated_at datetime
}

Table capacity_changes {
  event_id int [pk, ref: - accommodation_events.event_id]
  old_room_count int
  new_room_count int
}

Table category_changes {
  event_id int [pk, ref: - accommodation_events.event_id]
  old_value int
  new_value int
  old_system category_system
  new_system category_system
}

Enum renovation_type {
  partial
  full
}

Enum renovation_scope {
  rooms
  common_areas
  amenities
  structural
  full_property
}

Table renovations {
  event_id int [pk, ref: - accommodation_events.event_id]
  renovation_type renovation_type
  renovation_scope renovation_scope
  cost float
}

Table type_changes {
  event_id int [pk, ref: - accommodation_events.event_id]
  old_type accommodation_type
  new_type accommodation_type
}

Enum upload_status {
  pending
  processing
  completed
  failed
}

Table uploads {
  upload_id int [pk]
  org_id int [ref: > organizations.org_id]
  status upload_status
  error_message varchar
  file_path varchar
  created_at datetime
  updated_at datetime
}

Enum dataset_state {
  draft
  ready
  archived
}

Table datasets {
  dataset_id int [pk]
  org_id int [ref: > organizations.org_id]
  accommodation_id int [ref: > accommodations.id]
  source_upload_id int [ref: > uploads.upload_id]
  
  name varchar
  granularity varchar
  
  period_start date
  period_end date
  
  storage_path varchar
  currency varchar
  
  is_active boolean [default: true]
  state dataset_state [default: 'draft']
  
  created_at datetime
  updated_at datetime
}

Enum aggregation_status {
  pending
  computing
  ready
  failed
}

Table aggregations {
  aggregation_id int [pk]
  
  aggregation_type varchar [note: 'location, category, etc.']
  parameters json [note: '{"level": "city", "location": "Gran Canaria"}']
  
  storage_path varchar
  status aggregation_status [default: 'pending']
  
  computed_at datetime
  expires_at datetime
  created_at datetime
}

Enum product_status {
  active
  inactive
}

Table aggregated_products {
  product_id int [pk]
  name varchar
  description varchar
  
  aggregation_id int [ref: > aggregations.aggregation_id]
  template_name varchar [note: 'market_report']
  
  price_points int
  
  is_public boolean [default: true]
  is_featured boolean [default: false]
  status product_status [default: 'active']
  
  created_at datetime
  updated_at datetime
}

Table raw_products {
  product_id int [pk]
  name varchar
  description varchar
  
  accommodation_id int [ref: > accommodations.id]
  template_name varchar [note: 'hotel_report']
  
  preview_config json
  price_points int
  
  is_public boolean [default: true]
  is_featured boolean [default: false]
  status product_status [default: 'active']
  
  created_at datetime
  updated_at datetime
}

Table market_reports {
  report_id int [pk]
  org_id int [ref: > organizations.org_id]
  aggregated_product_id int [ref: > aggregated_products.product_id]
  filters json
  created_at datetime
}

Table accommodation_reports {
  report_id int [pk]
  org_id int [ref: > organizations.org_id]
  raw_product_id int [ref: > raw_products.product_id]
  created_at datetime
}

Enum entitlement_type {
  points
  granted
}

Table entitlements {
  entitlement_id int [pk]
  org_id int [ref: > organizations.org_id]
  
  aggregated_product_id int [ref: > aggregated_products.product_id]
  raw_product_id int [ref: > raw_products.product_id]
  
  entitlement_type entitlement_type
  
  granted_at datetime
  expires_at datetime
}

Enum payment_status {
  pending
  completed
  failed
  refunded
}

Table payment_records {
  payment_id int [pk]
  org_id int [ref: > organizations.org_id]
  
  amount int [note: 'in cents']
  currency varchar(3) [default: 'EUR']
  points_awarded int
  
  stripe_payment_id varchar
  status payment_status [default: 'pending']
  
  created_at datetime
  updated_at datetime
}

Enum points_reason {
  purchase
  welcome_bonus
  data_used
  product_access
  refund
  manual
}

Table points_ledger {
  ledger_id int [pk]
  org_id int [ref: > organizations.org_id]
  
  points int [note: 'positive (earned) or negative (spent)']
  reason points_reason
  
  reference_id int
  reference_type varchar [note: 'payment, product, aggregation']
  
  created_at datetime
}

Enum revenue_status {
  pending
  paid
  failed
}

Table revenue_distributions {
  distribution_id int [pk]
  
  raw_product_id int [ref: > raw_products.product_id]
  buyer_org_id int [ref: > organizations.org_id]
  
  org_id int [ref: > organizations.org_id, note: 'provider receiving payment']
  accommodation_id int [ref: > accommodations.id]
  
  amount int [note: 'in cents']
  revenue_share_pct decimal(5,2)
  
  stripe_transfer_id varchar
  status revenue_status [default: 'pending']
  
  created_at datetime
  updated_at datetime
}
```


## Design Notes

* **Accommodations are owned by provider organizations** using a standard foreign key
* **Datasets represent the source of truth**, while aggregations are derived from them
* **Aggregations use a flexible schema** with `aggregation_type` and `parameters` JSONB for extensibility
* **Data products are separated** into `aggregated_products` and `raw_products` with distinct pricing and access models
* **Unified points system** for all purchases, tracked via immutable `points_ledger`
* **Payment records** track real money flowing into the platform
* **Revenue distributions** track money flowing out to providers via Stripe Connect
* **Reports are separated** into `market_reports` and `accommodation_reports` based on context


## Key Principles

* Separation between **data generation** and **data consumption**
* Use of **S3 / data lake for heavy data**, PostgreSQL for metadata
* Flexibility through JSON fields for aggregation configuration and report filters
* **Immutable ledger** for points with full audit trail
* **Historical accuracy** by locking revenue_share_pct at time of transaction
* Designed to evolve toward **analytical query engines** (BigQuery, Athena)


