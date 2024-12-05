from flask import Flask, jsonify, request
import requests
import sqlite3
import os
import json
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from dotenv import load_dotenv
from flasgger import Swagger, swag_from

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Environment variables
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
DB_PATH = os.getenv('SQLITE_DB_PATH')
DB_PATH2 = os.getenv('CAR_MICROSERVICE_URL')

PORT = int(os.getenv('PORT', 5000))


# JWT Configuration
jwt = JWTManager(app)


# Homepoint - "/"
@app.route("/", methods=["GET"])
def homepoint():
    return jsonify({
        "SERVICE": "SUBSCRIPTION MANAGEMENT MICROSERVICE",
        "AVAILABLE ENDPOINTS": [
            {
                "PATH": "/",
                "METHOD": "GET",
                "DESCRIPTION": "Shows available endpoints and service information"
            },
            {
                "PATH": "/subscription",
                "METHOD": "POST",
                "DESCRIPTION": "Create a new subscription",
                "BODY": {
                    "user_id": "INTEGER",
                    "car_id": "INTEGER",
                    "additional_service_id": "INTEGER",
                    "subscription_start_date": "STRING (YYYY-MM-DD)",
                    "subscription_end_date": "STRING (YYYY-MM-DD)",
                    "price_per_month": "FLOAT"
                }
            },
            {
                "PATH": "/subscription/<user_id>",
                "METHOD": "GET",
                "DESCRIPTION": "Retrieve subscriptions for a specific user",
                "PARAMETER": {
                    "user_id": "INTEGER"
                }
            },
            {
                "PATH": "/additional_services",
                "METHOD": "POST",
                "DESCRIPTION": "Create a new additional service",
                "BODY": {
                    "service_name": "STRING",
                    "price": "FLOAT",
                    "description": "STRING"
                }
            },
            {
                "PATH": "/additional_services/<service_id>",
                "METHOD": "GET",
                "DESCRIPTION": "Retrieve details of an additional service by ID",
                "PARAMETER": {
                    "service_id": "INTEGER"
                }
            }
        ]
    })





# CREATE DATABASES
# Database for subscription and additional services 
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscription (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            additional_service_id TEXT NOT NULL,   
            subscription_start_date TEXT NOT NULL,
            subscription_end_date TEXT NOT NULL
        );
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS additional_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            price FLOAT NOT NULL,
            description TEXT
        );
    ''')
    conn.commit()
    conn.close()


# -----------------------------------------------------
# ENDPOINTS POST

# Create a new subscription
@app.route('/subscription', methods=['POST'])
def create_subscription():
    data = request.get_json()
    required_fields = ['user_id', 'car_id', 'additional_service_id', 'subscription_start_date', 'subscription_end_date']
    

    # Check if the additional_service_id is a list
    additional_service_id = data['additional_service_id']
    if not isinstance(additional_service_id, list):
            return jsonify({'error': 'additional_service_id must be a list'}), 400


    # Save additional services as a list
    additional_service_id_json = json.dumps(additional_service_id)

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
        INSERT INTO subscription (user_id, car_id, additional_service_id, subscription_start_date, subscription_end_date)
        VALUES (?, ?, ?, ?, ?)
    ''',( 
        data['user_id'],
        data['car_id'], 
        additional_service_id_json,
        data['subscription_start_date'], 
        data['subscription_end_date'] 
    ))
    conn.commit()
    return jsonify({'message': 'Subscription created successfully'}), 201



# Create additional services
@app.route('/additional_services', methods=['POST'])
def create_additional_services():
    data = request.get_json()
    required_fields = ['service_name', 'price', 'description']
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
        INSERT INTO additional_services (service_name, price, description)
        VALUES (?, ?, ?)
    ''',( 
        data['service_name'],
        data['price'],
        data['description']
    ))
    conn.commit()
    return jsonify({'message': 'Additional service created successfully'}), 201



# -----------------------------------------------------
# ENDPOINTS GET

# Get a subscription by User_id
@app.route('/subscription/<int:user_id>', methods=['GET'])
def get_subscription_by_user(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Gets all subscriptions for a user
        c.execute("SELECT * FROM subscription WHERE user_id = ?", (user_id,))
        subscriptions = c.fetchall()

        # If no subscriptions are found, return 404
        if not subscriptions:
            return jsonify({'message': 'Subscription not found'}), 404

        results = []

        # Organize the data in JSON format
        for subscription in subscriptions:

            # Decode the additional_service_id from JSON
            additional_service_ids = json.loads(subscription['additional_service_id'])



            # Get the price of the car from the car microservice
            try:
                response = requests.get(f"{DB_PATH2}/cars")
                cars = response.json()

                # Find the price of the car by car_id
                car = next((car for car in cars if car['id'] == subscription['car_id']), None)

                # If the car exists, get the price or set it to 0
                car_price = car['price'] if car else 0
            
            except requests.exceptions.RequestException as e:
                car_price = 0



            # Get information about the additional services
            additional_services = []
            for service_id in additional_service_ids:
                c.execute("SELECT * FROM additional_services WHERE id = ?", (service_id,))
                service = c.fetchone()
                if service:
                    additional_services.append({
                        "id": service['id'],
                        "service_name": service['service_name'],
                        "price": service['price'],
                        "description": service['description']
                    })

         
            # Calculate the total price of additional services and the subscription
            price_of_additional_services = sum(service["price"] for service in additional_services)
            total_price = car_price + price_of_additional_services


        # Get the results in a list
            results.append({
                "id": subscription['id'],
                "user_id": subscription['user_id'],
                "car_id": subscription['car_id'],
                "subscription_start_date": subscription['subscription_start_date'],
                "subscription_end_date": subscription['subscription_end_date'],
                "car_price": car_price,
                "additional_service": additional_services,
                "total_price": total_price 
            })


# Return the combined data, and convert the result to a list
    return jsonify({'subscriptions': results}), 200




# Get additional services by service_id
@app.route('/additional_services/<int:service_id>', methods=['GET'])
def get_additional_services_by_id(service_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM additional_services WHERE id = ?", (service_id,))
        additional_services = c.fetchall()

    if not additional_services:
        return jsonify({'message': 'Additional services not found'}), 404
    

    return jsonify({'additional_services': [dict(row) for row in additional_services]}), 200






init_db()
app.run(debug=True)