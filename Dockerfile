# Utilise une image officielle Python comme base
FROM python:3.10

# Affiche les erreurs immédiatement
ENV PYTHONUNBUFFERED=1

# Dossier de travail dans le conteneur
WORKDIR /app

# Copie tous les fichiers du projet dans /app
COPY . /app

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Démarre l'application Flask
CMD ["python", "dashboard.py"]