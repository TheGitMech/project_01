import MySQLdb
from config import MYSQL_CONFIG

def init_database():
    try:
        # Connect to MySQL server
        connection = MySQLdb.connect(
            host=MYSQL_CONFIG['HOST'],
            user=MYSQL_CONFIG['USER'],
            password=MYSQL_CONFIG['PASSWORD'],
            port=int(MYSQL_CONFIG['PORT'])
        )
        cursor = connection.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['DB']}")
        cursor.execute(f"USE {MYSQL_CONFIG['DB']}")

        # Read and execute the schema.sql file
        with open('schema.sql', 'r') as f:
            sql_commands = f.read()
            
        # Split and execute multiple SQL commands
        for command in sql_commands.split(';'):
            if command.strip():
                cursor.execute(command + ';')
        
        # Commit the changes
        connection.commit()
        print("Database initialized successfully!")

    except MySQLdb.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    init_database() 