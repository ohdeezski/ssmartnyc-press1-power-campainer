# Street Smart NYC Campaign Operations Center (press1)
# Production image: python 3-slim + gunicorn (gevent) for Flask-SocketIO.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=8080

WORKDIR /app

# OS deps: psycopg[binary] wheel, magic, build tooling
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn gevent gevent-websocket

COPY . .

# Non-root runtime user
RUN useradd --create-home -u 1001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Flask-SocketIO requires gevent websocket worker.
CMD ["gunicorn", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", \
     "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "1", \
     "--timeout", "120", "--worker-connections", "1000", "wsgi:app"]