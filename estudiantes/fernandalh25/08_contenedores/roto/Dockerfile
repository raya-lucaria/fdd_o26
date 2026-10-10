FROM python:3.14.7-slim-bookworm
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN useradd -m appuser
COPY app.py .
USER appuser
CMD ["python", "app.py"]
