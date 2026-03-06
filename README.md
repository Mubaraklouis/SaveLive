# SaveLife API

Express.js REST API with PostgreSQL, fully Dockerized with Docker Compose.

## Tech Stack

- **Runtime:** Node.js 20 (Alpine)
- **Framework:** Express.js
- **Database:** PostgreSQL 16 (Alpine)
- **Containerization:** Docker + Docker Compose

## Project Structure

```
SaveLife/
├── src/
│   ├── config/
│   │   └── db.js            # Database connection & pool
│   ├── routes/
│   │   ├── health.js        # Health check endpoint
│   │   └── users.js         # CRUD routes for users
│   └── index.js             # App entry point
├── db/
│   └── init.sql             # DB schema & seed data
├── .env                     # Environment variables
├── .env.example             # Env template
├── .dockerignore
├── .gitignore
├── Dockerfile               # App Docker image
├── docker-compose.yml       # Multi-container orchestration
├── package.json
└── README.md
```

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)

### Run the App

```bash
# Clone the repo
git clone https://github.com/Mubaraklouis/SaveLive.git
cd SaveLife

# Start all services (builds app image + pulls postgres)
docker compose up --build
```

The API will be available at **http://localhost:3000**.

### Stop the App

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```

## API Endpoints

| Method | Endpoint         | Description        |
|--------|------------------|--------------------|
| GET    | `/`              | Welcome message    |
| GET    | `/api/health`    | Health check + DB  |
| GET    | `/api/users`     | List all users     |
| GET    | `/api/users/:id` | Get user by ID     |
| POST   | `/api/users`     | Create a user      |
| PUT    | `/api/users/:id` | Update a user      |
| DELETE | `/api/users/:id` | Delete a user      |

### Example: Create a User

```bash
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

## Environment Variables

| Variable      | Default    | Description          |
|---------------|------------|----------------------|
| `PORT`        | `3000`     | App server port      |
| `DB_HOST`     | `db`       | PostgreSQL host      |
| `DB_PORT`     | `5432`     | PostgreSQL port      |
| `DB_USER`     | `postgres` | PostgreSQL user      |
| `DB_PASSWORD` | `postgres` | PostgreSQL password  |
| `DB_NAME`     | `savelife` | PostgreSQL database  |

## Development

For local development without Docker, copy `.env.example` to `.env`, set `DB_HOST=localhost`, install dependencies, and run:

```bash
npm install
npm run dev
```
