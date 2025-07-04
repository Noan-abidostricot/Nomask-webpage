# Utiliser une image Python optimisée comme base
FROM python:3.9-bullseye

# Définir des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_ENV=development

# Définir le répertoire de travail
WORKDIR /app

# Combiner les commandes d'installation et nettoyer le cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && curl -sL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Installer et configurer Tailwind CSS
RUN python manage.py tailwind init --no-input
RUN python manage.py tailwind install --no-input
RUN python manage.py tailwind build

# Créer et donner accès à staticfiles et collecter les fichiers statiques
RUN mkdir -p /app/staticfiles \
    && chmod -R 755 /app/staticfiles \
    && python manage.py collectstatic --noinput

# Exposer le port sur lequel l'application Django sera exécutée
EXPOSE 8000

# Utilise une variable d'environnement pour déterminer le mode d'exécution
CMD ["sh", "-c", "if [ \"$DJANGO_ENV\" = \"production\" ]; then gunicorn --bind 0.0.0.0:8000 neuroa_project.wsgi:application; else python manage.py runserver 0.0.0.0:8000; fi"]