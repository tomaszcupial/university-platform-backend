from flask_restx import Api, fields

# Create Flask-RestX API
api = Api(version='1.0', title='UserManagement API', description='API for managing users')

# Define user model
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
    'role': fields.String(required=True, description='User role (student/lecturer)')
})
# Define user model
user_model = api.model('Userdelete', {
    'id_user': fields.Integer(required=True, description='Id user'),
})