This README is designed for the repository test_dbt_ducklake, emphasizing the specific value proposition of DuckLake as a modern alternative to traditional lakehouse formats like Iceberg or Delta Lake.

🦆 dbt-ducklake: Streaming Lakehouse Power
This repository provides a dbt implementation for DuckLake, the integrated data lake and catalog format designed for extreme performance, simplicity, and streaming ingestion.

🚀 Why DuckLake?
Traditional lakehouse formats (like Apache Iceberg or Delta Lake) struggle with the "small file problem" and metadata sprawl. DuckLake reimagines the lakehouse by separating metadata management from file storage, using a standard SQL database (PostgreSQL, SQLite, or DuckDB) as the catalog.

Key Benefits
Real-Time Streaming Ingestion: Features Data Inlining, which stores small updates and deletes directly in the catalog database rather than writing thousands of tiny Parquet files. This results in up to 105x faster ingestion than traditional formats.

Sub-Second Analytics: By avoiding "metadata sprawl" and the overhead of scanning thousands of JSON/Avro manifest files, query performance can be up to 900x faster for streaming workloads.

True ACID Transactions: DuckLake provides ACID guarantees across multi-table operations by leveraging the transactional nature of the catalog database.

Zero-Lock-In & Open Specs: Data is stored in standard Parquet on S3, GCS, or local disk. The catalog is accessible via standard SQL.

Built for DuckDB: Native integration with the DuckDB engine allows for high-throughput analytical queries without the need for heavy, always-on clusters.

🛠 Project Structure
This dbt project is configured to demonstrate how to manage a DuckLake-backed data lake:

Plaintext
.
├── dbt_project.yml        # Project configuration
├── profiles.yml           # Connection settings for DuckLake/DuckDB
├── models/                # dbt models targeting DuckLake tables
│   ├── staging/           # Raw ingestion points
│   └── marts/             # Business-ready analytical views
└── seeds/                 # Static reference data
🏁 Getting Started
1. Prerequisites
Python 3.9+

DuckDB

dbt-duckdb adapter

2. Installation
Bash
git clone https://github.com/WillowyBoat2388/test_dbt_ducklake.git
cd test_dbt_ducklake
pip install dbt-duckdb
3. Configure Profile
Update your ~/.dbt/profiles.yml to point to your DuckLake metadata catalog.

YAML
test_dbt_ducklake:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: 'ducklake:metadata.ducklake' # Path to your DuckLake catalog
      extensions:
        - ducklake
      settings:
        data_path: 's3://your-bucket/data/' # Where Parquet files live
4. Run the Project
Bash
dbt deps
dbt seed
dbt run
🔄 Streaming Patterns
To leverage DuckLake's streaming capabilities, use the ducklake_flush_inlined_data command to periodically move inlined catalog data into optimized Parquet files. This ensures your "Hot Tier" (catalog) stays lean and your "Cold Tier" (S3/Parquet) stays high-performance.

⚖️ License
This project is licensed under the MIT License. See LICENSE for details.