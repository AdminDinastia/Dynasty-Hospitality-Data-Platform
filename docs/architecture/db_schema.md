# Database Schema

This document defines the relational structure of the system, including both the **data layer** (datasets, aggregations) and the **business layer** (data products, access, transactions).

The schema is designed to support a scalable data platform where:

* Providers upload and manage data
* Data is processed into datasets and aggregations
* Consumers access and purchase structured data products


## Core Concepts

The system is structured around four main layers:

* **Organizations & Users** → who interacts with the platform
* **Data Layer** → datasets and aggregations
* **Event Layer** → hotel structural changes over time
* **Business Layer** → monetization and access control


## Schema (DBML)

```dbml
Table users {
  user_id int [pk]
  org_id int [ref: > organizations.org_id]
  email varchar
  created_at datetime
  updated_at datetime
}

Enum organization_type {
  provider
  consumer
}

Table organizations {
  org_id int [pk]
  name varchar
  type organization_type
  created_at datetime
  updated_at datetime
}

Table hotels {
  hotel_id int [pk, ref: - organizations.org_id]
  city varchar
  country varchar
  current_category varchar
  current_room_count int
  last_renovation_date date
  created_at datetime
  updated_at datetime
}

Enum tipo_eventos {
  category_change
  capacity_change
  renovation
}

Table hotel_events {
  event_id int [pk]
  hotel_id int [ref: > hotels.hotel_id]
  event_type tipo_eventos
  effective_date date
  description varchar
  created_at datetime
  updated_at datetime
}

Table category_changes {
  event_id int [pk, ref: - hotel_events.event_id]
  old_category varchar
  new_category varchar
}

Table capacity_changes {
  event_id int [pk, ref: - hotel_events.event_id]
  old_room_count int
  new_room_count int
}

Enum tipos_renovacion {
  partial
  full
}

Enum tipos_scope {
  rooms
  common_areas
  amenities
  structural
  full_property
}

Table renovations {
  event_id int [pk, ref: - hotel_events.event_id]
  renovation_type tipos_renovacion
  renovation_scope tipos_scope
  renovation_detail varchar
  renovation_cost float
}

Enum estados {
  pending
  processing
  completed
  failed
}

Table uploads {
  upload_id int [pk]
  org_id int [ref: > organizations.org_id]
  status estados
  file_path varchar
  created_at datetime
  updated_at datetime
}

Table datasets {
  dataset_id int [pk]
  org_id int [ref: > organizations.org_id]
  source_upload_id int [ref: > uploads.upload_id]

  name varchar
  granularity varchar

  period_start date
  period_end date

  storage_path varchar
  currency varchar

  is_active boolean

  created_at datetime
  updated_at datetime
  state estados
}

Table aggregation_definitions {
  definition_id int [pk]
  name varchar

  group_by json
  metrics json
  filters json

  source_dataset varchar

  created_at timestamp
  updated_at timestamp
}

Table aggregations {
  aggregation_id int [pk]
  definition_id int [ref: > aggregation_definitions.definition_id]

  period_start date
  period_end date

  storage_path varchar

  status estados
  version int

  created_at timestamp
  updated_at timestamp
}

Table data_products {
  product_id int [pk]
  type varchar

  name varchar
  description varchar

  aggregation_id int [ref: > aggregations.aggregation_id]
  dataset_id int [ref: > datasets.dataset_id]

  period date

  created_at datetime
  updated_at datetime
}

Table transactions {
  transaction_id int [pk]
  buyer_org_id int [ref: > organizations.org_id]
  product_id int [ref: > data_products.product_id]

  price float
  commission float

  created_at datetime
}

Table data_access {
  access_id int [pk]

  org_id int [ref: > organizations.org_id]
  product_id int [ref: > data_products.product_id]

  access_type varchar

  created_at datetime
}

Table provider_consents {
  org_id int [pk, ref: - organizations.org_id]

  allow_data_sharing boolean
  sharing_scope varchar

  updated_at datetime
}
```


## Design Notes

* **Hotels are modeled as a specialization of organizations** using a shared primary key (1:1 relationship)
* **Datasets represent the source of truth**, while aggregations are derived from them
* **Aggregation definitions** allow reusable logic across multiple time periods
* **DataProducts abstract the data layer into consumable assets**
* **Access control and monetization are handled independently** from the data layer


## Key Principles

* Separation between **data generation** and **data consumption**
* Use of **S3 / data lake for heavy data**, PostgreSQL for metadata
* Flexibility through JSON fields for aggregation configuration
* Designed to evolve toward **BigQuery / analytical query engines**


