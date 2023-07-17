from flask_restx import Api, fields
api = Api(version='1.0', title='Course API', description='API for adding, deleting, and retrieving courses')

# Define course model
course_add_model = api.model('Course', {
    'name': fields.String(required=True, description='Course name'),
    'description': fields.String(required=True, description='Course description'),
    'id_user': fields.Integer(required=True, description='User ID')
})

course_del_model = api.model('Course', {
    'id_course': fields.Integer(required=True, description='Course ID')
})