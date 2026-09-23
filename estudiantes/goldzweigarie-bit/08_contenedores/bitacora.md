# Bitácora unidad 08

## Quién soy
- Nombre: Arié Goldzweig
- GitHub: goldzweigarie-bit
- Docker Hub: goldz177

## Qué corrí
docker version
docker images
docker history goldz177/app-docker:latest

## Tres defectos
1. Imagen base python:latest (>900MB) → cambié a python:3.12-slim
2. pip install sin --no-cache-dir → agregué la bandera
3. Falta USER (corre como root) → agregué useradd y USER appuser

## Lo que se rompió
Usé usuario de GitHub en vez de Docker Hub (error de auth). En Mac ARM64, docker run falló buscando arm64. Solución: tag correcto goldz177 y --platform linux/amd64.
