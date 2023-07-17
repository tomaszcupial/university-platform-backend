import requests
import random
import string

#Wymagania przypisanie odpowiednich zmiennych env

def test_login():
    # Test z poprawnymi danymi
    response = requests.post(f"http://localhost:5000/api/users/login",
                             json={"username":  "admin", "password":  "12345"})
    assert response.status_code == 200
    assert response.json()["success"] == True

    # Test z niepoprawnymi danymi
    response = requests.post(f"http://localhost:5000/api/users/login",
                             json={"username": "admin", "password": "zlehaselko"})
    assert response.status_code == 500
    assert response.json()["success"] == False

    # Test z losowymi danymi i złymi polami formularza
    random_username = ''.join(random.choices(
        string.ascii_letters + string.digits, k=10))
    random_password = ''.join(random.choices(
        string.ascii_letters + string.digits, k=10))
    response = requests.post(f"http://localhost:5000/api/users/login",
                             json={"dsadasdasd": random_username, "dasdasds": random_password})
    assert response.status_code == 400
    assert response.json()["success"] == False


def test_get_uzytkownicy(jwt_token):
    response = requests.get(
        f"http://localhost:5000/api/list-users",
        headers={"Authorization": f"{jwt_token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "success" in response.json()
    assert response.json()["success"] == True
    assert "data" in response.json()
    assert isinstance(response.json()["data"], list)
    # Sprawdzenie, czy każdy element na liście użytkowników jest słownikiem
    # zawierającym klucze "id", "username" i "deleted"
    for user in response.json()["data"]:
        assert "id" in user
        assert "username" in user
        assert "deleted" in user