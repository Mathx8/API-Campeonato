from config import db
import sqlite3
from datetime import datetime
import os
import pandas as pd

def create_sqlite_backup():
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    
    supabase_engine = db.get_engine()
    with sqlite3.connect(backup_path) as sqlite_conn:
        for table in db.metadata.tables.keys():
            df = pd.read_sql_table(table, supabase_engine)
            df.to_sql(table, sqlite_conn, if_exists='replace', index=False)
    
    return backup_path