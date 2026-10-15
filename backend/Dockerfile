FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home --user-group --uid 10001 app \
    && mkdir /data \
    && chown app:app /data

COPY backend/ ./backend/

USER app
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
