# tiktok-techjam-be

## Getting Started

### Setting up the project

Clone the project from the repository, then set up a virtual environment (recommended).

```shell
python3 -m venv venv
```

Activate the virtual environment.
For Linux:

```shell
source venv/bin/activate
```

For Windows (PowerShell):

```shell
.\venv\Scripts\Activate.ps1
```

Install the required packages.

```shell
pip install -r requirements.txt
```

### Environment Variables

Copy the `.env.example` file to `.env` and fill in the required environment variables.

### Running the Database

To run the database, use docker compose with the following command.

```shell
docker-compose -f ./build/docker-compose.yml --env-file .env up -d
```

### Running the Application

To run the project, use the following command.

```shell
fastapi dev app/main.py
```

## To-do List

- [x] Create a FastAPI template
- [] Create Database migrations
- [] Create authentication system
- [] Create CI/CD system to server (optional)
