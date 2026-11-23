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
    assert data["description"] == "Resident needs a cooling space"
    assert data["category"] == "cooling_space"
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
    
def test_create_request_missing_description(client):

    response = client.post(
        "/api/requests/",
        json={
            "category": "cooling_space"
        }
    )

    assert response.status_code == 400
    assert response.is_json


def test_get_all_requests(client):

    client.post(
        "/api/requests/",
        json={
            "description": "Resident needs cooling",
            "category": "cooling_space"
        }
    )

    response = client.get("/api/requests/")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 1
    
def test_get_single_request(client):

    create_response = client.post(
        "/api/requests/",
        json={
            "description": "Resident needs cooling",
            "category": "cooling_space"
        }
    )

    request_id = create_response.get_json()["id"]

    response = client.get(
        f"/api/requests/{request_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == request_id
    

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
            "status": "in_progress",
            "priority" : "high"
        }
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "in_progress"
    assert response.get_json()["priority"] == "high"
    
def test_update_request_invalid_priority(client):

    create_response = client.post(
        "/api/requests/",
        json={
            "description": "Resident needs cooling",
            "category": "cooling_space"
        }
    )

    request_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/requests/{request_id}",
        json={
            "priority": "super_urgent"
        }
    )

    assert response.status_code == 400
    assert response.is_json
    
def test_update_unknown_request(client):

    response = client.patch(
        "/api/requests/999",
        json={
            "status": "completed"
        }
    )

    assert response.status_code == 404
    
def test_delete_request(client):

    create_response = client.post(
        "/api/requests/",
        json={
            "description": "Resident needs cooling",
            "category": "cooling_space"
        }
    )

    request_id = create_response.get_json()["id"]

    response = client.delete(
        f"/api/requests/{request_id}"
    )

    assert response.status_code == 204

    # Verify that the request no longer exists.
    get_response = client.get(
        f"/api/requests/{request_id}"
    )

    assert get_response.status_code == 404

def test_delete_unknown_request(client):

    response = client.delete("/api/requests/999")

    assert response.status_code == 404
    assert response.is_json
    
def test_filter_requests(client):

    client.post(
        "/api/requests/",
        json={
            "description": "Cooling support needed",
            "category": "cooling_space",
            "area": "Bolton"
        }
    )

    client.post(
        "/api/requests/",
        json={
            "description": "Welfare visit needed",
            "category": "welfare_visit",
            "area": "Manchester"
        }
    )

    response = client.get(
        "/api/requests/?category=cooling_space&area_id=1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert all(
        request["category"] == "cooling_space"
        for request in data
    )