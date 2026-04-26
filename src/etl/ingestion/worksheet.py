from info import *

COMPANY_HEADER="""


"""

RAW_TABLE_DEFINITIONS="""
        timestamp TIMESTAMP,
        user_id VARCHAR,
        user_name VARCHAR,
        event_type VARCHAR
    """

DEST_TABLE_DEFINITIONS="""
        user_id VARCHAR,
        user_name VARCHAR,
        count_of_clicks BIGINT,
        last_snapshot INT,        
    """