# Life OS

A private, self-hosted full-stack daily tracker with Body and Mind modules in one application.

## Stack

- React single-page frontend
- FastAPI backend
- PostgreSQL with SQLAlchemy ORM and Alembic migrations
- JWT auth for one private user
- Docker Compose for local development
- GitHub Actions build, test, and EC2 deploy workflow

## Local Setup

1. Copy the environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and replace every `change-this-*` value.

3. Start the stack:

   ```bash
   docker compose up --build
   ```

4. Open the frontend:

   ```text
   http://localhost:8080
   ```

The API is available at `http://localhost:8000`.

## Required Environment Variables

The app expects these values in `.env`:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `CORS_ORIGINS`
- `BACKEND_PORT`
- `FRONTEND_PORT`
- `VITE_API_URL`
- `LIFEOS_USERNAME`
- `LIFEOS_PASSWORD`

`DATABASE_URL` should point at the Compose database when running in Docker:

```text
postgresql+psycopg://life_os:your-password@db:5432/life_os
```

## Migrations

Migrations run automatically when the backend container starts. To run them manually:

```bash
docker compose run --rm backend alembic -c alembic.ini upgrade head
```

To create a new migration after model changes:

```bash
docker compose run --rm backend alembic -c alembic.ini revision --autogenerate -m "describe change"
```

## Create the Single User

After the database is migrated, create or update the private login user:

```bash
docker compose run --rm backend python scripts/create_user.py
```

The script reads `LIFEOS_USERNAME` and `LIFEOS_PASSWORD` from `.env`. If either is missing, it prompts interactively.

## Tests

Run backend tests:

```bash
cd backend
python -m pytest -q
```

Run the frontend build:

```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run build
```

## API

All routes except `POST /auth/login` require a JWT bearer token.

Auth:

- `POST /auth/login`

Capture:

- `GET /captures`
- `POST /captures`
- `PATCH /captures/{id}`
- `POST /captures/{id}/convert`

Body:

- `GET /workouts`
- `POST /workouts`
- `GET /workouts/{id}`
- `POST /workouts/{id}/exercises`
- `GET /workouts/history`
- `GET /golf`
- `POST /golf`
- `GET /metrics`
- `POST /metrics`

Mind:

- `GET /books`
- `POST /books`
- `GET /books/{id}`
- `PATCH /books/{id}`
- `GET /philosophy`
- `POST /philosophy`
- `GET /decisions`
- `POST /decisions`
- `GET /decisions/{id}`
- `PATCH /decisions/{id}`

Book patches only accept `date_finished` and `my_reaction`. Decision patches only accept `actual_outcome` and `reviewed_at`. Philosophy notes are immutable after creation.

## EC2 Deployment

The GitHub Actions workflow has three jobs: `build`, `test`, and `deploy`.

Configure these repository secrets before deploying from `main`:

- `EC2_HOST`
- `EC2_USER`
- `EC2_SSH_KEY`
- `EC2_APP_DIR`
- `PRODUCTION_ENV_FILE`

`PRODUCTION_ENV_FILE` should contain the complete production `.env` contents:

```text
POSTGRES_DB=life_os
POSTGRES_USER=life_os
POSTGRES_PASSWORD=replace-with-a-strong-db-password
POSTGRES_PORT=5432

DATABASE_URL=postgresql+psycopg://life_os:replace-with-a-strong-db-password@db:5432/life_os
SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://your-domain-or-ec2-host

BACKEND_PORT=8000
FRONTEND_PORT=8080
VITE_API_URL=http://your-domain-or-ec2-host:8000

LIFEOS_USERNAME=your-login-username
LIFEOS_PASSWORD=replace-with-a-strong-login-password
```

The deploy job syncs the repository to the EC2 directory, writes `.env`, starts the stack, and creates or updates the single user. Your EC2 instance needs Docker, Docker Compose, SSH access for `EC2_USER`, and permission for that user to run Docker.

The main deployment command is:

```bash
docker compose up -d --build
```
