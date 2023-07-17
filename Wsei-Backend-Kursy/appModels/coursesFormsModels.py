from flask_restx import fields
from appModels.formsNamespaces import rest_api

add_course_model = rest_api.model('LoginModel', {"id_course": fields.Integer(required=True, min=1),
                                            "id_user": fields.Integer(required=True, min=1)
                                            })
