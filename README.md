# MelodyMate: tg-music-recommendation-system

## Project Description

MelodyMate: Music Recommendation System for ITMO LLM Course. MelodyMate is a music recommendation system developed as a final project for the ITMO Large Language Models course. The project demonstrates the application of modern machine learning techniques and natural language processing to create personalized music recommendations.

## Technology stack

- Python 3.12+
- Aiogram (asynchronous framework for the Telegram Bot API)
- ...

## Installation and configuration

### 1. Cloning a repository

```bash
git clone <URL репозитория>
cd tg-music-recommendation-system
```

### 2. Creating a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # for  Linux/MacOS
# or venv\Scripts\activate  # for Windows
```

### 3. Installing dependencies

```bash
pip install --upgrade pip
# pip install psycopg2-binary
# pip install python-multipart
# sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
pip install -r requirements.txt
```

### 4. Setting up Environment Variables

Create a `.env` file in the root directory of the project and add the following variables:

```env
PG_USER = "postgres"
PG_PASSWORD = 'postgres'
PG_HOST = PG_HOST
PG_PORT = 5432
PG_DATABASE = PG_DATABASE
PG_DEFAULT_DATABASE = 'postgres'
```

### 5. Launching the main Telegram Bot application

```bash
uvicorn app.main:app --port 8080
```

## Project structure

```md
├── app/
│   ├── main.py              # The main application
```

## Code Style & Linting (pre-commit)

We use **[pre-commit](https://pre-commit.com/)** to automatically check and format code on every commit.

### Setup

1. Install pre-commit (preferably in your development environment or virtualenv):

   ```bash
   pip install pre-commit
   ```

2. Install the pre-commit hooks in this repository:

   ```bash
   # This will run automatically on every git commit
   pre-commit install
   ```

### Run manually

   ```bash
   # Run on all files
   pre-commit run --all-files

   # Run only flake8
   pre-commit run flake8 --all-files

   # Run on staged files only
   pre-commit run
   ```
