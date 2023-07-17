from flask import Flask, request
from flask_restx import Resource
from flask_cors import CORS
from appModels.formsNamespaces import rest_api,kursy_namespace
from background.tokensAuthentication import token_required_with_role
from background.logsconf import logger
from background.config import BaseConfig
from appModels.coursesFormsModels import add_course_model
from coursesFunctions.getDataFunctions import get_courses
from coursesFunctions.postDataFunctions import sign_to_course
def create_app():

    app = Flask(__name__)
    app.secret_key = BaseConfig.SECRET_KEY
    rest_api.init_app(app)
    CORS(app)
    with app.app_context():
        logger.info("start app")

    return app


app = create_app()

@kursy_namespace.route('/api/courses/sign')
class RejestracjaKurs(Resource):
    @token_required_with_role('Wsei')
    @rest_api.expect(add_course_model, validate=True)
    def post(current_user):
       
        req_data = request.get_json()
        id_course = req_data.get("id_course")
        id_user = req_data.get("id_user")
        if not all([id_course, id_user]):
            return {"success": False, "msg": "Failed to validate required data"}, 422

        response = sign_to_course(id_course, id_user)
        if response['success'] == True:
            logger.info(
                '[%s] -- sign to course success', current_user.username)
            return response, 200
        else:
            logger.info(
                '[%s] -- sign to course failed', current_user.username)
            return response, 500
        


@kursy_namespace.route('/api/courses/list')

class ListaKursow(Resource):
    #@token_required_with_role('Wsei')
    def get(current_user):
      

        response = get_courses()

        if response['success'] == True:

            logger.info(
                '[%s] -- sign to course success', current_user.username)
            return response, 200
        else:
            logger.info(
                '[%s] -- sign to course failed', current_user.username)
            return response, 500


if __name__ == "__main__":
    app.run(port=5001)
