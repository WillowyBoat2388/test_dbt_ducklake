import duckdb
import os
from loguru import logger
from dotenv import load_dotenv
logger.add("setup_ducklake.log")
def main(data_path=None):
    """Create a Ducklake with PostgreSQL metadata and local data storage."""

    # Load environment variables
    load_dotenv()

    # Use default data path if not specified  
    data_path = os.getenv('S3_PATH')
    if data_path:
        s3_key = os.getenv('S3_KEY')
        s3_password = os.getenv('S3_SECRET')

        s3_secret = f"""
            CREATE OR REPLACE SECRET secret (
                TYPE s3,
                PROVIDER config,
                KEY_ID '{s3_key}',
                SECRET '{s3_password}',
                REGION 'eu-central-1'
            );
        """
    else:
        data_path = os.getenv('DATA_PATH' or 'dbt_proj/data/lake')
        # Ensure data path exists
        os.makedirs(data_path, exist_ok=True)
     
    # Use local duckdb if object storage not specified
    local_db = os.getenv('DB_PATH')
    if local_db:
        attach_ducklake = f"""
            ATTACH 'ducklake:{local_db}' AS lake (
                DATA_PATH '{data_path}', OVERRIDE_DATA_PATH true
            );
        """    
    else:        
         # Create PostgreSQL secret using environment variables
        host = os.getenv('RDS_HOST')
        port = os.getenv('RDS_PORT', '5432')
        user = os.getenv('RDS_USER')
        password = os.getenv('RDS_PASSWORD')
        db = os.getenv('RDS_DB', 'postgres')
        postgres_secret = f"""
            CREATE SECRET (
                TYPE postgres,
                HOST '{host}',
                PORT {port},
                DATABASE {db},
                USER '{user}',
                PASSWORD '{password}'
            );
        """                   
        attach_ducklake = f"""
            ATTACH 'ducklake:postgres:dbname=postgres' AS lake (
                DATA_PATH '{data_path}', OVERRIDE_DATA_PATH true
            );
        """
        # attach_ducklake = f"""
        #     ATTACH 'ducklake:postgres' AS lake (
        #         DATA_PATH '{data_path}', OVERRIDE_DATA_PATH true
        #     );
        # """

    conn = duckdb.connect()


    # Install required extensions
    logger.info("📦 Installing extensions...")
    conn.execute("INSTALL ducklake;")
    conn.execute("INSTALL postgres;") 
    conn.execute("INSTALL tpch;")

    
    try: 
        conn.execute(s3_secret) 
    except NameError:
        pass

    try: 
        conn.execute(postgres_secret)
    except NameError:
        pass
    
    try: 
        conn.execute(attach_ducklake)
    except :
        pass
    
    try: 
        conn.execute("USE lake;")
    except :
        pass
    
    
    return conn

def stream_api_to_ducklake():
    
    pass

def stream_parquet_to_ducklake():
    pass










