FROM python:3.14.7-slim-bookworm
WORKDIR /app
COPY requirements.txt .
COPY app.py .
RUN pip install -r requirements.txt
RUN useradd -m appuser
USER appuser
CMD ["python", "app.py"]
