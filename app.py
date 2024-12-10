from flask import Flask, jsonify, request
import requests
import sqlite3
import os
import json
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, get_jwt
from dotenv import load_dotenv
from flasgger import Swagger, swag_from
from swagger.swagger_config import init_swagger

# Load environment variables
load_dotenv()
app = Flask(__name__)

# Environment variables
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
DB_PATH = os.getenv('SQLITE_DB_PATH')
DB_PATH_cars = os.getenv('CAR_MICROSERVICE_URL', "https://cars-microservice-a7g2hqakb2cjffef.northeurope-01.azurewebsites.net")
DB_PATH_customer = os.getenv('CUSTOMER_MICROSERVICE_URL', "https://customer-microservice-b4dsccfkbffjh5cv.northeurope-01.azurewebsites.net")

# Port
PORT = int(os.getenv('PORT', 5000))

# JWT Configuration
jwt = JWTManager(app)

# Initialize Swagger
init_swagger(app)



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
                "PATH": "/create-subscription",
                "METHODS": ["POST"],
                "DESCRIPTION": "Create a new subscription",
                "BODY": {
                "customer_id": "INTEGER (required)",
                "car_id": "INTEGER (required)",
                "additional_service_id": "ARRAY of INTEGER (required)",
                "subscription_start_date": "STRING (YYYY-MM-DD, required)",
                "subscription_end_date": "STRING (YYYY-MM-DD, required)",
                "subscription_status": "BOOLEAN (default: TRUE)"
                }
            },
            {
                "PATH": "/get-subscriptions",
                "METHODS": ["GET"],
                "DESCRIPTION": "Retrieve all subscriptions for the current logged-in user",
                "BODY": {}
            },

            {
                "PATH": "/getall_subscriptions",
                "METHOD": "GET",
                "DESCRIPTION": "Retrieve all subscriptions"
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
            },
            {
                "PATH": "/cancel_subscription/<subscription_id>",
                "METHOD": "PATCH",
                "DESCRIPTION": "Cancel a subscription by setting its status to inactive and notifying the car microservice",
                "PARAMETER": {
                    "subscription_id": "INTEGER"
                },
                "BODY": {
                    "car_id": "INTEGER"
                }
            }
        ]
    })




# -----------------------------------------------------
# CREATE DATABASES

