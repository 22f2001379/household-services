from flask import current_app as app, jsonify, request
from flask_security import auth_required, roles_required, current_user, hash_password
from .database import db
from .models import *
from datetime import datetime
from flask_cors import cross_origin
# @app.route('/', methods=['GET'])
# def home():
#     return "This is my homepage."

@app.route('/api/home')
@auth_required('token')
@roles_required(['user', 'admin'])
def user_home():
    user = current_user
    return jsonify({"message": "Welcome!", "user_email": user.email})

@app.route('/api/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def login_user():
    credentials = request.get_json()
    if not credentials or 'email' not in credentials or 'password' not in credentials:
        return jsonify({"error": "Email and password are required"}), 400

    email = credentials['email']
    password = credentials['password']

    userDetails = User.query.filter_by(email=email, password=password).first()
    user = app.security.datastore.find_user(email=email)
    if not user or user.password != password:  # Compare the plain text password directly
        return jsonify({"error": "Invalid email or password"}), 401

    if userDetails.role_id == 3 and userDetails.approved == False:
        return jsonify({"error": "Account is not approved. Please contact admin!"}), 403

    # Generate the response with user data
    response = {
        "message": "Login successful!",
        "user": {
            "email": user.email,
            "roles": [role.name for role in user.roles],
            "id": userDetails.id,
            "approved": user.approved
        }
    }
    return jsonify(response), 200

@app.route('/api/register', methods=['POST'])
@cross_origin(supports_credentials=True)
def create_users():
    credentials = request.get_json()
    name = credentials['name']
    email = credentials['email']
    password = credentials['password']
    location = credentials.get('location')
    service = credentials.get('service')
    experience = credentials.get('experience')
    role_name = credentials.get('role', 'customer')  # Default to 'customer'
    
    # Find or create the role
    user_role = Role.query.filter_by(name=role_name).first()
    # print
    if not user_role:
        user_role = Role(name=role_name, description=f"{role_name} role")
        db.session.add(user_role)
        db.session.commit()
    
    # Set approved status based on role
    approved = False if role_name == 'professional' else True
    
    # Hash password before storing it
    # hashed_password = hash_password(password)
    
    # Create the user with hashed password
    app.security.datastore.create_user(
        email=email, password=password, roles=[user_role], approved=approved,
        role_id=user_role.id, user_name=name, location=location, service=service,
        experience=experience
    )
    db.session.commit()
    return jsonify({"message": "User created successfully!"}), 201

# Admin Routes
@app.route('/api/admin')
@auth_required('token')
@roles_required('admin')
def admin_home():
    return jsonify({"message": "Welcome, Admin!", "user_email": current_user.email})

@app.route('/api/admin/users')
@auth_required('token')
@roles_required('admin')
def list_users():
    users = User.query.all()
    return jsonify([{
        "id": u.id, "email": u.email, "roles": [r.name for r in u.roles], "active": u.active
    } for u in users])

@app.route('/api/admin/professionals/<int:user_id>/approve', methods=['PUT'])
@auth_required('token')
@roles_required('admin')
def approve_professional(user_id):
    user = User.query.get_or_404(user_id)
    if 'service_professional' not in [r.name for r in user.roles]:
        return jsonify({"error": "Not a professional"}), 400
    user.approved = True
    db.session.commit()
    return jsonify({"message": f"Professional {user.email} approved"}), 200

# ... (rest of your routes remain unchanged)


# Route to add a new service (Admin only)
# @roles_required('admin')  # Restrict to admin role
@app.route('/api/add/services', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_service():
    try:
        # Get JSON data from request
        data = request.get_json()
        print("&&&&&&&&&", data)
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['name', 'price', 'timeRequired']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Optional fields
        description = data.get('description', '')
        user_id = data.get('user_id', None)  # Optional, links to a professional

        # Validate base_price is a positive number
        try:
            price = float(data['price'])
            if price <= 0:
                return jsonify({'error': 'Base price must be positive'}), 400
        except ValueError:
            return jsonify({'error': 'Base price must be a number'}), 400

        # Create new service
        new_service = Service(
            name=data['name'],
            base_price=price,
            time_required=data['timeRequired'],
            description=description,
            user_id=user_id
        )

        # Add to database
        db.session.add(new_service)
        db.session.commit()

        # Return success response
        return jsonify({
            'message': 'Service added successfully',
            'service': {
                'id': new_service.id,
                'name': new_service.name,
                'base_price': new_service.base_price,
                'time_required': new_service.time_required,
                'description': new_service.description,
                'user_id': new_service.user_id
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Optional: Route to get all services (for testing)
@app.route('/api/get/services', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_services():
    services = Service.query.all()
    return jsonify([{
        'id': service.id,
        'name': service.name,
        'price': service.base_price,
        'timeRequired': service.time_required,
        'description': service.description,
        'user_id': service.user_id
    } for service in services]), 200


@app.route('/api/update/services/<int:service_id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_service(service_id):
    try:
        # Find the service by ID
        service = Service.query.get(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404

        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update fields if provided in the request (optional updates)
        if 'name' in data and data['name']:
            service.name = data['name']
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({'error': 'Base price must be positive'}), 400
                service.base_price = price
            except ValueError:
                return jsonify({'error': 'Base price must be a number'}), 400

        if 'timeRequired' in data and data['timeRequired']:
            service.time_required = data['timeRequired']

        if 'description' in data:
            service.description = data['description']

        if 'user_id' in data:
            service.user_id = data['user_id']  # Allow null or valid user_id

        # Commit changes to the database
        db.session.commit()

        # Return success response
        return jsonify({
            'message': 'Service updated successfully',
            'service': {
                'id': service.id,
                'name': service.name,
                'base_price': service.base_price,
                'time_required': service.time_required,
                'description': service.description,
                'user_id': service.user_id
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        
@app.route('/api/delete/services/<int:service_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete_service(service_id):
    try:
        # Find the service by ID
        service = Service.query.get(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Delete the service from the database
        db.session.delete(service)
        db.session.commit()

        # Return success response
        return jsonify({
            'message': 'Service deleted successfully',
            'service_id': service.id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    
@app.route('/api/get/customers', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_customers():
    userList = User.query.filter_by(role_id=2).all()
    print("918794729479qw7r9qw7er", userList)

    return jsonify([{
        'id': user.id,
        'email': user.email,
        'name': user.user_name,
        'location': user.location,
    } for user in userList]), 200

# @app.route('/api/get/customers', methods=['GET'])
# @cross_origin(supports_credentials=True)
# def get_customers():
#     userList = User.query.filter_by(role_id=2).all()
#     print("918794729479qw7r9qw7er", userList)

#     return jsonify([{
#         'id': user.id,
#         'email': user.email,
#         'name': user.user_name,
#         'location': user.location,
#     } for user in userList]), 200

@app.route('/api/get/professionals', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_professionals():
    userList = User.query.filter_by(role_id=3).all()


    return jsonify([{
        'id': user.id,
        'service': user.service,
        'name': user.user_name,
        'location': user.location,
        'experience': user.experience,
        'approved': user.approved,
        'rating': Review.query.filter_by(service_request_id=ServiceRequest.query.filter_by(professional_id=user.id).first().service_id).first().rating,
        # 'review': user.review
    } for user in userList]), 200

# @app.route('/api/get/services', methods=['GET'])
# @cross_origin(supports_credentials=True)
# def get_services():
#     services = Service.query.all()
#     return jsonify([{
#         'id': service.id,
#         'name': service.name,
#         'price': service.base_price,
#         'timeRequired': service.time_required,
#         'description': service.description,
#         'user_id': service.user_id
#     } for service in services]), 200

@app.route('/api/delete/user/<int:user_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete_user(user_id):
    try:
        # Find the service by ID
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'user not found'}), 404
        
        # Delete the user from the database
        db.session.delete(user)
        db.session.commit()

        # Return success response
        return jsonify({
            'message': 'user deleted successfully',
            'user_id': user_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ... (your existing imports and routes remain unchanged up to /api/delete/user/<int:user_id>) ...

@app.route('/api/update/user/<int:user_id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_user(user_id):
    try:
        # Find the user by ID
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get JSON data from request
        data = request.get_json()
        print("##############", data)
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update fields if provided in the request (optional updates)
        if 'name' in data and data['name']:
            user.user_name = data['name']

        if 'email' in data and data['email']:
            # Check if new email is already taken by another user
            if User.query.filter(User.email == data['email'], User.id != user_id).first():
                return jsonify({'error': 'Email already in use'}), 409
            user.email = data['email']

        if 'password' in data and data['password']:
            user.password = hash_password(data['password'])  # Hash the new password

        if 'location' in data:
            user.location = data['location']  # Allow null or valid string

        if 'service' in data:
            user.service = data['service']  # Allow null or valid string

        if 'experience' in data:
            user.experience = data['experience']  # Allow null or valid string

        if 'approved' in data:
            # Only admins should modify this; additional check if needed
            user.approved = bool(data['approved'])

        if 'role' in data and data['role']:
            # Find or create the new role
            new_role = Role.query.filter_by(name=data['role']).first()
            if not new_role:
                new_role = Role(name=data['role'], description=f"{data['role']} role")
                db.session.add(new_role)
                db.session.commit()
            # Update user's role via Flask-Security datastore
            app.security.datastore.remove_role_from_user(user, [r for r in user.roles][0])  # Remove old role
            app.security.datastore.add_role_to_user(user, new_role)
            # Update role_id if your model uses it
            user.role_id = new_role.id
            # Adjust approved status based on new role
            user.approved = False if data['role'] == 'professional' else True

        # Commit changes to the database
        db.session.commit()

        # Return success response
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.user_name,
                'location': user.location,
                'service': user.service,
                'experience': user.experience,
                'roles': [role.name for role in user.roles],
                'approved': user.approved
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route to add a new service request
@app.route('/api/add/service-request', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_service_request():
    try:
        # Get JSON data from request
        data = request.get_json()
        # print("aldsfjlasjdflkasjflkasjdfklasf",data)
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        # required_fields = ['customerId']
        # for field in required_fields:
        #     if field not in data or not data[field]:
        #         return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if service and customer exist
        # service = Service.query.get(data['serviceId'])
        # if not service:
        #     return jsonify({'error': 'Service not found'}), 404

        # customer = User.query.get(data['customerId'])
        # if not customer:
        #     return jsonify({'error': 'Customer not found'}), 404

        # Optional fields
        professional_id = data.get('professionalId')
        # if professional_id:
        #     professional = User.query.get(professional_id)
        #     if not professional or 'professional' not in [r.name for r in professional.roles]:
        #         return jsonify({'error': 'Invalid or non-professional user specified'}), 400

# {
#     "professionalId": 0,
#     "dateOfRequest": "2025-03-06",
#     "dateOfCompletion": "2025-03-25",
#     "remarks": "adfasdf",
#     "name": "Renee",
#     "location": "chennai",
#     "service": "Plumbling",
#     "customerId": 2,
#     "status": "requested"
# }
        date_of_request = data.get('dateOfRequest', datetime.utcnow())
        date_of_completion = data.get('dateOfCompletion')
        remarks = data.get('remarks', '')
        service = data.get('service', "")
        service_status = data.get('status', 'requested')  # Default to 'requested'

        # Validate date_of_completion if provided
        if date_of_request:
            try:
                date_of_request = datetime.fromisoformat(date_of_request)
            except ValueError:
                return jsonify({'error': 'Invalid date_of_completion format (use ISO format)'}), 400
            
        if date_of_completion:
            try:
                date_of_completion = datetime.fromisoformat(date_of_completion)
            except ValueError:
                return jsonify({'error': 'Invalid date_of_completion format (use ISO format)'}), 400
            
        service = Service.query.filter_by(name=service).first()
        print("aldsfjlasjdflkasjflkasjdfklasf",data)

        # Create new service request
        new_request = ServiceRequest(
            service_id=service.id,
            customer_id=data['customerId'],
            professional_id=professional_id,
            date_of_request=date_of_request,
            date_of_completion=date_of_completion,
            service_status=service_status,
            remarks=remarks
        )

        # Add to database
        db.session.add(new_request)
        db.session.commit()

        # Return success response
        return jsonify({
            'message': 'Service request added successfully',
            'service_request': {
                'id': new_request.id,
                'service_id': new_request.service_id,
                'customer_id': new_request.customer_id,
                'professional_id': new_request.professional_id,
                'date_of_request': new_request.date_of_request.isoformat(),
                'date_of_completion': new_request.date_of_completion.isoformat() if new_request.date_of_completion else None,
                'service_status': new_request.service_status,
                'remarks': new_request.remarks
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route to delete a service request
@app.route('/api/delete/service-request/<int:request_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
@auth_required('token')  # Optional: requires authenticated user
def delete_service_request(request_id):
    try:
        # Find the service request by ID
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404

        # Optionally restrict deletion to admins or the customer who created it
        # Uncomment and adjust based on your needs
        # if 'admin' not in [r.name for r in current_user.roles] and service_request.customer_id != current_user.id:
        #     return jsonify({'error': 'Unauthorized to delete this request'}), 403

        # Delete the service request from the database
        db.session.delete(service_request)
        db.session.commit()

        # Return success response
        return jsonify({
            'message': 'Service request deleted successfully',
            'request_id': request_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/get/service-request', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_service_requests():
    serviceList = ServiceRequest.query.all()
    # service = Service.query.filter_by(id=)

    return jsonify([{
        'id': service.id,
        'service_id': service.service_id,
        'customer_id': service.customer_id,
        'professional_id': service.professional_id,
        'date_of_request': service.date_of_request.isoformat(),
        'date_of_completion': service.date_of_completion.isoformat() if service.date_of_completion else None,
        'service_status': service.service_status,
        'remarks': service.remarks,
        "service": Service.query.filter_by(id=service.service_id).first().name
    } for service in serviceList]), 200

@app.route('/api/get/professional-service-request/<int:id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_professional_service_requests(id):
    serviceList = ServiceRequest.query.filter_by(professional_id=id)
    # review = Review.query.filter_by(service_request_id=)
    # user = User.query.filter_by(id=id).first()


    return jsonify([{
        'id': service.id,
        'service_id': service.service_id,
        'customer_id': service.customer_id,
        'professional_id': service.professional_id,
        'date_of_request': service.date_of_request.isoformat(),
        'date_of_completion': service.date_of_completion.isoformat() if service.date_of_completion else None,
        'service_status': service.service_status,
        'remarks': service.remarks,
        'rating': Review.query.filter_by(service_request_id=service.service_id).first().rating,
        "service": Service.query.filter_by(id=service.service_id).first().name
        # 'name': 
    } for service in serviceList]), 200


@app.route('/api/update/professional-service-request/<int:request_id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_professional_request_service(request_id):
    try:
        # Find the user by ID
        # if not user:
        #     return jsonify({'error': 'User not found'}), 404

        # Get JSON data from request
        data = request.get_json()
        # serviceList = ServiceRequest.query.get(request_id)
        service = ServiceRequest.query.filter_by(id=request_id).first()
        print("*************", service)
        if 'service_status' in data:
            service.service_status = data['service_status']  # Allow null or valid string

        # Commit changes to the database
        db.session.commit()

        # Return success response
        return jsonify({
            'id': service.id,
            'service_id': service.service_id,
            'customer_id': service.customer_id,
            'professional_id': service.professional_id,
            'date_of_request': service.date_of_request.isoformat(),
            'date_of_completion': service.date_of_completion.isoformat() if service.date_of_completion else None,
            'service_status': service.service_status,
            'remarks': service.remarks,
            "service": Service.query.filter_by(id=service.service_id).first().name
            # 'name': 
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/update/service-request/<int:user_id>', methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_service_requests(user_id):

    try:
        # Find the user by ID
        # if not user:
        #     return jsonify({'error': 'User not found'}), 404

        # Get JSON data from request
        data = request.get_json()
        service = ServiceRequest.query.filter_by(id=user_id).first()
        # serviceList = ServiceRequest.query.get(request_id)
        if 'service_status' in data:
            service.service_status = data['service_status']  # Allow null or valid string

        # Commit changes to the database
        db.session.commit()

        # Return success response
        return jsonify({
            'id': service.id,
            'service_id': service.service_id,
            'customer_id': service.customer_id,
            'professional_id': service.professional_id,
            'date_of_request': service.date_of_request.isoformat(),
            'date_of_completion': service.date_of_completion.isoformat() if service.date_of_completion else None,
            'service_status': service.service_status,
            'remarks': service.remarks,
            "service": Service.query.filter_by(id=service.service_id).first().name
            # 'name': 
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/get/reviews', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_review():
    reviews = Review.query.all()
    review_list = [
        {
            "id": review.id,
            "service_request_id": review.service_request_id,
            "rating": review.rating,
            "review_text": review.review_text,
            "date_posted": review.date_posted
        } 
        for review in reviews
    ]
    return jsonify({"reviews": review_list}), 200

@app.route('/api/get/reviews', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_review():
    data = request.get_json()
    service_request_id = data.get('service_request_id')
    rating = data.get('rating')
    review_text = data.get('review_text', '')
    
    if not service_request_id or rating is None:
        return jsonify({"error": "service_request_id and rating are required."}), 400
    
    service_request = ServiceRequest.query.get(service_request_id)
    if not service_request:
        return jsonify({"error": "Invalid service_request_id."}), 404
    
    new_review = Review(
        service_request_id=service_request_id,
        rating=rating,
        review_text=review_text
    )
    db.session.add(new_review)
    db.session.commit()
    
    return jsonify({"message": "Review added successfully!", "review_id": new_review.id}), 201


if __name__ == '__main__':
    app.run(debug=True)