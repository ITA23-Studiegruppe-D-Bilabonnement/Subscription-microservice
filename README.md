# Subscription Management Microservice

This Flask-based microservice provides an API for managing subscriptions, cars, and additional services. It allows users to create, view, and manage subscriptions and additional services stored in a database.

## Endpoints

## Create a New Subscription
  - **URL:** /subscription
  - **Method:** POST
  - **Description:** Creates a new subscription for a customer.
  - **Request Body:**

  ```json
  {
    "customer_id": 1,
    "car_id": 42,
    "additional_service_id": [101, 102],
    "subscription_start_date": "2024-01-01",
    "subscription_end_date": "2024-12-31"
  }
  ```
- **Response:**
  - `201 Created`: Subscription created successfully.
  - `400 Bad Request`: Invalid input, such as additional_service_id not being a list.



## Retrieve Subscriptions by Customer ID
  - **URL:** /subscription/<customer_id>
  - **Method:** GET
  - **Description:** Retrieves all subscriptions for a specific customer.
  - **Path Parameter:**
    customer_id (integer): The ID of the customer.

- **Response:**
  - `200 OK`: Returns a list of subscriptions in JSON format.
  - `404 Not Found`: No subscriptions found for the specified customer.

- **Example Request:**
  ```json
  { 
    GET /subscription/1
  }
    ```
    
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

  
## Retrieve Additional Service by ID
  - **URL:** /additional_services/<service_id>
  - **Method:** GET
  - **Description:** Retrieves details of a specific additional service by its ID.

- **Path Parameter:**
  - **service_id (integer):** The ID of the additional service.

- **Response:**
  - `200 OK:` Returns details of the additional service in JSON format.
  - `404 Not Found:` No additional service found with the specified ID.
Example Request:

```json
{
GET /additional_services/101
}
```

## Cancel subscription
  - **URL:** /cancel_subscription/<subscription_id>
  - **Method:** PATCH
  - **Description:** Cancels an active subscription by setting its status to               inactive and notifying the car microservices to update the car's status.

  - **Path Parameter:**
      - **subscription_id (integer):** The ID of the subscription to be cancelled.
   
  - **Response:**
      - **200 OK:** Subscription cancelled succesfully.
        ```json
        {
        "message": "Subscription cancelled succesfully"
         }
        ```

      - **400 Not Found:** Subscription not found.
        ```json
        {
        "message": "Subscription not found"
        }
        ```

      - **500 Internal Server Error:** An unexpected error occured.
        ```json
        {
        "error": "OOPS! Something went wrong :(",
        "message": "Error details"
        }
        ```






## Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | Yes | - | Secret key for JWT token generation |
| `PORT` | No | 5000 | Port to run the service on |
| `SQLITE_DB_PATH` | Yes | - | Path to SQLite database file |
| `CAR_MICROSERVICE_URL` | Yes | - | Path to SQLite database file |
