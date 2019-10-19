import os
import json
import psycopg2

PG_USER=os.environ['PG_USER']
PG_PASSWORD=os.environ['PG_PASSWORD']
PG_HOST=os.environ['PG_HOST']
PG_PORT=os.environ['PG_PORT']
PG_DATABASE=os.environ['PG_DATABASE']
PGSQL_SELECT_QUERY="SELECT marketid, marketname FROM market WHERE marketid = 42 OR marketid = 10 OR marketid = 17 OR marketid = 19 OR marketid = 23 OR marketid = 33 OR marketid = 1 OR marketid = 40;"

def get_cities(event, context):
    cities=[]

    try:
      connection=psycopg2.connect(user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT, database=PG_DATABASE)
      cursor=connection.cursor()
      cursor.execute(PGSQL_SELECT_QUERY)
      value_records=cursor.fetchall()
    except(Exception, psycopg2.Error) as error:
      print("Error while fetching from PSQL", error)
      return { "statusCode": 500, "body": json.dumps({"message": "Error while fetching data from PostgreSQL"}) }
    finally:
      if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
    for row in value_records:
      cities.append({"id":row[0], "city":row[1]})

    return { "statusCode": 200, "body": json.dumps(cities) }