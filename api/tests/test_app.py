def test_create_request(client):

    response = client.post(
        "/api/requests/",
        json={
            "description": "Resident needs a cooling space",
            "category": "cooling_space",
            "area": "Bolton"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["status"] == "pending"
    
def test_create_request_invalid_category(client):

    response = client.post(
        "/api/requests/",
        json={
            "description": "Resident needs support",
            "category": "invalid_category"
        }
    )

    assert response.status_code == 400

def test_get_unknown_request(client):

    response = client.get("/api/requests/999")

    assert response.status_code == 404
    
def test_update_request(client):

    create_response = client.post(
        "/api/requests/",
        json={
            "description": "Resident needs support",
            "category": "welfare_visit",
            "area": "Bolton"
        }
    )

    request_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/requests/{request_id}",
        json={
            "status": "in_progress"
        }
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "in_progress"