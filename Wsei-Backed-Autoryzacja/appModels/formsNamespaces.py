from flask_restx import Api, Namespace

# Tworzenie różnych przestrzeni nazw

rest_api = Api(version="1.0.0", title="Wsei Mikroserwis Logowania API")

login_namespace = Namespace(
    'System Logowania', description='Endpointy związane z kontem')



rest_api.add_namespace(login_namespace, path='/api/users')

  
