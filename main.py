import random
import json
from flask import Flask, jsonify, request
import psycopg2
import numpy as np
from keras.models import load_model

app = Flask(__name__)

@app.route('/get-origins', methods=['GET'])
def getOrigins():
    cities = []
    x_json = ''

    try:
        connection = psycopg2.connect(user = "postgres", password = "r351d3nc14501", host = "127.0.0.1", port = "5432", database = "potatoe_markets")
        cursor = connection.cursor()

        postgreSQL_select_Query = "SELECT * FROM market_origins"
        cursor.execute(postgreSQL_select_Query)
        value_records = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error obteniendo los datos de PostgreSQL", error)
    finally:
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    for row in value_records:
        x_json = {"id":row[1], "city":row[2]}
        cities.append(x_json)
    return jsonify(cities)


@app.route('/get-destination', methods=['GET'])
def getOrigins():
    cities = []
    x_json = ''

    try:
        connection = psycopg2.connect(user = "postgres", password = "r351d3nc14501", host = "127.0.0.1", port = "5432", database = "potatoe_markets")
        cursor = connection.cursor()

        postgreSQL_select_Query = "SELECT * FROM market_destination"
        cursor.execute(postgreSQL_select_Query)
        value_records = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error obteniendo los datos de PostgreSQL", error)
    finally:
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    for row in value_records:
        x_json = {"id":row[1], "city":row[2]}
        cities.append(x_json)
    return jsonify(cities)

@app.route('/get-cities', methods=['GET'])
def getCities():
    
    cities = []
    x_json = ''

    try:
        connection = psycopg2.connect(user = "postgres", password = "r351d3nc14501", host = "127.0.0.1", port = "5432", database = "potatoe_markets")
        cursor = connection.cursor()
        
        postgreSQL_select_Query = "SELECT marketid, marketname FROM market WHERE marketid= 42 OR marketid= 10 OR marketid= 17 OR marketid= 19 OR marketid= 23 OR marketid= 33 OR marketid= 1 OR marketid= 40;"
        cursor.execute(postgreSQL_select_Query)
        #print("Selecting rows from mobile table using cursor.fetchall")
        value_records = cursor.fetchall()
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    for row in value_records:
        x_json = {"id":row[0], "city":row[1]}
        cities.append(x_json)

    return jsonify(cities)


@app.route('/predict', methods=['POST'])
def predictMany():
    
    try:
        typee = request.json['type']
        marketId = request.json['id']
    except:
        return jsonify({'error': 'Ingrese todos los datos'})
    
    if typee == 0:
        endMarketId = 1
        sourceMarketId = marketId
    if typee == 1:
        endMarketId = marketId
        sourceMarketId = 1

    x_db = []
    x_min = 0
    x_max = 0

    try:
        connection = psycopg2.connect(user = "postgres", password = "r351d3nc14501", host = "127.0.0.1", port = "5432", database = "potatoe_markets")
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
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


    modelName = "{} {}.h5".format(sourceMarketName, endMarketName).replace(':', '')
    #model = load_model('Modelo_Zacatecas_Mercado_Abastos_Zacatecas.h5')
    try:
        model = load_model(modelName)
    except:
        return jsonify({'error': 'El modelo aun no ha sido generado'})    

    def scaleValues(x, x_min, x_max, r_min = 0, r_max = 1):
        scale = (r_max - r_min) / (x_max - x_min)
        X_scaled = (scale * x) + r_min - (x_min * scale)
        return X_scaled


    for con in range(0, len(x_db)):
        x_db[con] = scaleValues(float(x_db[con]), x_min, x_max)


    x_db.reverse()
    x_db = np.asarray(x_db)
    x_db = x_db.reshape((1, x_db.shape[0]))

    #Funcion encargada para revertir la escala del valor predecido
    def reverseScale(x_scaled, x_min, x_max, r_min = 0, r_max = 1):
        scale = (r_max - r_min) / (x_max - x_min)
        X = (x_scaled - r_min + (x_min * scale)) / scale  
        return X

    weekdayPredictions = []
    #5 elementos
    for con in range(0, 5):
        pday = model.predict(x_db, 10, verbose=0)
        x_db = np.reshape(x_db, x_db.shape[1])
        x_db = np.delete(x_db, 0)
        x_db = np.append(x_db, pday)
        x_db = x_db.reshape(1,x_db.shape[0])
        reverseScaledPrediction = reverseScale(pday[0][0], x_min, x_max)
        weekdayPredictions.append(reverseScaledPrediction)
        
    return jsonify(weekdayPredictions)


if __name__ == '__main__':
    app.run(debug=True)



