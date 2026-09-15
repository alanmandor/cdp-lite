# Data Architecture: Operational, Data Vault, and Kimball

## Purpose

CDP Lite separates operational data capture from analytical consumption. This prevents reporting requirements from changing the API's transactional model and preserves the history required for reliable analysis.

```text
FastAPI operational tables
        |
        v
Data Vault (historical integration layer)
        |
        v
Kimball star schema (analytics layer)
```

## Layer Responsibilities

| Layer | Responsibility | Main tables |
| --- | --- | --- |
| Operational | Supports the API's create and read flows. | `customer_profiles`, `customer_events` |
| Data Vault | Preserves business keys, relationships, payload changes, source lineage, and load history. | Hubs, Links, Satellites |
| Kimball | Provides simple, stable structures for BI queries and metrics. | Dimensions and Facts |

The operational layer is the source for this MVP. In a production implementation, the same vault could also ingest CRM, ecommerce, or web-tracking sources.

## Data Vault 2.0 Model

The first vault scope represents one customer and the events associated with that customer.

```text
HubCustomer ----< LinkCustomerEvent >---- HubEvent
     |                                         |
     v                                         v
SatCustomerProfile                       SatEventDetails
```

### Hubs

Hubs hold stable business keys, not descriptive attributes.

| Table | Business key | Why it exists |
| --- | --- | --- |
| `hub_customer` | `external_id` | Identifies the customer consistently across sources. |
| `hub_event` | source event identifier | Identifies an individual event consistently across loads. |

Each hub also records a hash key, `load_datetime`, and `record_source`.

### Link

`link_customer_event` records that a customer generated an event. It contains the hash keys of both hubs, its own link hash key, loading time, and source.

### Satellites

Satellites store descriptive and changing data with history.

| Table | Parent | Attributes |
| --- | --- | --- |
| `sat_customer_profile` | `hub_customer` | email, first name, last name, hash diff, load time, source |
| `sat_event_details` | `hub_event` | event type, event JSON, occurred time, hash diff, load time, source |

`hash_diff` tells the load process whether an incoming descriptive record differs from the latest known version. It avoids saving an identical version repeatedly.

## Kimball Model

Kimball structures are derived from the Data Vault and are designed for analytics users.

```text
dim_customer ----< fact_customer_event >---- dim_event_type
                         |
                         v
                      dim_date
```

### Grain

The grain of `fact_customer_event` is **one row per customer event**. Defining this first is essential: every metric calculated from this fact must respect that one row equals one event.

### Dimensions and Fact

| Table | Role | Key contents |
| --- | --- | --- |
| `dim_customer` | Customer analysis dimension | surrogate key, external ID, name, email, effective dates, current-row flag |
| `dim_event_type` | Event classification dimension | surrogate key, event type |
| `dim_date` | Calendar dimension | date key, day, month, quarter, year |
| `fact_customer_event` | Event fact | customer key, event-type key, date key, event identifier, occurred timestamp |

`dim_customer` will be a Type 2 slowly changing dimension: an email or name change closes the old dimension version and inserts a new current version. Historical events therefore remain associated with the customer attributes valid at the event time.

## Loading Sequence

1. The API stores profiles and events in operational tables.
2. A vault load creates or finds hub records by their business keys.
3. It creates the customer-event link and only adds satellite versions when the hash diff changes.
4. A mart load builds Type 2 customer history and event facts from the vault.

## MVP Vault Load

The MVP exposes `POST /warehouse/vault/load` to run the operational-to-vault load explicitly. The response reports how many hubs, links, and satellite versions were created.

The load is idempotent: running it again without source changes creates no new records. This is achieved by deterministic SHA-256 hash keys for hubs and links, plus `hash_diff` comparisons for satellites. In production, this endpoint would be replaced or triggered by a scheduled orchestration job.

## MVP Kimball Load

After a successful vault load, `POST /warehouse/mart/load` builds the customer-event mart. It creates a Type 2 customer dimension row for each new customer-profile satellite version, reusable event-type and date dimensions, and one fact row for each event hub.

The mart load is also idempotent. `hub_event_key` is the fact's durable event identifier, so an event is not inserted twice. The customer dimension carries the originating satellite load timestamp, which provides lineage from a dimension row back to its Data Vault version.

## Analytics Consumption

`GET /analytics/event-summary` reads only `fact_customer_event`, `dim_date`, and `dim_event_type`. It returns daily event counts by event type and accepts optional `start_date` and `end_date` filters. This demonstrates the value of the mart: business-facing aggregation does not need to understand operational tables, hubs, links, or satellites.

`fact_customer_event` also stores the optional `purchase_amount` measure and `currency_code` from valid `purchase` payloads. `GET /analytics/purchase-summary` aggregates those measures by date and currency. Currency is part of the result grain, so amounts in different currencies are never summed together.

## Interview Summary

Use this concise explanation:

> The operational API captures customer activity. Data Vault keeps a source-traceable historical integration layer, while Kimball converts that history into a star schema that is easy and fast for BI users to query. The fact table is defined at one event per row, and the customer dimension keeps Type 2 history so past events retain the attributes that were valid when they occurred.
