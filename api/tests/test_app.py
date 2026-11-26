from app.extensions import db
from app.residents.models import Resident
from app.areas.models import Area

# ==========================================
# CREATE Tests
# ==========================================

def test_create_request(client, app):
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        area = Area(name="Bolton")
        db.session.add_all([resident, area])
        db.session.commit()
        resident_id = resident.id
        area_id = area.id

    response = client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-001",
            "description": "Resident needs a cooling space",
            "category": "cooling_space",
            "resident_id": resident_id,
            "area_id": area_id
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    # assert data["reference"] == "REQ-001"
    assert data["description"] == "Resident needs a cooling space"
    assert data["category"] == "cooling_space"
    assert data["status"] == "pending"
    assert data["resident_id"] == resident_id
    assert data["area_id"] == area_id
    assert data["area_name"] == "Bolton"
    

def test_create_request_invalid_category(client, app):
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        db.session.add(resident)
        db.session.commit()
        resident_id = resident.id

    response = client.post(
        "/api/requests/",
        json={
            "reference": "REQ-002",
            # "description": "Resident needs support",
            "category": "invalid_category",
            "resident_id": resident_id
        }
    )

    assert response.status_code == 400
    

def test_create_request_missing_description(client, app):
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        db.session.add(resident)
        db.session.commit()
        resident_id = resident.id

    response = client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-003",
            "category": "cooling_space",
            "resident_id": resident_id
        }
    )

    assert response.status_code == 400
    assert response.is_json


# ==========================================
# GET Tests
# ==========================================

def test_get_all_requests(client, app):
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        db.session.add(resident)
        db.session.commit()
        resident_id = resident.id

    client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-004",
            "description": "Resident needs cooling",
            "category": "cooling_space",
            "resident_id": resident_id
        }
    )

    response = client.get("/api/requests/")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 1
    

def test_get_single_request(client, app):
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        db.session.add(resident)
        db.session.commit()
        resident_id = resident.id

    create_response = client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-005",
            "description": "Resident needs cooling",
            "category": "cooling_space",
            "resident_id": resident_id
        }
    )
    
    print(create_response)

    request_id = create_response.get_json()["id"]

    response = client.get(
        f"/api/requests/id/{request_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == request_id
    

def test_get_unknown_request(client):
    response = client.get("/api/requests/999")

    assert response.status_code == 404


# ==========================================
# UPDATE Tests
# ==========================================

def test_update_request(client, app):
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        area = Area(name="Bolton")
        db.session.add_all([resident, area])
        db.session.commit()
        resident_id = resident.id
        area_id = area.id

    create_response = client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-006",
            "description": "Resident needs support",
            "category": "welfare_visit",
            "resident_id": resident_id,
            "area_id": area_id
        }
    )

    request_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/requests/id/{request_id}",
        json={
            "status": "in_progress",
            "operational_priority": "high"
        }
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "in_progress"
    assert response.get_json()["operational_priority"] == "high"
    

def test_update_request_invalid_priority(client, app):
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        db.session.add(resident)
        db.session.commit()
        resident_id = resident.id

    create_response = client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-007",
            "description": "Resident needs cooling",
            "category": "cooling_space",
            "resident_id": resident_id
        }
    )

    request_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/requests/id/{request_id}",
        json={
            "operational_priority": "super_urgent"
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


# ==========================================
# DELETE Tests
# ==========================================

def test_delete_request(client, app):
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        db.session.add(resident)
        db.session.commit()
        resident_id = resident.id

    create_response = client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-008",
            "description": "Resident needs cooling",
            "category": "cooling_space",
            "resident_id": resident_id
        }
    )

    request_id = create_response.get_json()["id"]

    response = client.delete(
        f"/api/requests/id/{request_id}"
    )

    assert response.status_code == 204

    # Verify that the request no longer exists.
    get_response = client.get(
        f"/api/requests/{request_id}"
    )

    assert get_response.status_code == 404

def test_delete_unknown_request(client):
    response = client.delete("/api/requests/id/999")

    assert response.status_code == 404
    assert response.is_json


# ==========================================
# FILTER / SEARCH Tests
# ==========================================

def test_filter_requests(client, app):
    with app.app_context():
        resident = Resident(display_name="Test Resident")
        area1 = Area(name="Bolton")
        area2 = Area(name="Manchester")
        db.session.add_all([resident, area1, area2])
        db.session.commit()
        resident_id = resident.id
        area1_id = area1.id
        area2_id = area2.id

    client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-009",
            "description": "Cooling support needed",
            "category": "cooling_space",
            "resident_id": resident_id,
            "area_id": area1_id
        }
    )

    client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-010",
            "description": "Welfare visit needed",
            "category": "welfare_visit",
            "resident_id": resident_id,
            "area_id": area2_id
        }
    )

    response = client.get(
        f"/api/requests/?category=cooling_space&area_id={area1_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    # assert data[0]["reference"] == "REQ-009"
    assert all(
        request["category"] == "cooling_space"
        for request in data
    )

def test_search_requests(client, app):
    with app.app_context():
        resident = Resident(display_name="Jane Doe")
        db.session.add(resident)
        db.session.commit()
        resident_id = resident.id

    client.post(
        "/api/requests/",
        json={
            # "reference": "REQ-011",
            "description": "Needs cooling",
            "category": "cooling_space",
            "resident_id": resident_id
        }
    )

    # Test searching by Resident Name
    response = client.get("/api/requests/?search=Jane")
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["resident_name"] == "Jane Doe"

    # Test searching by Reference
    # response = client.get("/api/requests/?search=REQ-011")
    # assert response.status_code == 200
    # assert len(response.get_json()) == 1