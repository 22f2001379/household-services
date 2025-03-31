from flask_restful import Api, Resource, reqparse
from .models import *
from flask_security import auth_required, roles_required, roles_accepted, current_user

api = Api()

from flask_restful import Api, Resource
from flask_security import auth_required, current_user
from .models import Service, User
from .database import db

api = Api()

def roles_list(roles):
    """Convert roles to a list of role names."""
    return [role.name for role in roles]

parser = reqparse.RequestParser()

parser.add_argument("name")
parser.add_argument("base_price")
parser.add_argument("time_required")
parser.add_argument("description")

class ServiceApi (Resource):
    @auth_required('token')  # Ensure the user is authenticated
    def get(self):
        # Check if the current user is an admin
        if "admin" in roles_list(current_user.roles):
            # Admin can see all services
            services = Service.query.all()
        else:
            # Non-admin users can only see their associated services
            # Assuming a relationship between User and Service exists
            services = current_user.services  # This requires a relationship in the User model

        # Convert services to JSON
        service_json = [{
            "id": service.id,
            "name": service.name,
            "base_price": service.base_price,
            "time_required": service.time_required,
            "description": service.description
        } for service in services]

        return {"services": service_json}, 200

    @auth_required("token")
    @roles_required("user")
    def post(self):
        args = parser.parse_args()
        service = Service(name = args["name"],
        base_price = args["base_price"],
        time_required = args["time_required"],
        description = args["description"],
        user_id = current_user.id)

        db.session.add(service)
        db.session.commit()
        return{
            "message": "service created succesfully."
        }


api.add_resource(ServiceApi , "/api/get", "/api/create")

