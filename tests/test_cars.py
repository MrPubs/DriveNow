
import uuid
import pytest


# ── Helpers ────────────────────────────────────────────────────────────────────
def make_car_payload(**overrides) -> dict:
    """Build a valid Car payload matching the API schema."""
    payload = {
        "id": str(uuid.uuid4()),
        "model": {
            "company": "TestCo",
            "name": "TestCar",
            "year": 2024,
        },
        "status": {
            "status": "available"
        }
    }
    payload.update(overrides)
    return payload


# ── Health ──────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_ping(client):
    resp = await client.get("/health/ping")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "pong"}


# ── POST /v1/cars/ ──────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_add_car_returns_201_with_correct_shape(client):
    payload = make_car_payload()
    resp = await client.post("/v1/cars/", json=payload)

    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == payload["id"]
    assert body["model"]["name"] == "TestCar"
    assert body["model"]["company"] == "TestCo"
    assert body["model"]["year"] == 2024
    assert body["status"]["status"] == "available"


@pytest.mark.asyncio
async def test_add_car_all_valid_statuses(client):
    """Each rental status enum value should be accepted."""
    for status in ["available", "in use", "under maintenance"]:
        payload = make_car_payload(
            id=str(uuid.uuid4()),
            status={"status": status}
        )
        resp = await client.post("/v1/cars/", json=payload)
        assert resp.status_code == 201, f"Failed for status: {status}"
        assert resp.json()["status"]["status"] == status


@pytest.mark.asyncio
async def test_add_car_invalid_status_returns_422(client):
    payload = make_car_payload(status={"status": "broken"})
    resp = await client.post("/v1/cars/", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_add_car_missing_model_returns_422(client):
    payload = {"id": str(uuid.uuid4()), "status": {"status": "available"}}
    resp = await client.post("/v1/cars/", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_add_car_missing_id_returns_422(client):
    payload = {
        "model": {"company": "TestCo", "name": "TestCar", "year": 2024},
        "status": {"status": "available"}
    }
    resp = await client.post("/v1/cars/", json=payload)
    assert resp.status_code == 201


# ── GET /v1/cars/{car_id} ───────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_car_by_id(client):
    payload = make_car_payload()
    await client.post("/v1/cars/", json=payload)

    resp = await client.get(f"/v1/cars/{payload['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == payload["id"]


@pytest.mark.asyncio
async def test_get_car_nonexistent_returns_404(client):
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/v1/cars/{fake_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_car_invalid_uuid_returns_422(client):
    resp = await client.get("/v1/cars/not-a-uuid")
    assert resp.status_code == 422


# ── GET /v1/cars/ ───────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_all_cars_empty_db(client):
    resp = await client.get("/v1/cars/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["length"] == 0
    assert body["cars"] == []


@pytest.mark.asyncio
async def test_get_all_cars_returns_added_car(client):
    payload = make_car_payload()
    await client.post("/v1/cars/", json=payload)

    resp = await client.get("/v1/cars/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["length"] == 1
    assert body["cars"][0]["id"] == payload["id"]


@pytest.mark.asyncio
async def test_get_all_cars_status_filter(client):
    available = make_car_payload(id=str(uuid.uuid4()), status={"status": "available"})
    in_use = make_car_payload(id=str(uuid.uuid4()), status={"status": "in use"})
    await client.post("/v1/cars/", json=available)
    await client.post("/v1/cars/", json=in_use)

    resp = await client.get("/v1/cars/", params={"status_filter": "available"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["filter"] == "available"
    assert all(c["status"]["status"] == "available" for c in body["cars"])


@pytest.mark.asyncio
async def test_get_all_cars_invalid_status_filter_returns_422(client):
    resp = await client.get("/v1/cars/", params={"status_filter": "flying"})
    assert resp.status_code == 422


# ── PATCH /v1/cars/{car_id} ─────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_car_model(client):
    payload = make_car_payload()
    await client.post("/v1/cars/", json=payload)

    update = {"model": {"company": "NewCo", "name": "NewModel", "year": 2025}}
    resp = await client.patch(f"/v1/cars/{payload['id']}", json=update)
    assert resp.status_code == 200
    body = resp.json()
    assert body["model"]["name"] == "NewModel"
    assert body["model"]["company"] == "NewCo"
    assert body["model"]["year"] == 2025


@pytest.mark.asyncio
async def test_update_car_status(client):
    payload = make_car_payload()
    await client.post("/v1/cars/", json=payload)

    update = {"status": {"status": "in use"}}
    resp = await client.patch(f"/v1/cars/{payload['id']}", json=update)
    assert resp.status_code == 200
    assert resp.json()["status"]["status"] == "in use"


@pytest.mark.asyncio
async def test_update_nonexistent_car_returns_404(client):
    update = {"status": {"status": "in use"}}
    resp = await client.patch(f"/v1/cars/{uuid.uuid4()}", json=update)
    assert resp.status_code == 404


# ── DELETE /v1/cars/{car_id} ────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_delete_car(client):
    payload = make_car_payload()
    await client.post("/v1/cars/", json=payload)

    del_resp = await client.delete(f"/v1/cars/{payload['id']}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/v1/cars/{payload['id']}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_car_returns_404(client):
    resp = await client.delete(f"/v1/cars/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_car_invalid_uuid_returns_422(client):
    resp = await client.delete("/v1/cars/not-a-uuid")
    assert resp.status_code == 422