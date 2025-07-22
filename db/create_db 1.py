import psycopg2
from psycopg2 import sql

#This is to connect to your own database in your own pc. The port may be different so, check to be sure
host = "localhost"
port = "5432"
dbname = "postgres"
user = "postgres"
password = "cos101"

new_dbname = "panaview_db" # This is the name of our database we will be working with

try:
    # Connect to the PostgreSQL server
    connection = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    connection.autocommit = True  # Enable autocommit mode
    print("Connection to PostgreSQL server successful")

    cursor = connection.cursor()

    # This is the SQL statement to create a new database
    create_db_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_dbname))

    cursor.execute(create_db_query)
    print(f"Database '{new_dbname}' created successfully")
    
    cursor.close()
    connection.close()

except Exception as error:
    print(f"Error creating the database: {error}")
