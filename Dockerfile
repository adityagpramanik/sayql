FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" "sqlalchemy>=2.0.0" "psycopg[binary]>=3.1.0" "pydantic-settings>=2.0.0" "requests>=2.32.0" "pytest>=8.0.0"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
