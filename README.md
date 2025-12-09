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

### 2. Install docker (optional, if not already installed) - <https://docs.docker.com/engine/install/>

```bash
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)

# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Check docker status
sudo systemctl status docker

# Verify that the installation is successful by running the hello-world image
sudo docker run hello-world
```

### 3. Setting up Environment Variables

Create a `.env` file in the tg_bot directory of the project and add the following variables:

```bash
cd tg_bot/
nano .env
```

File structure as in tg_bot/.env.example

```env
BOT_TOKEN = your_telegram_bot_token
ADMIN_ID = tg_admin_id
MISTRAL_API_KEY = your_mistral_api_key
DB_HOST = your_host
DB_USER = your_user
DB_PASS = your_pass
DB_NAME = your_name
DB_PORT = 5432
```

### 4. Launching the Telegram Bot application

```bash
docker.exe compose -f .\docker-compose.yml up
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
