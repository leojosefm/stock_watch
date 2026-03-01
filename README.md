# **Personal Stock Monitor**  <!-- Bold heading of size 1 -->

This project is a simple  application that uses FastAPI for building APIs and PostgreSQL as the database. The application allows users to add data to users, companies, and watchlists tables, and uses Alembic for database migrations. Docker is used to containerize the FastAPI and PostgreSQL services.

## **Features**
- **FastAPI** for building the API endpoints.
- **PostgreSQL** for database management.
- **Docker** for containerized deployment.
- **Alembic** for handling database migrations.
- Automated migrations when the FastAPI container starts.

## **Requirements**
To run this project, you will need:
- Docker installed on your machine.
- Docker Compose installed on your machine.
- Python 3.8+ for local development (optional).
- A GitHub repository for version control (optional).


## **Getting Started**
Follow these steps to set up the project on your local machine:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/leojosefm/stock_watch.git
    cd your-repo
    ```

2. **Build and run the Docker containers:**
    ```bash
    docker-compose up --build
    ```

3. **Test the API:**
    - Open your browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to test the API with the Swagger UI.
    - You can also use tools like `curl` or `Postman` to interact with the API.

4. **Run database migrations:**
    ```bash
    docker-compose exec fastapi alembic upgrade head
    ```

## **Directory Structure**
```text
stock_watch/
├── alembic/                   # Alembic migrations directory
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI main application
│   ├── database.py            # Database connection setup
│   ├── models.py              # SQLAlchemy models
│   ├── routers/
│   │   └── user.py            # User API routes
│   └── crud.py                # Database interaction functions
├── Dockerfile                 # Dockerfile for FastAPI
├── docker-compose.yml          # Docker Compose configuration
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation

## Alembic migration steps after making DB modifictionans
```docker exec -it fastapi_app alembic revision --autogenerate -m "<comment>"
docker exec -it fastapi_app alembic upgrade head
```

## **MWAA**
Setup copied from https://github.com/aws/aws-mwaa-local-runner. This is schedule RSI calculations of the stocks under scope on daily or weekly basis
Steps to get container running
1. ./mwaa-local-env build-image
2. ./mwaa-local-env start

3. If running on windows terminal -- remove windows carriage return characters sed -i -e 's/\r$//' docker/script/bootstrap.sh

-- You need to connect - Postgres container to MWAA network 
```
docker network ls
docker network connect <mwaa_network_name> <postgres_container_name>
```

### Dags
1. load_companies - Reads wikipage , extracts S&P500 and loads to company table in our Postgres database. It uses a "check before insert" pattern to avoid duplicates. Runs daily, though in practice the S&P 500 list changes rarely

2. calculate rsi - It first reads all ticker symbols from the company table, then for each one it downloads the last month of daily price data via yfinance and calculates the RSI (Relative Strength Index) using the standard 14-period rolling average approach. The results — including open, high, low, close, volume, and the calculated RSI value — are written into a price_history table. It deletes existing records for each ticker before reloading, so it's a full refresh per stock each day

3. update watchlist - This is the alerting DAG. It queries a watchlist table where users have set RSI alert thresholds for specific stocks. The SQL finds the earliest date (after the watchlist entry was created) where the stock's RSI dropped to or below the user's threshold, and only for alerts not yet triggered. It then updates those watchlist rows to mark them as triggered, recording the RSI value and date when the threshold was crossed.

 The entries for watchlist table are posted from the Fast API app through Streamlit front end