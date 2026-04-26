from loguru import logger
from test_dbt_ducklake.ducklake import setup_ducklake


def ingest_from_api(path=None):
    """Fetch all sources and load into DuckLake."""
    from test_dbt_ducklake.ingestion.import_ import (
        ingest_wb_countries,
        ingest_doing_business,
        ingest_enterprise_surveys,
        ingest_governance_indicators,
    )
    con = setup_ducklake()
    
    # ingest_wb_countries(con)
    # ingest_doing_business(con)
    # ingest_enterprise_surveys(con)
    ingest_governance_indicators(con)

    tables = con.execute("SHOW TABLES").fetchall()
    logger.info("Ingestion complete. Tables in datalake:")
    for (t,) in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        logger.info(f"  {t}: {count} rows")

    con.close()

    # # Generate TPC-H data in memory, then copy to Ducklake
    # conn.execute("USE memory;")
    # conn.execute("CALL dbgen(sf = 0.1);")  # ~60K lineitem records

    # conn.execute("USE ducklake_catalog;")
    # conn.execute("CREATE TABLE lineitem AS SELECT * FROM memory.lineitem;")

    # conn.close()

if __name__ == "__main__":
    ingest_from_api()
