#  Satellite Telemetry Monitoring & Anomaly Detection System

A fully containerized, multi-service telemetry processing platform that ingests satellite data, performs real-time anomaly detection using machine learning, generates contextual explanations, and persists results in a relational database.

Designed to demonstrate microservice architecture, ML integration, distributed systems, and production-style container orchestration.

## System Architecture
```text
Client (React)
        │
        ▼
Spring Boot Backend  ───── PostgreSQL
        │
        ▼
FastAPI ML Service (IsolationForest + RAG Engine)
```



## Services

| Service | Tech | Responsibility |
|---------|------|-----------------|
| **Frontend** | React + Vite | Telemetry submission, anomaly visualization, history display |
| **Backend** | Spring Boot | REST API, persistence, WebSocket broadcast |
| **ML Service** | FastAPI + Scikit-Learn | Feature engineering + anomaly scoring |
| **Database** | PostgreSQL | Persistent telemetry storage |
| **Orchestration** | Docker Compose | Multi-service networking & configuration |

##  Key Features

- **Real-time telemetry ingestion** – Accept and process satellite sensor data instantly
- **IsolationForest-based anomaly detection** – Statistically sound anomaly scoring
- **Feature engineering** – Delta and rolling mean computations
- **Optional RAG-powered explanation generation** – Contextual natural language anomaly analysis
- **REST + WebSocket backend** – Flexible client communication patterns
- **Persistent storage** – PostgreSQL for reliable data retention
- **Fully Dockerized microservice architecture** – Production-ready containerization
- **Environment-based configuration** – Flexible deployment across environments
- **Clean separation of services** – Maintainable, independently deployable components

## Running the Full Stack (Recommended)

From the project root:

```bash
docker compose up --build -d
```

View logs:

```bash
docker compose logs -f
```

### Services & Ports

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8080 |
| ML Service | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

Stop services:

```bash
docker compose down
```

Remove database volume:

```bash
docker compose down -v
```

>  Make sure Docker Desktop is running before executing the commands above.

##  ML Pipeline

The ML service:

- Accepts raw telemetry (/predict)
- Computes engineered features:
  - Temperature delta
  - Voltage delta
  - Rolling mean
- Applies a pre-trained IsolationForest
- Produces:
  - Anomaly score
  - Binary anomaly flag
  - Optional contextual explanation

**Training script:** ml-service/train_model.py

**Generates:** anomaly_pipeline.pkl

*(Note: Model artifacts are excluded from Git.)*

##  Data Flow

1. Client sends telemetry to ML service
2. ML service scores data
3. ML service optionally forwards result to backend
4. Backend stores record in PostgreSQL
5. Backend broadcasts via WebSocket
6. Clients retrieve history via /api/telemetry

## Running Services Individually

### Backend

```bash
cd secure_dashboard
./mvnw clean install
./mvnw spring-boot:run
```




Or with custom database:

```bash
./mvnw spring-boot:run \
    -Dspring.datasource.url=jdbc:postgresql://localhost:5432/telemetry \
    -Dspring.datasource.username=postgres \
    -Dspring.datasource.password=postgres
```

**Tests:** Unit/integration tests use in-memory H2 via `src/test/resources/application.properties`

### ML Service

```bash
cd ml-service
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```




Expects trained pipeline: `anomaly_pipeline.pkl`

Optionally forwards results to backend at `http://backend:8080/api/ml/result` (adjust `SPRING_URL` in `app.py`)

### Support Scripts

- **`ml-service/train_model.py`** – Synthetic data generator & model training → `anomaly_pipeline.pkl`
- **`ml-service/rag/build_index.py`** – Builds FAISS index & document list for explanation generation

## Testing

Backend tests use in-memory H2:

```
src/test/resources/application.properties
```

## Environment Configuration

Environment variables for:

- Database credentials
- Service URLs
- Optional OpenAI API key (RAG)

Frontend configuration via:

- frontend/.env.production
- frontend/.env.development

## Tech Stack

- **Java 17** – Backend runtime
- **Spring Boot 3** – Web framework & DI
- **PostgreSQL** – Relational database
- **FastAPI** – ML service framework
- **Scikit-Learn** – Machine learning
- **React** – Frontend UI
- **Docker Compose** – Container orchestration

## Screenshots
![alt text](images/anomaly.png)
![alt text](images/dashboardui.png)
![alt text](images/telemetryhistory.png)

## Why This Project?

This project demonstrates:

- **Multi-service architecture** – Loosely coupled, independently deployable services
- **Backend + ML integration** – Seamless service-to-service communication
- **Container networking** – Service discovery via Docker DNS
- **Environment-driven configuration** – Flexible, secure credential management
- **Clean production-style structure** – Industry-standard project organization
- **Separation of concerns** – Each service owns its domain
