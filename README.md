# GoGig

<p align="center">
  <img src="images/logo.png" alt="GoGig Logo"/>
</p>

GoGig is a Discord bot project designed to automate job searching and subreddit/keyword management using Reddit and PostgreSQL. It features modular command handling, database-backed configuration, and supports Docker-based deployment.

## Features
- Discord bot with job search automation
- Subreddit and keyword management (add/list/remove via commands)
- SQLAlchemy ORM models and Alembic migrations
- PostgreSQL database integration
- Docker and Docker Compose support
- Modular command structure (cogs)

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.12+

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gogig.git
   cd gogig
   ```
2. Copy and edit environment variables:
   ```bash
   cp sample.env .env
   # Edit .env as needed
   ```
3. Build and start with Docker Compose:
   ```bash
   docker-compose up --build
   # or
   docker-compose -f default.docker-compose.yml up --build
   ```

### Database Migrations
- Alembic is used for migrations:
  ```bash
  alembic upgrade head
  alembic revision --autogenerate -m "Your migration message"
  ```

## Project Structure
```
GoGig/
├── alembic/           # Alembic migration scripts
├── cogs/              # Discord bot command modules
├── config/            # Configuration and database setup
├── models/            # SQLAlchemy ORM models
├── services/          # Business logic/services
├── main.py            # Bot entry point
├── Dockerfile         # Docker build file
├── default.docker-compose.yml # Docker Compose with PostgreSQL
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## Useful Commands
- Add/list/remove subreddits and keywords via Discord bot commands
- Run linter:
  ```bash
  ./lint.sh
  ```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
