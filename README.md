# NoMask - Recruitment Platform

This project is the MVP version NoMask recruitment platform, developed with Django (back-end) and Vue.js (front-end), virtualized with venv and uv for dependencies management.

## Prerequisites

- Python
- venv/uv

## SSH authentication with repository (if you're part of the 'institutsolacroup' organization)

1. Generate new Ed25519 key:

ssh-keygen -t ed25519 -C "votre_email@exemple.com"

2. Start SSH authentication service if it isn't yet:

eval `ssh-agent -s`

3. Add this new key to SSH agent:

ssh-add ~/.ssh/id_ed25519

4. Display and copy the public key

cat ~/.ssh/id_ed25519.pub

5. Add it to your codeberg account in your account setting/SSH/GPG Keys section

Click on "Add key" for Manage SSH Keys
Paste the key on the "Content" section

6. Clone the repository:

git clone git@codeberg.org:institutsolacroup/neuroa_mvp.git

## Access token authentication (if you're not part of the 'institutsolacroup' organization)

1. Ask us for an access token

2. Configure the credentials manager to safe store the token

git config --global credential.helper store

3. Use it to clone the repository and start working on it

git clone https://codeberg.org/institutsolacroup/neuroa_mvp.git

## Installation and Setup

1. Browse to the project directory

cd neuroa_mvp

2. Create environment files:

a. If it doesn't exist create a `.env` file at the root of the project with the following variables:

SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=5432
DB_URL=postgres://your_user:your_password@your_host:5432/your_db_name
DJANGO_ENV=development
ALLOWED_HOSTS=.nomask.fr,.nomask.pro,.nomask.eu,localhost,127.0.0.1,web
CSRF_TRUSTED_ORIGINS=https://nomask.fr,https://nomask.pro,https://nomask.eu,http://localhost:8080,http://localhost:8000,http://web:8000
EMAIL_HOST=your_host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_user
EMAIL_HOST_PASSWORD=your_password

b. If it doesn't exist create a `.env` file in the `frontend` directory:

VUE_APP_API_URL=http://localhost:8000

3. Create an `init.sql` file at the root of the project:

CREATE USER your_user WITH PASSWORD 'your_password';
CREATE DATABASE your_db_name;
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_user;

4. For local development install and run uv for dependencies in virtual environment (dependencies edit in "pyproject.toml"):

a. Install:

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

b. Add uv.exe to path then execute the following command to install the dependencies:

uv.exe sync

c. Activate the virtual environment:

.venv\Scripts\activate

d. Lunch the server:

python manage.py runserver 8000

5. Make and apply database migrations:

python manage.py makemigrations
python manage.py migrate

## Usage

- Back-end API: http://localhost:8000
- Admin interface: http://localhost:8000/admin
- Front-end application: http://localhost:8080

## Testing

### Back-end Tests

pytest -s

### Front-end Tests

npm run test:unit

## Project Structure

- `apps/`: Django applications (back-end)
- `neuroa_app`: for candidates
- `neuroa_sol`: for companies
- `frontend/`: Vue.js application (front-end)
- `src/`: Source code
- `components/`: Reusable Vue components
- `views/`: Page components
- `router/`: Vue router configuration
- `store/`: Global application state (Vuex)
- `assets/`: Static resources

## Deployment

Deployment is managed by Forgejo Actions. Each push to the main branch triggers the CI/CD pipeline.

