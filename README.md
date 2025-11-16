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
- A Google Cloud Console -- Project and Client secrets 

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
