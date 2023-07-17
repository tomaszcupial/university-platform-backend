from flask_restx import Api, Namespace

# Tworzenie różnych przestrzeni nazw

rest_api = Api(version="1.0.0", title="Wsei Mikroserwis Obsługa kursów API")




kursy_namespace = Namespace(
    'Obsługa Kursów', description='Endpointy związane z kursami')



rest_api.add_namespace(kursy_namespace)

  
