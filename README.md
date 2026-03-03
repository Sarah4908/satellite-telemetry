# Satellite Telemetry Project

This repository contains the pieces that power a simple satellite‑telemetry
demo. At the moment we’re only concerned with the back‑end and the anomaly
scoring service – the React frontend has been removed from the scope of this
readme.

## Components

- **secure_dashboard** – Spring Boot application that exposes a REST API,
  persists telemetry records in PostgreSQL, broadcasts them over WebSocket and
  runs a tiny retrieval‑augmented “RAG” layer to generate human‑readable
  explanations for anomalies.
- **ml‑service** – FastAPI microservice that receives raw telemetry, computes
  delta/rolling‑mean features, scores them with a pre‑trained `IsolationForest`,
  constructs a prediction payload and (optionally) forwards the result back to
  the Spring backend.

Both services are designed to run independently during development or together
inside Docker.

## Running the full stack (Docker)

The `docker-compose.yml` file in the project root defines three containers:

```yaml
services:
  db:      # PostgreSQL database
  backend: # build ./secure_dashboard
  ml-service: # build ./ml-service
  frontend:  # you can ignore this service for now
```

To start everything:

```sh
docker-compose up --build -d
# view combined logs
docker-compose logs -f
```

- **Postgres** listens on `localhost:5432`
- **Backend** listens on `http://localhost:8080`
- **ML service** listens on `http://localhost:8000`

The compose file also configures the backend to use
`jdbc:postgresql://db:5432/telemetry` and injects `OPENAI_API_KEY` into the ML
container for the RAG explanation engine. The frontend service is built but not
required for the core system and can simply be ignored or removed from the
compose file if desired.

Stop the stack with `docker-compose down` (add `-v` to remove the database
volume).

## Running individually

### Backend

```sh
cd secure_dashboard
# compile & test with the Maven wrapper
./mvnw clean install

# run against a local Postgres instance
./mvnw spring-boot:run \
    -Dspring.datasource.url=jdbc:postgresql://localhost:5432/telemetry \
    -Dspring.datasource.username=postgres \
    -Dspring.datasource.password=postgres
```

Unit/integration tests use an in‑memory H2 database; the test configuration is
in `src/test/resources/application.properties`.

### ML service

```sh
cd ml-service
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The service expects a trained pipeline file (`anomaly_pipeline.pkl`) produced by
`train_model.py`. When an anomaly is detected it will call the backend at
`http://backend:8080/api/ml/result`; you can adjust `SPRING_URL` in `app.py`
or run it in Docker for proper DNS resolution.

### Support scripts

- `ml-service/train_model.py` – synthetic data generator and model training;
  writes `anomaly_pipeline.pkl`.
- `ml-service/rag/build_index.py` – builds a FAISS index and document list used
  by `rag_engine.py` for explanation generation.

## How components interact

1. A client POSTs raw telemetry to the ML service (`/predict`).
2. The ML service computes features, scales them, predicts with the
   `IsolationForest` and may generate a RAG explanation via `rag_engine`.
3. The ML service returns the scored payload and, if running in Docker, also
   POSTs it to the backend at `/api/ml/result`.
4. The backend saves the record, broadcasts it to any WebSocket subscribers and
   (if the record is marked anomalous) may call `RagService` to compute an
   explanation.
5. Clients can retrieve stored records via `GET /api/telemetry` and request
   explanations via `POST /api/anomaly/explain`.

---

For now the README focuses on these two services; the React frontend has been
omitted but can be added back later when UI work resumes.
