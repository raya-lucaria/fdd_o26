FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN useradd -m app && chown -R app /app

USER app

CMD ["python", "app.py"]
