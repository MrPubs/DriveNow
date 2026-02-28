# DriveNow

> A containerized car rental management API built with FastAPI, SQLAlchemy, and PostgreSQL.

---

## Architecture

```
┌─────────────────────────────┐
│           Client            │
│       HTTP Request          │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       FastAPI Router        │  ── API Layer
│                             │
│  /cars  /rentals  /health   │
│  /metrics                   │
│                             │
│  · Parameter validation     │
│  · Request logging          │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Service Layer         │  ── CarService / RentalService
│                             │
│  · Business logic           │
│  · ORM object transformation│
│  · Structured error handling│
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Database Layer / ORM    │  ── SQLAlchemy AsyncSession
│                             │
│  · Query execution          │
│  · Schema-to-model mapping  │
│  · ORM object resolution    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│         PostgreSQL          │
│                             │
│  · Persistent data storage  │
│  · Constraint enforcement   │
│  · Migrations on startup    │
└─────────────────────────────┘
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/MrPubs/DriveNow.git
cd DriveNow
```

### 2. Build Docker images

```bash
docker compose build
```

### 3. Start containers

```bash
docker compose up -d
```

> Database migrations run automatically on container startup via Alembic. No manual steps required.

### 4. Explore the API

Interactive Swagger UI is available at:

```
http://0.0.0.0:8000/docs
```

### 5. View logs

Application logs are written to the API container at:

```
/containedapp/logs
```

---

## Request Lifecycle

```
Client
  └─▶  FastAPI endpoint receives and validates the request
         └─▶  Service Layer executes business logic
                └─▶  SQLAlchemy ORM queries the database
                └─▶  Service returns a domain object
         └─▶  Pydantic serializes the response
  └─▶  Client receives response
         └─▶  Logs written to console and persistent file
```

---

## Endpoints

| Group       | Path         | Description                  |
|-------------|--------------|------------------------------|
| **Cars**    | `/cars`      | Manage vehicle inventory     |
| **Rentals** | `/rentals`   | Manage rental listings       |
| **Health**  | `/health`    | Application health status    |
| **Metrics** | `/metrics`   | Runtime performance metrics  |

---

## Tech Stack

| Layer        | Technology                     |
|--------------|-------------------------------|
| API          | FastAPI + Uvicorn              |
| ORM          | SQLAlchemy (async)             |
| Migrations   | Alembic                        |
| Database     | PostgreSQL                     |
| Container    | Docker + Docker Compose        |
| Runtime      | Python 3.12                    |