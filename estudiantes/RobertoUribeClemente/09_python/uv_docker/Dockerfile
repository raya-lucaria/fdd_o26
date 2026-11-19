FROM python:3.13-slim

# uv no viene en la imagen de Python: se copia su binario de la imagen oficial.
COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /usr/local/bin/uv

WORKDIR /app

# Escribe cada instrucción debajo de su hueco. Los comentarios pueden quedarse.
# HUECO 1: copia aquí los dos archivos que describen el ambiente.
COPY pyproject.toml uv.lock ./


# HUECO 2: crea el ambiente desde el lock, y que la construcción falle si el
#          lock ya no coincide con pyproject.toml.
RUN uv sync --locked


# HUECO 3: copia el programa.
COPY reporte.py ./


CMD ["uv", "run", "--no-sync", "reporte.py"]