# Database for subscription and additional services 
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscription (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            additional_service_id TEXT NOT NULL,   
            subscription_start_date TEXT NOT NULL,
            subscription_end_date TEXT NOT NULL,
            subscription_status BOOLEAN NOT NULL DEFAULT 1
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
init_db()


# -----------------------------------------------------
# ENDPOINTS POST

# Create a new subscription
@app.route('/create', methods=['POST'])
@jwt_required()
@swag_from("swagger/create_subscription.yaml")
def create_subscription():
    data = request.get_json()
    required_fields = ['car_id', 'additional_service_id', 'subscription_start_date', 'subscription_end_date', 'subscription_status']
    # Standard subscription status is 1 = active
    subscription_status = data.get('subscription_status', True)

    # Get the current logged in user
    current_userid = get_jwt_identity()
    

    # Check if the required fields are present
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400


    # Check if the additional_service_id is a list
    additional_service_id = data['additional_service_id']
    if not isinstance(additional_service_id, list):
            return jsonify({'error': 'additional_service_id must be a list'}), 400


    
    #Notify the cars microservice that a new subscription has been created
    car_id = data['car_id']
    print(car_id)
    try:
        response = requests.put(f"{DB_PATH_cars}/update-status/{car_id}")
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.RequestException as e:    
        print(f"{DB_PATH_cars}/update-status/{car_id}")
        return jsonify({'error': 'Error notifying the car microservice'}), 500
    
    
    # Save additional services as a JSON string
    additional_service_id_json = json.dumps(additional_service_id)

    # Save the subscription to the database
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
        INSERT INTO subscription (customer_id, car_id, additional_service_id, subscription_start_date, subscription_end_date, subscription_status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''',( 
        current_userid,
        data['car_id'], 
        additional_service_id_json,
        data['subscription_start_date'], 
        data['subscription_end_date'], 
        data['subscription_status']
    ))
    conn.commit()
    return jsonify({'message': 'Subscription created successfully'}), 201






# -----------------------------------------------------

# Create additional services
@app.route('/additional_services', methods=['POST'])
@swag_from("swagger/additional_services(post).yaml")
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

# Get a subscription for the current logged in user.
@app.route('/fetch', methods=['GET'])
@jwt_required()
@swag_from("swagger/get_subscription.yaml")
def get_subscription_by_customer():
    
    # Get the current logged in user
    try:
        current_userid = get_jwt_identity()
        
        # Get the token from the Authorization header
        jwt_token = request.headers.get('Authorization', '').split(' ')[1]
        if not jwt_token:
            return jsonify({'error': 'Missing Authorization header'}), 401

        # Prepare the headers for the request to the customer microservice
        headers = {'Authorization': f'Bearer {jwt_token}'}


        try:
            customer_response = requests.get(f"{DB_PATH_customer}/user", headers=headers)
            customer_response.raise_for_status()  # Check if the request was successful
            customer_data = customer_response.json()
            first_name = customer_data.get('first_name', 'Unknown')
            last_name = customer_data.get('last_name', 'Unknown')

        except requests.exceptions.RequestException as e:
            return jsonify({'error': 'Error fetching user data from customer microservice', 'message': str(e)}), 500
     
    
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            # Gets all subscriptions for a customer
            c.execute("SELECT * FROM subscription WHERE customer_id = ?", (current_userid,))
            subscriptions = c.fetchall()

            if not subscriptions:
                return jsonify({'message': 'Subscription not found'}), 404

            results = []


            for subscription in subscriptions:
                # Decode the additional_service_id from JSON
                additional_service_ids = json.loads(subscription['additional_service_id'])
     
                # Get information about the car from the car microservice
                try:
                    response = requests.get(f"{DB_PATH_cars}/cars")
                    response.raise_for_status()  # Check if the request was successful
                    print(f"Car service response: {response.text}")
                    cars = response.json()

                    # Ensure cars is a list
                    if not isinstance(cars, list):
                        return jsonify({'error': 'Invalid response from car microservice'}), 500

                    # Find car details by car_id
                    car = next((car for car in cars if car.get('car_id') == subscription['car_id']), None)
                    car_price = car['price'] if car else 0
                    car_brand = car.get('car_brand', 'Unknown')
                    car_model = car.get('car_model', 'Unknown')
                    engine_type = car.get('engine_type', 'Unknown')

                except requests.exceptions.RequestException as e:
                    print(f"Request error: {e}")
                    car_price = 0
                    car_brand = 'Unknown'
                    car_model = 'Unknown'
                    engine_type = 'Unknown'
                    
                    

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
                    "customer_id": subscription['customer_id'],
                    "first_name": first_name,
                    "last_name": last_name,
                    "car_id": subscription['car_id'],
                    "subscription_start_date": subscription['subscription_start_date'],
                    "subscription_end_date": subscription['subscription_end_date'],
                    "subscription_status": subscription['subscription_status'],
                    "car_price": car_price,
                    "car_brand": car_brand,
                    "car_model": car_model,
                    "engine_type": engine_type,
                    "additional_service": additional_services,
                    "total_price": total_price
                })

        return jsonify({'subscriptions': results}), 200

    except Exception as e:
        print(f"Internal server error: {e}")
        return jsonify({'error': 'Internal server error occurred'}), 500






# -----------------------------------------------------
# Get all subscriptions

@app.route('/getall_subscriptions', methods=['GET'])
@swag_from("swagger/getall_subscriptions.yaml")
def get_all_subscriptions():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM subscription")
        subscriptions = c.fetchall()

    if not subscriptions:
        return jsonify({'message': 'Subscriptions not found'}), 404

    return jsonify({'subscriptions': [dict(row) for row in subscriptions]}), 200






# -----------------------------------------------------
# Get additional services by service_id

@app.route('/additional_services/<int:service_id>', methods=['GET'])
@swag_from("swagger/service_id(get).yaml")
def get_additional_services_by_id(service_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM additional_services WHERE id = ?", (service_id,))
        additional_services = c.fetchall()

    if not additional_services:
        return jsonify({'message': 'Additional services not found'}), 404
    

    return jsonify({'additional_services': [dict(row) for row in additional_services]}), 200






# -----------------------------------------------------
# Cancel subscription

@app.route('/cancel_subscription/<int:subscription_id>', methods=['PATCH'])
@swag_from("swagger/cancel_subscription.yaml")
def cancel_subscription(subscription_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT car_id FROM subscription WHERE id = ?", (subscription_id,))
        result = c.fetchone()

        if not result:
            return jsonify({'message': 'Subscription not found'}), 404

        car_id = result[0]


    #Notify the cars microservice that subscription has been deactivated
    test = requests.put(f"{DB_PATH_cars}/update-status/{car_id}")
    print(test)
    print(f"{DB_PATH_cars}/update-status/{car_id}")
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE subscription SET subscription_status = 0 WHERE id = ?", (subscription_id,))
        conn.commit()

    return jsonify({'message': 'Subscription cancelled successfully'}), 200





if __name__ == '__main__':
    app.run(debug=True)