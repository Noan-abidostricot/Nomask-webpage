# Utiliser une image Python optimisée comme base
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_ENV=development

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update --allow-releaseinfo-change --fix-missing && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        gnupg \
        ca-certificates && \
    # Installer Node.js (version 16 LTS) pour Tailwind
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Mettre à jour pip
RUN pip install --upgrade pip

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copier tout le code de l'application
COPY . .

# Installer Tailwind via npm (dans le dossier Tailwind si besoin)
# -- NOTE: Si tu utilises django-tailwind, la commande tailwind doit être disponible,
# mais si erreur persiste, il faut vérifier que l'app Tailwind est bien dans INSTALLED_APPS
RUN npm install -g tailwindcss postcss autoprefixer || true

# Générer les assets Tailwind (assure-toi que l'app Tailwind est bien configurée)
RUN python manage.py tailwind install --no-input || true
RUN python manage.py tailwind build || true

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Exposer le port de l'application
EXPOSE 8000

# Lancer le serveur selon l'environnement
CMD ["sh", "-c", "if [ \"$DJANGO_ENV\" = \"production\" ]; then gunicorn --bind 0.0.0.0:8000 neuroa_project.wsgi:application; else python manage.py runserver 0.0.0.0:8000; fi"]
