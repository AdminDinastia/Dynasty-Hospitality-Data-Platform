# Data Products & Access Model

## 1. Product Types

Contamos con dos tipos principales de DataProducts:

* **Aggregated DataProducts**

  * Derivados de múltiples datasets
  * Representan métricas agregadas, comparativas y benchmarks de mercado

* **Raw DataProducts**

  * Derivados de un dataset individual (e.g., un hotel específico y un periodo concreto)
  * Representan datos detallados y exactos

Cada DataProduct corresponde a un **dataset o periodo concreto (snapshot)**.


## 2. Access Model

### Data Providers

#### Free access

* Access to their own datasets and internal metrics
* Access to basic aggregated benchmarks (e.g., by city or category)
* Ability to compare performance across their own properties (e.g., chain-level or regional view)


#### Advanced access (data-exchange or paid)

* Access to advanced benchmarks:

  * comparisons with similar hotels
  * comparisons with competitors in the same area

* Access is unlocked through:

  * contributing additional data (data-exchange model), or
  * direct payment

* For MVP:

  * most benchmarking can remain free to incentivize onboarding
  * advanced benchmarking can be introduced later as a premium feature


### Data Consumers

#### Free access

##### Aggregated level

* Access to basic aggregated metrics:

  * e.g., province-level or city-level performance


##### Hotel level (preview)

* Access to limited preview analytics per hotel:

  * proprietary score (e.g., 1–10)
  * selected signals such as:

    * occupancy above/below market
    * revenue trend (increasing / declining / stable)

* These insights are:

  * simplified
  * non-exact
  * designed to generate interest without exposing raw data


#### Paid access

##### Aggregated level (subscription)

* Access to advanced aggregations:

  * more granular segmentation (e.g., category, zone, hotel type)
  * deeper time analysis
  * comparisons and insights across the market

* Characteristics:

  * lower cost
  * scalable
  * subscription-based access


##### Hotel level (raw data)

* Access to full hotel datasets:

  * exact metrics
  * detailed breakdowns (time series, performance evolution)

* Availability depends on:

  * provider consent (`ProviderConsent`)

* Access is granted as a **snapshot (fixed period data)**


## 3. Purchase Flow

1. The user selects a DataProduct (aggregated or raw).

2. The system validates:

   * whether the user already has access
   * whether the product is available
   * for raw products, whether the provider allows access (`ProviderConsent`)

3. The user proceeds with payment:

   * one-time purchase (raw data), or
   * subscription (aggregated access, valid while active)

4. A transaction is created.

5. A corresponding access record (`DataAccess`) is created.

6. The user gains access to the DataProduct.

7. The purchased dataset is available as a **snapshot (fixed period data)**.

8. If new data for the same entity becomes available (e.g., new year), it is offered as a **separate purchasable update at a reduced price**.


## 4. Provider Control

1. Providers decide whether their data can be shared.

2. Providers define the sharing scope:

   * aggregated only
   * aggregated + raw

3. Providers can update their sharing preferences at any time.

4. Changes in sharing preferences affect **future availability**, but do not revoke access to already purchased data.

5. Providers benefit financially from raw data sales via a commission model.


## 5. Monetization

The platform generates revenue primarily from data consumers (e.g., investors, companies).


### Aggregated Data (Subscription)

* Users pay a recurring fee to access:

  * aggregated metrics
  * benchmarking data
  * market insights and comparisons

* This provides:

  * scalable revenue
  * continuous engagement


### Raw Data (One-time Purchase)

* Users can purchase individual datasets (e.g., a specific hotel and period).

* These purchases provide:

  * full access to exact metrics
  * detailed breakdowns
  * high-value insights

* Raw data purchases generate:

  * higher margin per transaction
  * commission revenue shared with providers


### Updates

* New datasets (e.g., future periods) are treated as:

  * new purchasable DataProducts
  * offered at a reduced price compared to the initial purchase


### Providers

* Providers (hotels) are not the primary paying users in the MVP.

* They may optionally:

  * pay for advanced benchmarking features
  * or unlock features via data contribution (data-exchange model)


## 6. Consumption Model

Users consume purchased data through:


### Primary (MVP)

* Interactive dashboards
* Structured visualizations
* Filtered views (time, location, category)


### Additional formats

* Exportable reports (e.g., PDF)
* Data export (e.g., CSV / Parquet)


### Access characteristics

* Purchased datasets are:

  * permanently accessible
  * immutable (snapshot-based)
  * read-only

* Users can:

  * revisit the data at any time
  * use it for analysis and decision-making


### Updates

* New data (e.g., future periods) is not automatically included
* It is offered as a separate purchasable update


## Future Monetization 

Potential future extensions of the pricing model:

* Token-based pricing
* Usage-based access
* API monetization
* Tiered subscription plans with usage limits

