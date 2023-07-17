import psycopg2
from flask import Flask, request
from flask_restx import Resource, fields, Api
from connection import conn_to_db
from models import api, course_add_model,course_del_model
from flask_cors import CORS
from courseFunctions import delete_course,add_course
from auth import token_required_with_role
# Connect to the PostgreSQL database


# Create the courses API blueprint
app=Flask(__name__)
api.init_app(app)
CORS(app)

@api.route('/api/delete-course')
class DeleteCourse(Resource):
    @token_required_with_role('Wykladowca')

    @api.expect(course_del_model)
    def post(current_user):
        req_data = request.get_json()
        course_id=req_data.get("id_course")
      

        response = delete_course(course_id)
        if response['success'] == True:
            
            return response, 200
        else:
            return response, 500

       
        
@api.route('/api/add-course')
class CourseAdd(Resource):
    #@token_required_with_role('Wykladowca')
    @api.expect(course_add_model)
    def post(current_user):
        req_data = request.get_json()
        course_name=req_data.get("name")
        course_description=req_data.get("description")
        course_id_user=req_data.get("id_user")
        response = add_course(course_name,course_description,course_id_user)
        if response['success'] == True:
            
            return response, 200
        else:
            return response, 500

if __name__ == '__main__':
    app.run(port=5002)
