import os
import django
import sqlite3
import mysql.connector
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udemyclone.settings')
django.setup()

def get_sqlite_data():
    """Get all data from SQLite database"""
    sqlite_conn = sqlite3.connect('db.sqlite3')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all tables
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = sqlite_cursor.fetchall()
    
    data = {}
    for table in tables:
        table_name = table[0]
        if table_name not in ['django_migrations', 'sqlite_sequence']:
            try:
                # Get column names
                sqlite_cursor.execute(f"PRAGMA table_info('{table_name}');")
                columns = [col[1] for col in sqlite_cursor.fetchall()]
                
                # Get data - using parameterized query for safety
                sqlite_cursor.execute(f"SELECT * FROM '{table_name}';")
                rows = sqlite_cursor.fetchall()
                
                data[table_name] = {
                    'columns': columns,
                    'rows': rows
                }
            except sqlite3.OperationalError as e:
                print(f"Error processing table {table_name}: {e}")
                continue
    
    sqlite_conn.close()
    return data

def migrate_to_mysql(data):
    """Migrate data to MySQL"""
    mysql_conn = mysql.connector.connect(
        host='localhost',
        user='pcl_user',
        password='pcl_password',
        database='pcl_db'
    )
    mysql_cursor = mysql_conn.cursor()
    
    # Define the order of tables to migrate
    table_order = [
        'accounts_user',
        'django_content_type',
        'auth_permission',
        'auth_group',
        'accounts_user_groups',
        'accounts_user_user_permissions',
        'django_admin_log',
        'django_session',
        'courses_category',
        'courses_course',
        'courses_lesson',
        'udemy_enroll'
    ]
    
    # Disable foreign key checks
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    # First, clear existing data from MySQL tables
    for table_name in reversed(table_order):
        try:
            mysql_cursor.execute(f"DELETE FROM {table_name};")
        except mysql.connector.Error as err:
            print(f"Error clearing table {table_name}: {err}")
    
    # Migrate data in the specified order
    for table_name in table_order:
        if table_name not in data:
            print(f"Table {table_name} not found in SQLite data")
            continue
            
        table_data = data[table_name]
        if not table_data['rows']:
            continue
            
        columns = table_data['columns']
        rows = table_data['rows']
        
        # Prepare insert statement
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});"
        
        # Insert data
        for row in rows:
            try:
                # Convert any None values to NULL for MySQL
                row = [None if val is None else val for val in row]
                mysql_cursor.execute(insert_query, row)
            except mysql.connector.Error as err:
                if err.errno == 1062:  # Duplicate entry error
                    print(f"Skipping duplicate entry in {table_name}")
                    continue
                print(f"Error inserting into {table_name}: {err}")
                print(f"Row data: {row}")
                print(f"Columns: {columns}")
                print(f"Query: {insert_query}")
    
    # Re-enable foreign key checks
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    mysql_conn.commit()
    mysql_conn.close()

def verify_migration():
    """Verify the migration by comparing record counts"""
    sqlite_conn = sqlite3.connect('db.sqlite3')
    sqlite_cursor = sqlite_conn.cursor()
    
    mysql_conn = mysql.connector.connect(
        host='localhost',
        user='pcl_user',
        password='pcl_password',
        database='pcl_db'
    )
    mysql_cursor = mysql_conn.cursor()
    
    # Get all tables
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = sqlite_cursor.fetchall()
    
    print("\nVerifying migration...")
    for table in tables:
        table_name = table[0]
        if table_name not in ['django_migrations', 'sqlite_sequence', 'table-name']:
            try:
                # Get SQLite count
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM '{table_name}';")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                # Get MySQL count
                mysql_cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                mysql_count = mysql_cursor.fetchone()[0]
                
                print(f"{table_name}: SQLite={sqlite_count}, MySQL={mysql_count}")
                if sqlite_count != mysql_count:
                    print(f"WARNING: Count mismatch for {table_name}!")
            except Exception as e:
                print(f"Error verifying table {table_name}: {e}")
    
    sqlite_conn.close()
    mysql_conn.close()

def main():
    print("Starting migration from SQLite to MySQL...")
    
    # Get data from SQLite
    print("Reading data from SQLite...")
    data = get_sqlite_data()
    
    # Migrate to MySQL
    print("Migrating data to MySQL...")
    migrate_to_mysql(data)
    
    # Verify migration
    verify_migration()
    
    print("\nMigration completed!")

if __name__ == '__main__':
    main() 