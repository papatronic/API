import os
import psycopg2
import numpy as np
import json

PG_USER=os.environ['PG_USER']
PG_PASSWORD=os.environ['PG_PASSWORD']
PG_HOST=os.environ['PG_HOST']
PG_PORT=os.environ['PG_PORT']
PG_DATABASE=os.environ['PG_DATABASE']

# Funcion encargada para revertir la escala del valor predecido
def reverseScale(x_scaled, x_min, x_max, r_min = 0, r_max = 1):
  scale = (r_max - r_min) / (x_max - x_min)
  X = (x_scaled - r_min + (x_min * scale)) / scale  
  return X

def scaleValues(x, x_min, x_max, r_min = 0, r_max = 1):
  scale = (r_max - r_min) / (x_max - x_min)
  X_scaled = (scale * x) + r_min - (x_min * scale)
  return X_scaled

def predict_many(event, context):

  try:
    typee = event['type']
    marketId = event['id']
  except:
    return { "statusCode": 412, "body": json.dumps({"message": "Ingrese todos los datos"}) }
    
  if typee == 0:
    endMarketId = 1
    sourceMarketId = marketId
  if typee == 1:
    endMarketId = marketId
    sourceMarketId = 1

  x_db = []
  x_min = 0
  x_max = 0

  # Los modelos corresponden a los siguientes destinos:
  # type =1
  # Sinaloa como origen
  # id origen: 1
  # id destino: 10, 17, 19, 23, 33, 40

  # type = 0
  # Sinaloa como destino
  # id origen: 42 = jalisco
  # id destino: 1

  try:
    connection = psycopg2.connect(user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT, database=PG_DATABASE)
    cursor = connection.cursor()
      
    postgreSQL_select_Query = "select price from normalized_price where sourcemarketid = {} and endmarketid = {} order by sniimdate desc limit 25".format(sourceMarketId, endMarketId)
    cursor.execute(postgreSQL_select_Query)
    #print("Selecting rows from mobile table using cursor.fetchall")
    value_records = cursor.fetchall()
    #Save each column value into the correspondent  array
    for row in value_records:
        x_db.append(row[0])
      
    postgreSQL_select_Query = "select (select marketName from market where marketid = {}), (select marketName from market where marketid = {})".format(sourceMarketId, endMarketId)
    cursor.execute(postgreSQL_select_Query)
    #print("Selecting rows from mobile table using cursor.fetchall")
    value_records = cursor.fetchall()
    #Save each column value into the correspondent  array
    sourceMarketName = value_records[0][0]
    endMarketName = value_records[0][1]
          
    postgreSQL_select_Query = "select min(price), max(price) from normalized_price"
    cursor.execute(postgreSQL_select_Query)
    #print("Selecting rows from mobile table using cursor.fetchall")
    value_records = cursor.fetchall()
    #Save each column value into the correspondent variable
    x_min = np.float32(value_records[0][0])
    x_max = np.float32(value_records[0][1])     
  except (Exception, psycopg2.Error) as error :
    print ("Error while fetching data from PostgreSQL", error)
    return { "statusCode": 500, "body": json.dumps({"message": "Error while fetching data from PSQL"}) }
  finally:
    #closing database connection.
    if(connection):
      cursor.close()
      connection.close()
      print("PostgreSQL connection is closed")


  modelName = "{} {}.h5".format(sourceMarketName, endMarketName).replace(':', '')
  try:
    model = load_model(modelName)
  except:
    return { "statusCode": 501, "body": json.dumps({"message": "El modelo aun no ha sido generado."}) }

  for con in range(0, len(x_db)):
    x_db[con] = scaleValues(float(x_db[con]), x_min, x_max)


  x_db.reverse()
  x_db = np.asarray(x_db)
  x_db = x_db.reshape((1, x_db.shape[0]))

  weekdayPredictions = []
  # 5 elementos
  for con in range(0, 5):
    pday = model.predict(x_db, 10, verbose=0)
    x_db = np.reshape(x_db, x_db.shape[1])
    x_db = np.delete(x_db, 0)
    x_db = np.append(x_db, pday)
    x_db = x_db.reshape(1,x_db.shape[0])
    reverseScaledPrediction = reverseScale(pday[0][0], x_min, x_max)
    weekdayPredictions.append(reverseScaledPrediction)
      
  return { "statusCode": 200, "body": json.dumps(weekdayPredictions) }