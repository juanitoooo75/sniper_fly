FROM python:3.10

# Affiche les erreurs en détail
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "sniper_bot.py"]
# Utilise une image officielle Python comme base
FROM python:3.10

# Dossier de travail dans le conteneur
WORKDIR /app

# Copie tout le contenu de ton dossier dans le conteneur
COPY . /app

# Installe les dépendances du fichier requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Commande de démarrage de ton bot
CMD ["python", "sniper_bot.py"]