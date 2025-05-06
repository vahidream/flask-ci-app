FROM python:3.9-slim

# Lazımi sistem paketləri
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# İş qovluğunu təyin et
WORKDIR /app

# requirements.txt faylını kopyala və paketləri qur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bütün faylları konteynerə kopyala
COPY . .

# Upload qovluğunu yarat
RUN mkdir -p /app/static/uploads

# wait-for-it.sh faylını icra ediləbilən et
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Flask 80 portunda işləyəcək
EXPOSE 80

# PostgreSQL servisə qədər gözləyir və sonra Flask-i işə salır
CMD ["/wait-for-it.sh", "db:5432", "--", "python", "app.py"]

