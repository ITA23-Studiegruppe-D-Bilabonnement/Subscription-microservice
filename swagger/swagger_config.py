from flasgger import Swagger

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "specs": [
                {
                    "endpoint": 'homepoint',
                    "route": '/',
                    "spec": '/swagger/homepoint.yaml'
                },
                {
                    "endpoint": 'create_subscription',
                    "route": '/subscription',
                    "spec": '/swagger/create_subscription.yaml'
                },
                {
                    "endpoint": 'get_subscription',
                    "route": '/subscription/<customer_id>',
                    "spec": '/swagger/get_subscription.yaml'
                },
                {
                    "endpoint": 'create_additional_service',
                    "route": '/additional_services',
                    "spec": '/swagger/create_additional_service.yaml'
                },
                {
                    "endpoint": 'get_additional_service',
                    "route": '/additional_services/<service_id>',
                    "spec": '/swagger/get_additional_service.yaml'
                }
            ],
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

template = {
    "info": {
        "title": "Subscription Management Microservice",
        "description": "Microservice for managing subscriptions, cars, and additional services",
        "version": "1.0.0",
        "contact": {
            "name": "KEA",
            "url": "https://kea.dk"
        }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
        }
    }
}

def init_swagger(app):
    """Initialize Swagger with the given Flask app"""
    return Swagger(app, config=swagger_config, template=template)
