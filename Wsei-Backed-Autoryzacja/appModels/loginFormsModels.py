from flask_restx import fields
from appModels.formsNamespaces import rest_api

login_model = rest_api.model('LoginModel', {"username": fields.String(required=True, min_length=1, max_length=64),
                                            "password": fields.String(required=True, min_length=1, max_length=64)
                                            })
