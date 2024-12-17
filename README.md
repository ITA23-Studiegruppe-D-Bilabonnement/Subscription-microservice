# Subscription Management Microservice

This microservice is designed for managing customer subscriptions, associated car details, and additional services. Built with Flask, it provides a RESTful API to handle the creation, retrieval, and management of subscriptions and services. The service interacts with a SQLite database and integrates with external microservices.


## File structure
```
project/
├── app.py                   
├── swagger/                 
│   ├── additional_services(post).yaml          
│   ├── cancel_subscription.yaml           
│   ├── create_subscription.yaml        
│   ├── get_subscription.yaml    
│   └── getall_subscriptions.yaml
    ├── service_id(get).yaml    
    ├── swagger_config.py    
├── .dockerignore            
├── .env                     
├── .github/                 
│   └── workflows/           
│       └── main_Subscription-microservice.yml 
├── .gitignore               
├── Dockerfile               
├── README.md                
├── requirements.txt
```



## Available Endpoints

### Subscriptions
- `POST /create`: Create a new subscription.
- `GET /fetch`: Retrieve subscriptions logged-in user.
- `PATCH /cancel_subscription/<subscription_id>`: Cancel an active subscription.
- `GET /getall_subscriptions`: Get all subscriptions.

### Additional Services
- `POST /additional_services`: Add a new additional service.
- `GET /additional_services/<service_id>`: Retrieve additional service details by ID.





## Create a New Subscription
  - **URL:** /create
  - **Method:** POST
  - **Description:** Creates a new subscription for a customer.
  - **Request Body:**

  ```json
  {
    "car_id": 42,
    "additional_service_id": [101, 102],
    "subscription_start_date": "2024-01-01",
    "subscription_end_date": "2024-12-31",
    "subscription_status": true
  }
  ```
- **Response:**
  - `201 Created`: Subscription created successfully.
  - `400 Bad Request`: Invalid input, such as additional_service_id not being a list.
  - `500 Internal server error`: Unexpected error.

    ***Example of error messages (400)***
    
      ```json
   {
    "error": "car_id is required"
   }
    ```
  
      ```json
   {
    "error": "Dates must be in YYYY-MM-DD format"
   }
    ```
  
     ```json
   {
    "error": "Car with ID 123 not found"
   }
    ```
  
     ```json
   {
    "error": "Car with ID 123 is already rented"
   }
    ```
  
     ```json
   {
    "error": "additional_service_id must be a list"
   }
    ```
  
     ```json
   {
    "error": "Additional service with ID 456 not found"
   }
    ```     


## Retrieve Subscriptions by current_userid
  - **URL:** /fetch
  - **Method:** GET
  - **Description:** Retrieves all subscriptions for the logged-in user. 
 
- **Response:**
  - `200 OK`: Returns a list of subscriptions in JSON format.
  - `401 Unauthorized`: Missing or invalid Authorization header.
  - `404 Not Found`: No subscriptions found for the specified customer.
  - `500 Internal server error`: Issues with external services or database.



## Get all created subscriptions
  - **URL:** /getall_subscriptions
  - **Method:** GET
  - **Description:** Retrieves all created subscriptions from database

- **Response:**
  - `200 OK`: Returns a list of all subscriptions.    
  - `404 Not found`: If no subscriptions are found in the database.



## Cancel Subscription
  - **URL:** `/cancel_subscription/<subscription_id>`
  - **Method:** PATCH
  - **Description:** Cancels an active subscription by setting its status to inactive and notifying the car microservice to update the car's status.

  - **Response**
    - `200 OK`: Subscription cancelled successfully
    - `404 Not found`: If no subscriptions are found in the database



    
  ## Add a New Additional Service
    - **URL:** /additional_services
    - **Method:** POST
    - **Description:** Adds a new additional service to the database.
    - **Request Body:**

    ```json
    {
    "service_name": "Premium Wash",
    "price": 250.0,
    "description": "A complete car wash with premium wax and polish"
    }
    ```

- **Response:**
  - `201 Created:` Additional service created successfully.
  - `400 Bad Request:` Invalid input, such as missing required fields.
  - `500 Internal server error:` Unexpected error.

  

## Retrieve Additional Service by ID
  - **URL:** /additional_services/<service_id>
  - **Method:** GET
  - **Description:** Retrieves details of a specific additional service by its ID.

- **Response:**
  - `200 OK:` Returns details of the additional service in JSON format.
  - `404 Not Found:` No additional service found with the specified ID.



## Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | Yes | - | Secret key for JWT token generation |
| `PORT` | No | 5000 | Port to run the service on |
| `SQLITE_DB_PATH` | Yes | - | Path to SQLite database file |
| `CAR_MICROSERVICE_URL` | Yes | - | Path to the car microservice for status updates and retrievals |
|`CUSTOMER_MICROSERVICE_URL` | Yes | - | Path to the customer microservice for retrievals |
