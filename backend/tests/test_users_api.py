def test_login_response_200(anon_client):
    payload = {
        "username": "admin",
        "password": "admin"
    }
    response = anon_client.post("/users/login", json=payload)
    assert response.status_code == 200
    # assert "access_token" in response.json()
    # assert "refresh_token" in response.json()

def test_register_response_201(anon_client):
    payload = {
        "username": "sldfjlsdkf",
        "password": "sldfspodfjijosdf",
        "password_confirm": "sldfspodfjijosdf",
    }
    response = anon_client.post("users/register", json=payload)
    assert response.status_code == 201
