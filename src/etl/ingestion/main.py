from loguru import logger
import duckdb
from etl.ingestion.worksheet import *
from etl.setup_ducklake import main as setup_ducklake


RAW_TABLE = "raw_events"
DEST_TABLE = "user_clicks"

# Set up DuckDB schema
def init_db(con: duckdb.DuckDBPyConnection):
    cursor = con.cursor()
    cursor.execute("USE lake;")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {RAW_TABLE} ({RAW_TABLE_DEFINITIONS})")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {DEST_TABLE} ({DEST_TABLE_DEFINITIONS}")
    cursor.close()

def ingest_from_api(path=None):
    """Fetch all sources and load into DuckLake."""
    from etl.ingestion.api_ingest import (
        ingest_wb_countries,
        ingest_doing_business,
        ingest_enterprise_surveys,
        ingest_governance_indicators,
    )
    con = setup_ducklake()
    
    ingest_wb_countries(con)
    ingest_doing_business(con)
    ingest_enterprise_surveys(con)
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

# # batch ingestion method — inserts raw messages
# def batch_consume_and_insert(con: duckdb.DuckDBPyConnection, value_list: list duration_seconds: int):
    

#     logger.info(f"Batch Consuming from source {topic}...")
#     start_time = time.time()

#     with con.cursor() as cursor:
#         cursor.execute("USE lake;")
#         # try:
#             # while time.time() - start_time < duration_seconds:
#             #     msg = None
#             #     if msg is None:
#             #         logger.info("No new messages found, sleeping for 5 seconds...")
#             #         time.sleep(5)
#             #         continue
#             #     if msg.error():
#             #         logger.debug("Consumer error:", msg.error())
#             #         continue

#         try:
#             event = json.loads(msg.value().decode("utf-8"))
#             ts = datetime.fromisoformat(event["timestamp"])
#             cursor.execute(
#                 f"INSERT INTO {RAW_TABLE} VALUES (?, ?, ?, ?)",
#                 value_list
#             )
#         except Exception as e:
#             logger.error("Error inserting:", e)

#         # except KeyboardInterrupt:
#         #     logger.debug("Stopping consumer...")
#         # finally:
#         #     logger.info("Closing consumer...")
#         #     consumer.close()
    

# # streaming engine consumer thread — inserts raw messages
# def stream_consume_and_insert(con: duckdb.DuckDBPyConnection, value_list: list duration_seconds: int):
    

#     logger.info(f"Consuming from topic {topic}...")
#     start_time = time.time()

#     with con.cursor() as cursor:
#         cursor.execute("USE lake;")
#         try:
#             while time.time() - start_time < duration_seconds:
#                 msg = None
#                 if msg is None:
#                     print("No new messages found, sleeping for 5 seconds...")
#                     time.sleep(5)
#                     continue
#                 if msg.error():
#                     logger.debug("Consumer error:", msg.error())
#                     continue

#                 try:
#                     event = json.loads(msg.value().decode("utf-8"))
#                     ts = datetime.fromisoformat(event["timestamp"])
#                     cursor.execute(
#                         f"INSERT INTO {RAW_TABLE} VALUES (?, ?, ?, ?)",
#                         value_list
#                     )
#                 except Exception as e:
#                     logger.error("Error inserting:", e)

#         except KeyboardInterrupt:
#             logger.debug("Stopping consumer...")
#         finally:
#             logger.info("Closing consumer...")
#             consumer.close()
    


# # Aggregation thread — runs every 5s
# def aggregate_loop(con: duckdb.DuckDBPyConnection, duration_seconds: int):    
#     start_time = time.time()
#     with con.cursor() as cursor:
#         cursor.execute("USE events_ducklake;")
#         while time.time() - start_time < duration_seconds:
#             try:
#                 # Determine the latest last_snapshot in the destination table
#                 last_snapshot_update = cursor.execute(f"SELECT max(last_snapshot) FROM {DEST_TABLE}").fetchone()[0] or 0
#                 max_snapshot = cursor.execute(f"SELECT max(snapshot_id) FROM events_ducklake.snapshots();").fetchone()[0]

#                 # Aggregate only new raw data
#                 aggregate_sql = f"""
#                     MERGE INTO {DEST_TABLE} AS dest
#                     USING (
#                         SELECT 
#                             user_id,
#                             user_name,
#                             COUNT(*) AS count_of_clicks,
#                             ? AS last_snapshot,
#                         FROM events_ducklake.table_changes('{RAW_TABLE}', ?, ?)
#                         WHERE event_type = 'CLICK'
#                         GROUP BY user_id, user_name
#                     ) AS src
#                     ON dest.user_id = src.user_id
#                     WHEN MATCHED THEN 
#                         UPDATE SET 
#                             count_of_clicks = dest.count_of_clicks + src.count_of_clicks,
#                             last_snapshot = src.last_snapshot
#                     WHEN NOT MATCHED THEN
#                         INSERT (user_id, user_name, count_of_clicks, last_snapshot)
#                         VALUES (src.user_id, src.user_name, src.count_of_clicks, src.last_snapshot)
#                 """
#                 cursor.execute(aggregate_sql, [max_snapshot, last_snapshot_update, max_snapshot])

#                 print(f"Aggregation executed at {datetime.now()} from {last_snapshot_update} to {max_snapshot}")
#                 time.sleep(5)

#             except Exception as e:
#                 print("Aggregation error:", e)


# def main():
    # parser = argparse.ArgumentParser(description="Kafka to DuckDB streaming pipeline")
    # parser.add_argument("--bootstrap-servers", type=str, default="localhost:9092", help="Kafka bootstrap servers")
    # parser.add_argument("--topic", type=str, default="my_topic", help="Kafka topic to consume from")
    # parser.add_argument("--duration-seconds", type=int, default=20, help="Duration to run the pipeline (seconds)")
    # args = parser.parse_args()

    # con = setup_ducklake()
    # init_db(con)

    # t1 = threading.Thread(target=consume_and_insert, args=(args.bootstrap_servers, args.topic, con, args.duration_seconds))
    # t2 = threading.Thread(target=aggregate_loop, args=(con, args.duration_seconds), daemon=True)

    # t1.start()
    # t2.start()

    # t1.join()
    # t2.join()


if __name__ == "__main__":
    # main()
    ingest_from_api()
