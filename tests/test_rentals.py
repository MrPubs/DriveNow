import uuid
import pytest
from datetime import datetime, timezone, timedelta


# ── Helpers ────────────────────────────────────────────────────────────────────
def make_car_payload(**overrides) -> dict:
    payload = {
        "id": str(uuid.uuid4()),
        "model": {
            "company": "TestCo",
            "name": "TestCar",
            "year": 2024,
        },
        "status": {"status": "available"}
    }
    payload.update(overrides)
    return payload


def make_rental_payload(car_id: str, **overrides) -> dict:
    now = datetime.now(timezone.utc)
    payload = {
        "id": str(uuid.uuid4()),
        "car_id": car_id,
        "customer_name": "John Doe",
        "start_date": now.isoformat(),
        "end_date": (now + timedelta(days=3)).isoformat(),
    }
    payload.update(overrides)
    return payload


async def create_car(client) -> str:
    """Helper: create a car and return its id."""
    car = make_car_payload()
    resp = await client.post("/v1/cars/", json=car)
    assert resp.status_code == 201
    return car["id"]


# ── POST /v1/rentals/ ───────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_start_rental_returns_201_with_correct_shape(client):
    car_id = await create_car(client)
    payload = make_rental_payload(car_id)

    resp = await client.post("/v1/rentals/", json=payload)
    assert resp.status_code == 201

    body = resp.json()
    assert body["id"] == payload["id"]
    assert body["car_id"] == car_id
    assert body["customer_name"] == "John Doe"
    assert "start_date" in body
    assert "end_date" in body


@pytest.mark.asyncio
async def test_start_rental_nonexistent_car_returns_404(client):
    payload = make_rental_payload(car_id=str(uuid.uuid4()))
    resp = await client.post("/v1/rentals/", json=payload)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_start_rental_end_before_start_returns_422(client):
    car_id = await create_car(client)
    now = datetime.now(timezone.utc)
    payload = make_rental_payload(
        car_id,
        start_date=(now + timedelta(days=3)).isoformat(),
        end_date=now.isoformat(),  # end before start
    )
    resp = await client.post("/v1/rentals/", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_start_rental_end_equals_start_returns_422(client):
    car_id = await create_car(client)
    now = datetime.now(timezone.utc)
    payload = make_rental_payload(
        car_id,
        start_date=now.isoformat(),
        end_date=now.isoformat(),  # same time
    )
    resp = await client.post("/v1/rentals/", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_start_rental_missing_car_id_returns_422(client):
    now = datetime.now(timezone.utc)
    payload = {
        "id": str(uuid.uuid4()),
        "customer_name": "John Doe",
        "start_date": now.isoformat(),
        "end_date": (now + timedelta(days=3)).isoformat(),
    }
    resp = await client.post("/v1/rentals/", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_start_rental_missing_customer_name_returns_422(client):
    car_id = await create_car(client)
    now = datetime.now(timezone.utc)
    payload = {
        "id": str(uuid.uuid4()),
        "car_id": car_id,
        "start_date": now.isoformat(),
        "end_date": (now + timedelta(days=3)).isoformat(),
    }
    resp = await client.post("/v1/rentals/", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_start_rental_invalid_car_id_format_returns_422(client):
    now = datetime.now(timezone.utc)
    payload = {
        "id": str(uuid.uuid4()),
        "car_id": "not-a-uuid",
        "customer_name": "John Doe",
        "start_date": now.isoformat(),
        "end_date": (now + timedelta(days=3)).isoformat(),
    }
    resp = await client.post("/v1/rentals/", json=payload)
    assert resp.status_code == 422


# ── GET /v1/rentals/{rental_id} ────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_rental_by_id(client):
    car_id = await create_car(client)
    payload = make_rental_payload(car_id)
    await client.post("/v1/rentals/", json=payload)

    resp = await client.get(f"/v1/rentals/{payload['id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == payload["id"]
    assert body["car_id"] == car_id
    assert body["customer_name"] == "John Doe"


@pytest.mark.asyncio
async def test_get_rental_nonexistent_returns_404(client):
    resp = await client.get(f"/v1/rentals/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_rental_invalid_uuid_returns_422(client):
    resp = await client.get("/v1/rentals/not-a-uuid")
    assert resp.status_code == 422


# ── GET /v1/rentals/ ───────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_all_rentals_empty_db(client):
    resp = await client.get("/v1/rentals/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["length"] == 0
    assert body["rentals"] == []


@pytest.mark.asyncio
async def test_get_all_rentals_returns_created_rental(client):
    car_id = await create_car(client)
    payload = make_rental_payload(car_id)
    await client.post("/v1/rentals/", json=payload)

    resp = await client.get("/v1/rentals/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["length"] == 1
    assert body["rentals"][0]["id"] == payload["id"]


@pytest.mark.asyncio
async def test_get_all_rentals_multiple(client):
    for _ in range(3):
        car_id = await create_car(client)  # fresh car for each rental
        payload = make_rental_payload(car_id)
        resp = await client.post("/v1/rentals/", json=payload)
        assert resp.status_code == 201

    resp = await client.get("/v1/rentals/")
    assert resp.status_code == 200
    assert resp.json()["length"] == 3


# ── DELETE /v1/rentals/{rental_id} ────────────────────────────────────────────
@pytest.mark.asyncio
async def test_delete_rental(client):
    car_id = await create_car(client)
    payload = make_rental_payload(car_id)
    await client.post("/v1/rentals/", json=payload)

    del_resp = await client.delete(f"/v1/rentals/{payload['id']}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/v1/rentals/{payload['id']}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_rental_returns_404(client):
    resp = await client.delete(f"/v1/rentals/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_rental_invalid_uuid_returns_422(client):
    resp = await client.delete("/v1/rentals/not-a-uuid")
    assert resp.status_code == 422