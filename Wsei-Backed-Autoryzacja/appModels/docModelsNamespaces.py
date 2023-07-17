from flask_restx import fields
from appModels.formsNamespaces import rest_api
FailureModel = rest_api.model('FailureModel', {
    'success': fields.Boolean(description='Status operacji', default=False),
    'msg': fields.String(description='Komunikat błędu')
})

SuccessModel = rest_api.model('SuccessModel', {
    'success': fields.Boolean(description='Status operacji', default=True),
    'msg': fields.String(description='Komunikat')
})


UserTokenModel = rest_api.model('UserTokenModel', {
    'id': fields.Integer(description='ID użytkownika', example=1),
    'username': fields.String(description='Nazwa użytkownika', example="jan.kowalski"),
})

SuccessDataModelUserToken = rest_api.model('UserTokenSuccessDataModel', {
    'success': fields.Boolean(description='Status operacji', default=True),
    'token': fields.String(description='Token użytkownika'),
    'user': fields.Nested(UserTokenModel, description='Informacje o użytkowniku'),
    'permissions': fields.List(fields.String, description='Uprawnienia użytkownika', example=["role1,role2"]),
})
