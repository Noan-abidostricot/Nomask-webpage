# Image Python officielle
FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste du code
COPY . .

# Collecter les fichiers statiques (optionnel pour Django)
RUN python manage.py collectstatic --noinput

# Lancer les migrations (optionnel si tu veux tout auto)
# RUN python manage.py migrate

# Port exposé
EXPOSE 8000

# Commande de démarrage
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
