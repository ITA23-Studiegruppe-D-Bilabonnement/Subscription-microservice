from flask import Flask, jsonify, request
import requests
import sqlite3
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from dotenv import load_dotenv
from flasgger import Swagger, swag_from

app = Flask(__name__)


app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
DB_PATH = os.getenv('SQLITE_DB_PATH')
PORT = int(os.getenv('PORT', 5000))
jwt = JWTManager(app)




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
            additional_service_id INTEGER NOT NULL,   
            subscription_start_date TEXT NOT NULL,
            subscription_end_date TEXT NOT NULL,
            price_per_month FLOAT NOT NULL
    
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



# Create a new subscription
@app.route('/subscription', methods=['POST'])
def create_subscription():
    data = request.get_json()
    required_fields = ['user_id', 'car_id', 'additional_service_id', 'subscription_start_date', 'subscription_end_date', 'price_per_month']
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
        INSERT INTO subscription (user_id, car_id, additional_service_id, subscription_start_date, subscription_end_date, price_per_month)
        VALUES (?, ?, ?, ?, ?, ?)
    ''',( 
        data['user_id'],
        data['car_id'], 
        data['additional_service_id'],
        data['subscription_start_date'], 
        data['subscription_end_date'], 
        data['price_per_month']

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
# ENDPOINTS

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

        results = {}

        # Organize the data in JSON format
        for subscription in subscriptions:
             #Use user_id and subscription_start_date as the key to group the data
            key = (subscription['user_id'], subscription['subscription_start_date'])

            if key not in results:
                    results[key] = {
                        "id": subscription['id'],
                        "user_id": subscription['user_id'],
                        "car_id": subscription['car_id'],
                        "subscription_start_date": subscription['subscription_start_date'],
                        "subscription_end_date": subscription['subscription_end_date'],
                        "price_per_month": subscription['price_per_month'],
                        "additional_services": []
                    }
    
            # Get information about the additional services
            c.execute("SELECT * FROM additional_services WHERE id = ?", (subscription['additional_service_id'],))
            service = c.fetchone()
            if service:
                    results[key]['additional_services'].append({
                        "id": service['id'],
                        "service_name": service['service_name'],
                        "price": service['price'],
                        "description": service['description']
                    })
            
    # Return the combined data, and convert the result to a list
    return jsonify({'subscriptions': list(results.values())}), 200




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





load_dotenv()
#init_db()
app.run(debug=True)