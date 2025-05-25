FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# ⬇️ C’est ici qu’on change le fichier lancé au démarrage
CMD ["python", "dashboard.py"]