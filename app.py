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


@app.route("/")
def hello():
    return "Hello World!"


# Database initialization
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscription (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            car_model TEXT NOT NULL,
            subsription_start_date TEXT NOT NULL,
            subscription_end_date TEXT NOT NULL,
            price_per_month FLOAT NOT NULL
    
        );
    ''')
    conn.commit()
    conn.close()



# Create a new subscription

@app.route('/subscription', methods=['POST'])
def create_subscription():
    data = request.get_json()
    required_fields = ['user_id', 'car_id', 'first_name', 'last_name', 'email', 'car_model', 'subsription_start_date', 'subscription_end_date', 'price_per_month']
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
        INSERT INTO subscription (user_id, car_id, first_name, last_name, email, car_model, subsription_start_date, subscription_end_date, price_per_month)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',( 
        data['user_id'],
        data['car_id'],
        data['first_name'], 
        data['last_name'], 
        data['email'], 
        data['car_model'], 
        data['subsription_start_date'], 
        data['subscription_end_date'], 
        data['price_per_month']

    ))
    conn.commit()
    return jsonify({'message': 'Subscription created successfully'}), 201





# Get a subscription by User_id
@app.route('/subscription/<int:user_id>', methods=['GET'])
def get_subscription_by_user(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM subscription WHERE user_id = ?", (user_id,))
        subscriptions = c.fetchall()

    if not subscriptions:
        return jsonify({'message': 'Subscription not found'}), 404
    

    return jsonify({'subscriptions': [dict(row) for row in subscriptions]}), 200






load_dotenv()
init_db()
app.run(debug=True)