import pytest


def test_get_invalid_phone_key(client):
    response = client.get('/api/phone_key/bad_phone_key')
    assert response.status_code == 404


def test_create_phone_key_with_bad_phone(client):
    response1 = client.post('/api/phone_key/create', json={'phone': 'bad phone'})
    response2 = client.post('/api/phone_key/create', json={'phone': '79508119553'})
    response3 = client.post('/api/phone_key/create', json={'phone': '+79509553'})
    response4 = client.post('/api/phone_key/create', json={'phone': '+89508119553'})

    assert response1.status_code == 422
    assert response2.status_code == 422
    assert response3.status_code == 422
    assert response4.status_code == 422


def test_create_phone_key(client):
    response = client.post('/api/phone_key/create', json={'phone': '+79508119553'})

    assert response.status_code == 201
