# snowflake_utils.py
import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_data_from_snowflake():
    desired_topics = ["Market Efficiency", "Equity Valuation: Concepts and Basic Tools", "Introduction to Industry and Company Analysis"]
    
    # Initialize Snowflake connection
    snowflake_ctx = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )
    
    where_clause = f"WHERE TOPICNAME IN ({', '.join(['%s' for _ in desired_topics])})"
    sql_query = "SELECT INTRODUCTION, LEARNINGOUTCOME, SUMMARY, TOPICNAME FROM cleaned_extracted {}".format(where_clause)
    
    # Executing the SQL query
    try:
        with snowflake_ctx.cursor() as cur:
            cur.execute(sql_query, desired_topics)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return {"columns": columns, "rows": rows}
    finally:
        snowflake_ctx.close()
