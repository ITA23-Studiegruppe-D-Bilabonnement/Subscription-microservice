# Subscription Management Microservice

This microservice is designed for managing customer subscriptions, associated car details, and additional services. Built with Flask, it provides a RESTful API to handle the creation, retrieval, and management of subscriptions and services. The service interacts with a SQLite database and integrates with external microservices.


## Available Endpoints

### Subscriptions
- `POST /create`: Create a new subscription.
- `GET /fetch`: Retrieve subscriptions logged-in user.
- `PATCH /cancel_subscription/<subscription_id>`: Cancel an active subscription.

### Additional Services
- `POST /additional_services`: Add a new additional service.
- `GET /additional_services/<service_id>`: Retrieve additional service details by ID.




## Endpoints

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
    "subscriptions_status": true
  }
  ```
- **Response:**
  - `201 Created`: Subscription created successfully.
  - `400 Bad Request`: Invalid input, such as additional_service_id not being a list.



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
  - ***URL:*** /getall_subscriptions
  - ***Method:*** GET
  - ***Description:*** Retrieves all created subscriptions from database

- **Response:**
  - `200 OK`: Returns a list of all subscriptions.

  ```json
{
  "subscriptions": [
    {
      "id": 1,
      "customer_id": 123,
      "car_id": 42,
      "additional_service_id": "[1, 2, 3]",
      "subscription_start_date": "2024-01-01",
      "subscription_end_date": "2024-12-31",
      "subscription_status": true
    },
    {
      "id": 2,
      "customer_id": 124,
      "car_id": 43,
      "additional_service_id": "[4, 5]",
      "subscription_start_date": "2024-02-01",
      "subscription_end_date": "2024-12-31",
      "subscription_status": false
    }
  ]
}

  ```
  - `404 Not found`: If no subscriptions are found in the database.





## Cancel Subscription
  - **URL:** `/cancel_subscription/<subscription_id>`
  - **Method:** PATCH
  - **Description:** Cancels an active subscription by setting its status to inactive and notifying the car microservice to update the car's status.

  
**Path Parameter:**
- `subscription_id (integer)`: The ID of the subscription to be cancelled.

### Example Response:
- **200 OK:**
  ```json
  {
    "message": "Subscription cancelled successfully"
  }

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

### Example Request:
`GET /additional_services/101`

### Example Response:
```json
{
  "id": 101,
  "service_name": "Premium Wash",
  "price": 250.0,
  "description": "A complete car wash with premium wax and polish"
}





## Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | Yes | - | Secret key for JWT token generation |
| `PORT` | No | 5000 | Port to run the service on |
| `SQLITE_DB_PATH` | Yes | - | Path to SQLite database file |
| `CAR_MICROSERVICE_URL` | Yes | - | Path to the car microservice for status updates and retrievals |
