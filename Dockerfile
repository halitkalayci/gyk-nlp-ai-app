# Python 3.10 slim imajını kullan
FROM python:3.10-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem paketlerini güncelle ve gerekli paketleri yükle
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Model dizinini oluştur (eğer yoksa)
RUN mkdir -p model

# Port 8000'i expose et
EXPOSE 8000

# Environment değişkenleri için varsayılan değerler
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV PYTHONUNBUFFERED=1

# Uygulama kullanıcısı oluştur
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check ekle
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Uygulamayı başlat
CMD ["python", "main.py"]
